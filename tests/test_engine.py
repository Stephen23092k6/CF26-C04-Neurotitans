import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.engine import Event, EventProcessor, DynamicSecurityGraph, AttackReconstructor


def test_target_alone_insufficient():
    # Target alone cannot create an inferred edge (without meeting min plausibility)
    g = DynamicSecurityGraph()
    evs = [
        Event("a", "AUTHENTICATION", 1, 1, "D1", "S1", device_id="D1", floor=1, network_segment="N1", severity=.5),
        # D9 is the target, has high severity, but shares nothing else (no topology, no network, no floor)
        # Score = temporal(30) + high_value(0) = 30 < 65
        Event("b", "RESOURCE_ACCESS", 3, 3, "D9", "D9", floor=9, network_segment="N9", severity=.9),
    ]
    for n, typ, floor, net in [("D1", "DEVICE", 1, "N1"), ("S1", "SERVER", 3, "N3"), ("D9", "DEVICE", 9, "N9")]:
        g.upsert_node(n, typ, floor=floor, network_segment=net)
    for e in evs: g.apply(e)
    
    paths = AttackReconstructor(min_plausibility=65.0).reconstruct(g, "D1", "D9")
    # Path from D1 to D9 should fail because 30 < 65
    for p in paths:
        assert "D9" not in p.nodes


def test_same_floor_alone_insufficient():
    # temporal (30) + spatial (15) = 45 < 65
    g = DynamicSecurityGraph()
    evs = [
        Event("a", "AUTHENTICATION", 1, 1, "D1", "S1", device_id="D1", floor=1, network_segment="N1", severity=.5),
        Event("b", "RESOURCE_ACCESS", 3, 3, "D2", "D2", floor=3, network_segment="N4", severity=.9),
    ]
    # S1 and D2 on floor 3, but different networks, not target, not server/asset, no topology.
    for n, typ, floor, net in [("D1", "DEVICE", 1, "N1"), ("S1", "DEVICE", 3, "N3"), ("D2", "DEVICE", 3, "N4")]:
        g.upsert_node(n, typ, floor=floor, network_segment=net)
    for e in evs: g.apply(e)
    
    paths = AttackReconstructor(min_plausibility=65.0).reconstruct(g, "D1")
    for p in paths:
        assert "D2" not in p.nodes


def test_same_network_alone_insufficient_with_contradictory():
    # temporal (30) + network (25) = 55. Without contradictory, it's 55 < 65 so it fails anyway.
    # If it was target (0) it fails. Wait, let's make it temporal (30) + network (25) + spatial (15) = 70 (Plausible)
    # Then add contradictory (-40) -> 30 < 65 (Implausible)
    g = DynamicSecurityGraph()
    evs = [
        Event("a", "AUTHENTICATION", 1, 1, "D1", "S1", device_id="D1", floor=1, network_segment="N1", severity=.5),
        Event("b", "RESOURCE_ACCESS", 3, 3, "D2", "D2", floor=3, network_segment="N3", severity=.9),
        Event("c", "DEVICE_OFFLINE", 3.1, 3.1, "D2", "D2", floor=3, network_segment="N3", severity=0.1)
    ]
    # S1 and D2 are on N3 and floor 3.
    for n, typ, floor, net in [("D1", "DEVICE", 1, "N1"), ("S1", "DEVICE", 3, "N3"), ("D2", "DEVICE", 3, "N3")]:
        g.upsert_node(n, typ, floor=floor, network_segment=net)
    for e in evs: g.apply(e)
    
    paths = AttackReconstructor(min_plausibility=65.0).reconstruct(g, "D1")
    for p in paths:
        assert "D2" not in p.nodes


def test_high_value_asset_alone_insufficient():
    # temporal (30) + high_value (10) = 40 < 65
    g = DynamicSecurityGraph()
    evs = [
        Event("a", "AUTHENTICATION", 1, 1, "D1", "S1", device_id="D1", floor=1, network_segment="N1", severity=.5),
        Event("b", "RESOURCE_ACCESS", 3, 3, "S2", "S2", floor=9, network_segment="N9", severity=.9),
    ]
    # S1 (N3/3), S2 is SERVER (N9/9)
    for n, typ, floor, net in [("D1", "DEVICE", 1, "N1"), ("S1", "DEVICE", 3, "N3"), ("S2", "SERVER", 9, "N9")]:
        g.upsert_node(n, typ, floor=floor, network_segment=net)
    for e in evs: g.apply(e)
    
    paths = AttackReconstructor(min_plausibility=65.0).reconstruct(g, "D1")
    for p in paths:
        assert "S2" not in p.nodes


