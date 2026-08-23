from __future__ import annotations
from typing import Any
from .engine import Event, DynamicSecurityGraph, PathEvidence, AttackPath

class IsolatedAlertBaseline:
    """
    Event-level scoring only. 
    No graph traversal, no inferred gaps, no temporal path reconstruction.
    """
    def reconstruct(self, graph: DynamicSecurityGraph, seed: str, target: str | None = None) -> list[AttackPath]:
        # Filter high severity events
        high_sev = [e for e in graph.events if e.severity >= 0.7]
        nodes = sorted(list(set(e.source for e in high_sev) | set(e.destination for e in high_sev if e.destination)))
        
        if seed not in nodes:
            nodes.insert(0, seed)
            
        if target and target not in nodes:
            nodes.append(target)
            
        if len(nodes) < 2:
            return []
            
        evidences = []
        for i in range(len(nodes)-1):
            evidences.append(PathEvidence(
                nodes[i], nodes[i+1], "UNKNOWN", [], 0.0, False, False, is_inferred=False, inference_reason="IsolatedAlertBaseline"
            ))
            
        score = min(100.0, len(high_sev) * 10)
        return [AttackPath(nodes, evidences, score, 40.0, ["Reconstructed via isolated alerts"])]


class SlidingWindowBaseline:
    """
    Groups suspicious events in a configurable time window.
    No spatial path reasoning, no dynamic graph reconstruction.
    """
    def __init__(self, window_size: float = 60.0):
        self.window = window_size

    def reconstruct(self, graph: DynamicSecurityGraph, seed: str, target: str | None = None) -> list[AttackPath]:
        events = sorted([e for e in graph.events if e.severity >= 0.5], key=lambda e: e.event_time)
        if not events:
            return []
            
        best_nodes = []
        current_group = []
        
        for e in events:
            if not current_group or (e.event_time - current_group[-1].event_time <= self.window):
                current_group.append(e)
            else:
                current_group = [e]
                
            nodes = []
            for ev in current_group:
                if ev.source not in nodes: nodes.append(ev.source)
                if ev.destination and ev.destination not in nodes: nodes.append(ev.destination)
                
            if len(nodes) > len(best_nodes):
                best_nodes = nodes
                
        if seed not in best_nodes:
            best_nodes.insert(0, seed)
            
        if target and target not in best_nodes:
            best_nodes.append(target)
            
        if len(best_nodes) < 2:
            return []
            
        evidences = [PathEvidence(best_nodes[i], best_nodes[i+1], "UNKNOWN", [], 0.0, False, False) for i in range(len(best_nodes)-1)]
        return [AttackPath(best_nodes, evidences, 75.0, 60.0, ["Reconstructed via sliding window"])]


class StaticGraphBaseline:
    """
    Static graph path search.
    No temporal scoring, no spatial reasoning weights, no inferred gaps.
    """
    def reconstruct(self, graph: DynamicSecurityGraph, seed: str, target: str | None = None) -> list[AttackPath]:
        from collections import deque
        if seed not in graph.nodes:
            return []
            
        q = deque([(seed, [seed])])
        visited = set([seed])
        
        while q:
            node, path = q.popleft()
            if target and node == target:
                evidences = [PathEvidence(path[i], path[i+1], "OBSERVED", [], 0.0, False, False) for i in range(len(path)-1)]
                return [AttackPath(path, evidences, 80.0, 70.0, ["Reconstructed via static BFS"])]
                
            for nxt in graph.edges.get(node, {}):
                if nxt not in visited:
                    visited.add(nxt)
                    q.append((nxt, path + [nxt]))
                    
        return []
