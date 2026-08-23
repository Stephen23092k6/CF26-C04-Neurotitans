
from __future__ import annotations
from dataclasses import dataclass
import random
from .engine import Event, DynamicSecurityGraph, EventProcessor


@dataclass
class SimConfig:
    floors: int = 5
    devices_per_floor: int = 8
    seed: int = 7


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
                other = self.rng.choice(self.devices)
                of = self.graph.nodes[other].attrs["floor"]
                on = self.graph.nodes[other].attrs["network_segment"]
                events.append(self._event(f"n-{i}", "NETWORK_CONNECTION", t+.2, did, other, floor=of, network=on, severity=.2))
        return events

    def attack_scenario(self) -> list[Event]:
        t=self.base_time+500
        return [
            self._event("a1","AUTHENTICATION",t,"USER-ALICE","D-007",floor=1,severity=.4,user_id="USER-ALICE",network="N-01"),
            self._event("a2","NETWORK_CONNECTION",t+18,"D-007","S-02",floor=3,severity=.8,network="N-03"),
            self._event("a3","NETWORK_CONNECTION",t+35,"S-02","D-021",floor=3,severity=.9,network="N-03"),
            self._event("a4","LOCATION_CHANGE",t+48,"D-021","D-021",floor=5,severity=.7,network="N-05"),
            self._event("a5","RESOURCE_ACCESS",t+60,"D-021","D-999",floor=5,severity=1.0,network="N-05"),
        ]

    def mixed_scenario(self, missing=0.0, delayed=0.0, duplicate=0.0) -> list[Event]:
        events = self.normal_events(140) + self.attack_scenario()
        # Missing telemetry
        if missing:
            keep=[]
            for e in events:
                if self.rng.random() >= missing:
                    keep.append(e)
            events=keep
        # Delay / reorder simulation by perturbing ingest time and ordering
        out=[]
        for e in events:
            ingest=e.ingest_time + (self.rng.random()*delayed if delayed else 0)
            out.append(Event(e.event_id,e.event_type,e.event_time,ingest,e.source,e.destination,e.user_id,e.device_id,e.network_segment,e.floor,e.severity,e.metadata))
            if duplicate and self.rng.random()<duplicate:
                out.append(out[-1])
        self.rng.shuffle(out)
        return out


def process_events(events, reorder_window=8.0):
    processor=EventProcessor(reorder_window=reorder_window)
    ready=processor.ingest(events)
    ready.extend(processor.flush())
    ready.sort(key=lambda e:e.event_time)
    return ready, processor