def test_strong_combined_evidence_produces_gap():
    # temporal (25) + network (15) + identity (30) = 70 >= 65 -> Plausible
    g = DynamicSecurityGraph()
    evs = [
        Event("a", "AUTHENTICATION", 1, 1, "D1", "S1", device_id="D1", user_id="U1", floor=1, network_segment="N1", severity=.5),
        Event("b", "RESOURCE_ACCESS", 3, 3, "S2", "S2", device_id="D1", user_id="U1", floor=4, network_segment="N3", severity=.9),
    ]
    # S1 (N3/3), S2 is SERVER (N3/4)
    for n, typ, floor, net in [("D1", "DEVICE", 1, "N1"), ("S1", "DEVICE", 3, "N3"), ("S2", "SERVER", 4, "N3")]:
        g.upsert_node(n, typ, floor=floor, network_segment=net)
    for e in evs: g.apply(e)
    
    paths = AttackReconstructor(min_plausibility=65.0).reconstruct(g, "D1")
    found_s2 = any("S2" in p.nodes for p in paths)
    assert found_s2


def test_explicit_path_outranks_inferred_path():
    # D1 -> S1
    # Path 1: S1 infers D3 (temporal 30 + network 25 + spatial 15 = 70) => D3
    # Path 2: S1 explicitly connects D4, D4 connects D3
    g = DynamicSecurityGraph()
    evs = [
        Event("a", "AUTHENTICATION", 1, 1, "D1", "S1", device_id="D1", floor=1, network_segment="N1", severity=.5),
        # Path 1 (inference gap via D3)
        Event("c1", "NETWORK_CONNECTION", 3, 3, "D3", "D5", floor=3, network_segment="N3", severity=.9),
        # Path 2 (explicit)
        Event("b2", "NETWORK_CONNECTION", 2, 2, "S1", "D4", floor=3, network_segment="N3", severity=.8),
        Event("c2", "NETWORK_CONNECTION", 3, 3, "D4", "D3", floor=3, network_segment="N3", severity=.9),
    ]
    for n, typ, floor, net in [("D1", "DEVICE", 1, "N1"), ("S1", "SERVER", 3, "N3"), ("D3", "DEVICE", 3, "N3"), ("D4", "DEVICE", 3, "N3"), ("D5", "DEVICE", 3, "N3")]:
        g.upsert_node(n, typ, floor=floor, network_segment=net)
    for e in evs: g.apply(e)
    
    paths = AttackReconstructor(min_plausibility=65.0).reconstruct(g, "D1")
    # Best path must be the explicit one
    best = paths[0]
    assert best.nodes[:4] == ["D1", "S1", "D4", "D3"]
    assert not best.edges[0].is_inferred
    assert not best.edges[1].is_inferred
    assert not best.edges[2].is_inferred


def test_inference_budget():
    # temporal (30) + network (25) + spatial (15) = 70 >= 65
    g = DynamicSecurityGraph()
    evs = [
        Event("a", "AUTHENTICATION", 1, 1, "D1", "S1", device_id="D1", floor=3, network_segment="N3", severity=.5),
        Event("b", "NETWORK_CONNECTION", 2, 2, "D2", "D3", floor=3, network_segment="N3", severity=.8),
        Event("c", "NETWORK_CONNECTION", 3, 3, "D4", "D5", floor=3, network_segment="N3", severity=.9),
        Event("d", "NETWORK_CONNECTION", 4, 4, "D6", "D7", floor=3, network_segment="N3", severity=.9),
    ]
    for n in ["D1", "S1", "D2", "D3", "D4", "D5", "D6", "D7"]:
        g.upsert_node(n, "DEVICE", floor=3, network_segment="N3")
    for e in evs: g.apply(e)
    
    paths = AttackReconstructor(max_inferred_gaps=1, min_plausibility=65.0).reconstruct(g, "D1")
    for p in paths:
        inferred = sum(1 for e in p.edges if e.is_inferred)
        assert inferred <= 1
