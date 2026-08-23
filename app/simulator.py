from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import random
from .engine import Event, DynamicSecurityGraph, EventProcessor

@dataclass
class SimConfig:
    floors: int = 5
    devices_per_floor: int = 8
    seed: int = 7

@dataclass
class ScenarioData:
    name: str
    events: list[Event]
    ground_truth: dict[str, Any]


class BuildingSimulator:
    def __init__(self, config: SimConfig | None = None):
        self.config = config or SimConfig()
        self.rng = random.Random(self.config.seed)
        self.graph = DynamicSecurityGraph()
        self.base_time = 1_700_000_000.0
        self.devices: list[str] = []
        self.networks: list[str] = []
        self._build()

    def _build(self):
        for floor in range(1, self.config.floors + 1):
            network = f"N-{floor:02d}"
            self.networks.append(network)
            self.graph.upsert_node(network, "NETWORK", floor=floor, network_segment=network)
            for idx in range(self.config.devices_per_floor):
                did = f"D-{(floor-1)*self.config.devices_per_floor + idx + 1:03d}"
                self.devices.append(did)
                self.graph.upsert_node(did, "DEVICE", floor=floor, network_segment=network, criticality=1 if idx < 6 else 2)
                self.graph.connect(did, network, "MEMBER_OF", self._event(f"topo-{did}", "SYSTEM_HEARTBEAT", self.base_time, did, network, floor=floor, severity=.1), .1)

        self.graph.upsert_node("S-02", "SERVER", floor=3, network_segment="N-03", criticality=5)
        self.graph.upsert_node("D-999", "ASSET", floor=5, network_segment="N-05", criticality=10)

    def _event(self, eid, et, t, src, dst=None, floor=None, severity=.1, user_id=None, network=None, meta=None):
        return Event(eid, et, t, t, src, dst, user_id=user_id, device_id=src if src.startswith("D-") else None,
                     network_segment=network, floor=floor, severity=severity, metadata=meta or {})

    def normal_events(self, count=100) -> list[Event]:
        events=[]
        for i in range(count):
            did = self.rng.choice(self.devices)
            floor = self.graph.nodes[did].attrs["floor"]
            net = self.graph.nodes[did].attrs["network_segment"]
            t = self.base_time + i*0.7
            events.append(self._event(f"e-{i}", "DEVICE_TELEMETRY", t, did, did, floor=floor, network=net, severity=.05))
            if i % 3 == 0:
                # Sparse traffic: mostly talk to servers or self-floor, not a complete random graph
                target_options = ["S-02", "D-999"]
                if self.rng.random() < 0.2:
                    same_floor = [d for d in self.devices if self.graph.nodes[d].attrs["floor"] == floor]
                    target_options.extend(same_floor)
                    
                other = self.rng.choice(target_options)
                of = self.graph.nodes[other].attrs["floor"]
                on = self.graph.nodes[other].attrs["network_segment"]
                events.append(self._event(f"n-{i}", "NETWORK_CONNECTION", t+.2, did, other, floor=of, network=on, severity=.2))
        return events

    def generate_scenario(self, name: str, is_benign: bool = False, multi_path: bool = False) -> ScenarioData:
        t = self.base_time + 500
        events = []
        gt = {
            "seed": "D-007",
            "target": "D-999",
            "expected_nodes": ["D-007", "S-02", "D-021", "D-999"],
            "expected_edges": ["D-007->S-02", "S-02->D-021", "D-021->D-999"],
            "event_ids": ["a1", "a2", "a3", "a4", "a5"],
            "timestamps": [t, t+18, t+35, t+48, t+60]
        }
        
        if is_benign:
            gt["target"] = "None"
            gt["expected_nodes"] = []
            events = [
                self._event("b1","AUTHENTICATION",t,"USER-BOB","D-010",floor=2,severity=.3,user_id="USER-BOB",network="N-02"),
                self._event("b2","NETWORK_CONNECTION",t+20,"D-010","D-012",floor=2,severity=.4,network="N-02"),
            ]
        else:
            events = [
                self._event("a1","AUTHENTICATION",t,"USER-ALICE","D-007",floor=1,severity=.4,user_id="USER-ALICE",network="N-01"),
                self._event("a2","NETWORK_CONNECTION",t+18,"D-007","S-02",floor=3,severity=.8,network="N-03"),
                self._event("a3","NETWORK_CONNECTION",t+35,"S-02","D-021",floor=3,severity=.9,network="N-03"),
                self._event("a4","LOCATION_CHANGE",t+48,"D-021","D-021",floor=5,severity=.7,network="N-05"),
                self._event("a5","RESOURCE_ACCESS",t+60,"D-021","D-999",floor=5,severity=1.0,network="N-05"),
            ]
            
        if multi_path and not is_benign:
            gt["expected_nodes"].append("D-014")
            events.extend([
                self._event("m1","NETWORK_CONNECTION",t+15,"D-007","D-014",floor=2,severity=.6,network="N-02"),
                self._event("m2","NETWORK_CONNECTION",t+40,"D-014","D-999",floor=5,severity=.8,network="N-05"),
            ])
            
        # Background noise
        events.extend(self.normal_events(140))
        self.rng.shuffle(events)
        
        return ScenarioData(name, events, gt)

    def perturb_stream(self, data: ScenarioData, missing=0.0, delayed=0.0, duplicate=0.0, floor_loss=None) -> list[Event]:
        events = []
        for e in data.events:
            # Correlated loss: entire floor telemetry drops
            if floor_loss is not None and e.floor == floor_loss:
                continue
            
            # Random loss
            if self.rng.random() < missing:
                continue
                
            # Jitter
            ingest = e.ingest_time + (self.rng.random() * delayed if delayed else 0)
            
            new_e = Event(e.event_id, e.event_type, e.event_time, ingest, e.source, e.destination, 
                          e.user_id, e.device_id, e.network_segment, e.floor, e.severity, e.metadata)
            events.append(new_e)
            
            # Duplicates
            if duplicate and self.rng.random() < duplicate:
                events.append(new_e)
                
        self.rng.shuffle(events)
        return events


def process_events(events, reorder_window=8.0):
    processor=EventProcessor(reorder_window=reorder_window)
    ready=processor.ingest(events)
    ready.extend(processor.flush())
    ready.sort(key=lambda e:e.event_time)
    return ready, processor

# Legacy wrapper for UI compatibility
def get_legacy_sim():
    s = BuildingSimulator()
    s.attack_scenario = lambda: s.generate_scenario("legacy").events[:5]
    s.mixed_scenario = lambda m, d, dup: s.perturb_stream(s.generate_scenario("legacy"), m, d, dup)
    return s
