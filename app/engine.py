from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict, deque
from typing import Any, Iterable, Optional
import hashlib
import math


@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: str
    event_time: float
    ingest_time: float
    source: str
    destination: Optional[str] = None
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    network_segment: Optional[str] = None
    floor: Optional[int] = None
    severity: float = 0.1
    metadata: dict[str, Any] = field(default_factory=dict)

    def fingerprint(self) -> str:
        raw = f"{self.event_type}|{self.event_time:.3f}|{self.source}|{self.destination}|{self.user_id}|{self.device_id}|{self.network_segment}|{self.floor}"
        return hashlib.sha256(raw.encode()).hexdigest()


@dataclass
class Entity:
    entity_id: str
    entity_type: str
    attrs: dict[str, Any] = field(default_factory=dict)


class DynamicSecurityGraph:
    """Small dependency-free graph layer for the prototype."""

    def __init__(self) -> None:
        self.nodes: dict[str, Entity] = {}
        self.edges: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        self.events: list[Event] = []
        self.events_by_node: dict[str, list[Event]] = defaultdict(list)

    def upsert_node(self, entity_id: str, entity_type: str, **attrs: Any) -> None:
        if entity_id not in self.nodes:
            self.nodes[entity_id] = Entity(entity_id, entity_type, dict(attrs))
        else:
            if self.nodes[entity_id].entity_type == "UNKNOWN" and entity_type != "UNKNOWN":
                self.nodes[entity_id].entity_type = entity_type
            self.nodes[entity_id].attrs.update(attrs)

    def connect(self, a: str, b: str, relation: str, event: Event, weight: float = 1.0) -> None:
        self.edges[a][b] = {
            "relation": relation,
            "first_seen": min(event.event_time, self.edges[a].get(b, {}).get("first_seen", event.event_time)),
            "last_seen": max(event.event_time, self.edges[a].get(b, {}).get("last_seen", event.event_time)),
            "weight": max(weight, self.edges[a].get(b, {}).get("weight", weight)),
            "supporting_events": sorted(set(self.edges[a].get(b, {}).get("supporting_events", []) + [event.event_id])),
        }

    def neighbors(self, node_id: str) -> list[str]:
        return list(self.edges.get(node_id, {}).keys())

    def apply(self, event: Event) -> None:
        self.events.append(event)
        if event.source:
            self.upsert_node(event.source, "UNKNOWN")
            self.events_by_node[event.source].append(event)
        if event.destination:
            self.upsert_node(event.destination, "UNKNOWN")
            if event.destination != event.source:
                self.events_by_node[event.destination].append(event)

        relation = {
            "AUTHENTICATION": "AUTHENTICATED_TO",
            "NETWORK_CONNECTION": "CONNECTED_TO",
            "RESOURCE_ACCESS": "ACCESSED",
            "LOCATION_CHANGE": "LOCATED_AT",
            "PRIVILEGE_CHANGE": "ESCALATED_TO",
            "DEVICE_TELEMETRY": "OBSERVED",
            "POLICY_EVENT": "POLICY_CHECK",
            "SYSTEM_HEARTBEAT": "HEARTBEAT",
        }.get(event.event_type, "OBSERVED")

        if event.destination:
            self.connect(event.source, event.destination, relation, event, weight=max(0.1, event.severity))

    def export(self) -> dict[str, Any]:
        return {
            "nodes": [vars(n) for n in self.nodes.values()],
            "edges": [
                {"source": a, "target": b, **attrs}
                for a, nbrs in self.edges.items()
                for b, attrs in nbrs.items()
            ],
            "event_count": len(self.events),
        }


class EventProcessor:
    """Deduplicates events and reconstructs bounded event order."""

    def __init__(self, reorder_window: float = 8.0) -> None:
        self.reorder_window = reorder_window
        self.seen_ids: set[str] = set()
        self.seen_fingerprints: set[str] = set()
        self.buffer: list[Event] = []
        self.max_event_time = -math.inf
        self.dropped_duplicates = 0
        self.late_events = 0

    def ingest(self, events: Iterable[Event]) -> list[Event]:
        accepted: list[Event] = []
        for event in events:
            fp = event.fingerprint()
            if event.event_id in self.seen_ids or fp in self.seen_fingerprints:
                self.dropped_duplicates += 1
                continue
            self.seen_ids.add(event.event_id)
            self.seen_fingerprints.add(fp)
            self.buffer.append(event)
            self.max_event_time = max(self.max_event_time, event.event_time)

        cutoff = self.max_event_time - self.reorder_window
        ready = [e for e in self.buffer if e.event_time <= cutoff]
        self.buffer = [e for e in self.buffer if e.event_time > cutoff]
        ready.sort(key=lambda e: e.event_time)

        if ready:
            self.late_events += sum(
                1 for e in ready
                if e.ingest_time - e.event_time > self.reorder_window
            )
        accepted.extend(ready)
        return accepted

    def flush(self) -> list[Event]:
        self.buffer.sort(key=lambda e: e.event_time)
        out = self.buffer
        self.buffer = []
        return out


