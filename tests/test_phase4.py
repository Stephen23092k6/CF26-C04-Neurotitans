import pytest
from app.simulator import process_events
from app.engine import DynamicSecurityGraph, AttackReconstructor
from app.adversary import IdentityAdversarySimulator

def test_vpn_rotation_recovery():
    sim = IdentityAdversarySimulator()
    data = sim.simulate_vpn_rotation()
    ready, _ = process_events(data.events)
    
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
        
    recon = AttackReconstructor()
    paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    
    assert len(paths) > 0
    best_path = paths[0]
    
    # Target reached and path valid
    assert best_path.nodes[-1] == data.ground_truth["target"]
    
    # We expect high confidence because identity continuity +30 mitigates the spatial/network gaps
    assert best_path.confidence > 60.0
    
    # Verify the explanation contains the VPN rotation reason
    vpn_reasons = [e.inference_reason for e in best_path.edges if "vpn_rotation" in e.inference_reason]
    # In explicit hops, inference_reason is used to store continuity reasons
    assert any("vpn_rotation_continuity" in e.inference_reason for e in best_path.edges)

def test_ip_churn_recovery():
    sim = IdentityAdversarySimulator()
    data = sim.simulate_ip_churn()
    ready, _ = process_events(data.events)
    
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
        
    paths = AttackReconstructor().reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    
    assert len(paths) > 0
    best = paths[0]
    assert best.nodes[-1] == data.ground_truth["target"]
    assert any("strong_identity_continuity" in e.inference_reason or "device_continuity" in e.inference_reason for e in best.edges)

def test_stolen_credential_confidence_reduction():
    sim = IdentityAdversarySimulator()
    data = sim.simulate_stolen_credential()
    ready, _ = process_events(data.events)
    
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
        
    recon = AttackReconstructor()
    paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    
    if paths:
        best = paths[0]
        # If it managed to reach the target despite the anomaly, it should have reduced confidence.
        # If it failed to reach the target, that is also a correct rejection.
        if best.nodes[-1] == data.ground_truth["target"]:
            assert best.confidence < 85.0

def test_fake_identity_rejection():
    sim = IdentityAdversarySimulator()
    data = sim.simulate_identity_spoofing()
    ready, _ = process_events(data.events)
    
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
        
    recon = AttackReconstructor(min_plausibility=60.0)
    paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    
    if paths:
        best = paths[0]
        # If it reconstructs via background noise or survives the penalty to reach target, it must be severely degraded.
        if best.nodes[-1] == data.ground_truth["target"]:
            assert best.score < 50.0  # severely degraded
