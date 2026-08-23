import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.engine import DynamicSecurityGraph, AttackReconstructor
from app.simulator import process_events
from scenarios.adversarial_scenarios import FinalScenarios
from app.explanation import PathExplanation
from app.analyst import AnalystReportGenerator
from demo.run_final_demo import run_demo

def test_explanation_generation():
    sim = FinalScenarios()
    data = sim.get_scenario_4_lotl()
    
    ready, _ = process_events(data.events)
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
        
    recon = AttackReconstructor()
    paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    
    assert len(paths) > 0
    best_path = paths[0]
    
    exp = PathExplanation.generate(best_path)
    assert "confidence" in exp
    assert "decision" in exp
    assert exp["decision"] in ["HIGH_CONFIDENCE_ATTACK_PATH", "MEDIUM_CONFIDENCE_ATTACK_PATH", "LOW_CONFIDENCE_PATH"]
    
    # LOTL scenario doesn't have an identity contradiction
    assert not exp["identity_analysis"]["credential_risk"]
    assert not exp["identity_analysis"]["identity_spoofing"]

def test_vpn_rotation_explanation():
    sim = FinalScenarios()
    data = sim.get_scenario_1_vpn_rotation()
    
    ready, _ = process_events(data.events)
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
        
    recon = AttackReconstructor()
    paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    
    assert len(paths) > 0
    best_path = paths[0]
    
    exp = PathExplanation.generate(best_path)
    assert exp["identity_analysis"]["vpn_rotation_detected"]
    
    report = AnalystReportGenerator.generate(exp)
    assert "VPN Rotation" in report

def test_stolen_credentials_penalty():
    sim = FinalScenarios()
    data = sim.get_scenario_2_stolen_credential()
    
    ready, _ = process_events(data.events)
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
        
    recon = AttackReconstructor()
    paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    
    if paths:
        best_path = paths[0]
        # if the path reached the target, the penalty should be reflected in the explanation
        if best_path.nodes[-1] == data.ground_truth["target"]:
            exp = PathExplanation.generate(best_path)
            assert exp["identity_analysis"]["credential_risk"]
            report = AnalystReportGenerator.generate(exp)
            assert "Credential" in report

def test_demo_pipeline():
    # Just running it to ensure no exceptions
    run_demo(1)
    run_demo(4)