@dataclass
class PathEvidence:
    source: str
    target: str
    relation: str
    supporting_events: list[str]
    temporal_gap: float
    network_transition: bool
    spatial_transition: bool
    is_inferred: bool = False
    inference_reason: str = ""


@dataclass
class AttackPath:
    nodes: list[str]
    edges: list[PathEvidence]
    score: float
    confidence: float
    explanation: list[str]


def _floor_of(graph: DynamicSecurityGraph, node: str) -> Optional[int]:
    entity = graph.nodes.get(node)
    if not entity:
        return None
    return entity.attrs.get("floor")


def _network_of(graph: DynamicSecurityGraph, node: str) -> Optional[str]:
    entity = graph.nodes.get(node)
    if not entity:
        return None
    return entity.attrs.get("network_segment")


class AttackReconstructor:
    def __init__(self, time_window: float = 120.0, max_depth: int = 6, 
                 max_inferred_gaps: int = 2, min_plausibility: float = 65.0,
                 weights: dict[str, float] = None) -> None:
        self.time_window = time_window
        self.max_depth = max_depth
        self.max_inferred_gaps = max_inferred_gaps
        # Minimum plausibility score required to bridge an INFERRED_GAP (suggested: 60-65)
        self.min_plausibility = min_plausibility
        self.weights = weights or {
            "temporal": 30.0,
            "network": 25.0,
            "spatial": 15.0,
            "topology": 20.0,
            "high_value": 10.0,
            "contradictory": -40.0
        }

    def _edge_score(self, graph: DynamicSecurityGraph, a: str, b: str, meta: dict[str, Any]) -> tuple[float, bool, bool]:
        af, bf = _floor_of(graph, a), _floor_of(graph, b)
        an, bn = _network_of(graph, a), _network_of(graph, b)
        spatial = af is not None and bf is not None and af != bf
        net = an is not None and bn is not None and an != bn
        score = float(meta.get("weight", 1.0)) * 20
        if net:
            score += 18
        if spatial:
            score += 12
        return score, net, spatial

    def reconstruct(self, graph: DynamicSecurityGraph, seed: str, target: str | None = None) -> list[AttackPath]:
        if seed not in graph.nodes:
            return []
        paths: list[AttackPath] = []
        q: deque[tuple[str, list[str], list[PathEvidence], float, int]] = deque([(seed, [seed], [], 0.0, 0)])

        while q:
            node, nodes, evidences, raw, gap_count = q.popleft()
            
            if len(nodes) > self.max_depth:
                continue

            if len(nodes) > 1:
                paths.append(self._finalize(graph, nodes, evidences, raw))
            
            if target and node == target:
                continue

            explicit_neighbors = set(graph.edges.get(node, {}).keys())
            prev_time = 0.0
            if evidences:
                prior_evs = evidences[-1].supporting_events
                for ev in graph.events_by_node.get(node, []):
                    if ev.event_id in prior_evs:
                        prev_time = max(prev_time, ev.event_time)
            else:
                seed_times = [ev.event_time for ev in graph.events_by_node.get(node, [])]
                if seed_times:
                    prev_time = min(seed_times)

            enqueued_explicit = set()
            for nxt, meta in graph.edges.get(node, {}).items():
                if nxt in nodes:
                    continue
                score, net, spatial = self._edge_score(graph, node, nxt, meta)
                
                curr_times = [ev.event_time for ev in graph.events_by_node.get(nxt, []) if ev.event_id in meta.get("supporting_events", [])]
                curr_time = max(curr_times) if curr_times else prev_time
                gap = max(0.0, curr_time - prev_time)
                
                if evidences and gap > self.time_window:
                    continue
                    
                evidence = PathEvidence(
                    node, nxt, meta["relation"], list(meta.get("supporting_events", [])), 
                    gap, net, spatial, is_inferred=False
                )
                q.append((nxt, nodes + [nxt], evidences + [evidence], raw + score, gap_count))
                enqueued_explicit.add(nxt)

            if gap_count >= self.max_inferred_gaps:
                continue
                
            for nxt in graph.nodes:
                if nxt in nodes or nxt in enqueued_explicit:
                    continue
                    
                # Requirement: Inferred gap must still require meaningful positive evidence (severity >= 0.5)
                nxt_events = [ev for ev in graph.events_by_node.get(nxt, []) 
                              if ev.event_time >= prev_time and ev.severity >= 0.5]
                
                if not nxt_events:
                    continue
                    
                nxt_time = min([ev.event_time for ev in nxt_events])
                gap = nxt_time - prev_time
                
                plausibility = 0.0
                reasons = []
                
                if 0 <= gap <= self.time_window:
                    plausibility += self.weights["temporal"]
                    reasons.append(f"temporal(+{self.weights['temporal']})")
                else:
                    # Absolute constraint: temporal proximity is required to even consider hopping
                    continue
                    
                af, bf = _floor_of(graph, node), _floor_of(graph, nxt)
                an, bn = _network_of(graph, node), _network_of(graph, nxt)
                
                if an is not None and bn is not None and an == bn:
                    plausibility += self.weights["network"]
                    reasons.append(f"network(+{self.weights['network']})")
                    
                if af is not None and bf is not None and af == bf:
                    plausibility += self.weights["spatial"]
                    reasons.append(f"spatial(+{self.weights['spatial']})")
                    
                if nxt in explicit_neighbors:
                    plausibility += self.weights["topology"]
                    reasons.append(f"topology(+{self.weights['topology']})")
                    
                nxt_type = graph.nodes[nxt].entity_type
                if nxt_type in ("SERVER", "ASSET"):
                    plausibility += self.weights["high_value"]
                    reasons.append(f"high_value(+{self.weights['high_value']})")
                    
                contradictory_types = {"DEVICE_OFFLINE", "ACCOUNT_LOCKED", "POLICY_DENY", "NETWORK_ISOLATED", "AUTHENTICATION_FAILED"}
                contradictory_evs = [ev for ev in graph.events_by_node.get(nxt, []) if ev.event_time >= prev_time and ev.event_type in contradictory_types]
                
                if contradictory_evs:
                    plausibility += self.weights["contradictory"]
                    reasons.append(f"contradictory({self.weights['contradictory']})")

                if plausibility < self.min_plausibility:
                    continue
                
                reason_str = " | ".join(reasons) + f" | final_plausibility={plausibility}"
                spatial_transition = (af is not None and bf is not None and af != bf)
                network_transition = (an is not None and bn is not None and an != bn)
                
                evidence = PathEvidence(
                    node, nxt, "INFERRED_GAP", [], gap, network_transition, spatial_transition, 
                    is_inferred=True, inference_reason=reason_str
                )
                q.append((nxt, nodes + [nxt], evidences + [evidence], raw - 5.0, gap_count + 1))

        uniq: dict[tuple[str, ...], AttackPath] = {}
        for p in paths:
            if target and p.nodes[-1] == target:
                p.score += 50.0
                p.confidence += 15.0
            
            uniq[tuple(p.nodes)] = p
            
        return sorted(uniq.values(), key=lambda p: (p.score, p.confidence), reverse=True)

    def _finalize(self, graph: DynamicSecurityGraph, nodes: list[str], evidences: list[PathEvidence], raw: float) -> AttackPath:
        spatial_count = sum(1 for e in evidences if e.spatial_transition)
        net_count = sum(1 for e in evidences if e.network_transition)
        gap_count = sum(1 for e in evidences if e.is_inferred)
        obs_count = len(evidences) - gap_count
        
        temporal_quality = sum(max(0.0, 1.0 - min(e.temporal_gap / self.time_window, 1.0)) for e in evidences) / max(1, len(evidences))
        
        score = raw + spatial_count * 5 + net_count * 8 + temporal_quality * 20
        confidence = 35 + 8 * obs_count + spatial_count * 5 + net_count * 8 + temporal_quality * 20
        
        score -= gap_count * 5
        confidence -= gap_count * 30
        
        score = min(100.0, max(0.0, score))
        confidence = min(99.0, max(0.0, confidence))

        explanation = [
            f"Path consists of {obs_count} observed transition(s) and {gap_count} inferred gap(s).",
        ]
        
        for i, ev in enumerate(evidences):
            if ev.is_inferred:
                explanation.append(f"Hop {i+1} ({ev.source} \u2192 {ev.target}) INFERRED_GAP: {ev.inference_reason}")
                
        if gap_count > 0:
            explanation.append(f"Confidence reduced by {gap_count * 30} due to missing telemetry.")
            
        if net_count > 0:
            explanation.append(f"{net_count} network-boundary transition(s) contribute to threat score.")
        if spatial_count > 0:
            explanation.append(f"{spatial_count} physical-location transition(s) contribute additional context.")
            
        explanation.append(f"Temporal consistency score: {temporal_quality:.2f}.")
        explanation.append("Result is a candidate reconstruction with evidence-backed confidence, not proof of malicious intent.")
        
        return AttackPath(nodes, evidences, round(score, 2), round(confidence, 2), explanation)
