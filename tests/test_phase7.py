import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.engine import DynamicSecurityGraph, AttackReconstructor, AttackPath, PathEvidence, Event
from scenarios.adversarial_scenarios import FinalScenarios
from app.simulator import process_events
from app.hypotheses import AttackHypothesis
from app.threat_intel import MitreMapper
from app.investigation import InvestigationTimeline
from app.risk_engine import RiskAssessment
from app.explanation import PathExplanation
from demo.run_investigation import run_investigation

def _get_path_for_scenario(scenario_func):
    data = scenario_func()
    ready, _ = process_events(data.events)
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
    recon = AttackReconstructor()
    paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    return paths, g

def test_hypothesis_generation():
    sim = FinalScenarios()
    paths, _ = _get_path_for_scenario(sim.get_scenario_1_vpn_rotation)
    assert len(paths) > 0
    hyps = AttackHypothesis.generate(paths)
    assert len(hyps) > 0
    names = [h.name for h in hyps]
    assert "Evasive Lateral Movement (VPN Rotation)" in names

def test_multiple_attack_paths():
    sim = FinalScenarios()
    paths, _ = _get_path_for_scenario(sim.get_scenario_4_lotl)
    # The reconstruction might only yield 1 path depending on noise, but hypothesis logic should handle list
    hyps = AttackHypothesis.generate(paths)
    assert len(hyps) == len(paths)

def test_mitre_mapping():
    # Make dummy event
    e1 = Event("test1", "AUTHENTICATION", 0.0, 0.0, "A", "B", severity=1.0)
    e2 = Event("test2", "COMMAND_EXECUTION", 0.0, 0.0, "A", "B", severity=1.0)
    
    edge = PathEvidence("A", "B", "relation", [e1.event_id, e2.event_id], 0.0, False, False)
    
    path = AttackPath(["A", "B"], [edge], 100.0, 100.0, [])
    
    g = DynamicSecurityGraph()
    g.events = [e1, e2]
    
    techs = MitreMapper.extract_techniques(path, g)
    t_ids = [t["technique_id"] for t in techs]
    assert "T1078" in t_ids
    assert "T1059" in t_ids

def test_timeline_generation():
    sim = FinalScenarios()
    paths, g = _get_path_for_scenario(sim.get_scenario_1_vpn_rotation)
    timeline = InvestigationTimeline.generate(paths[0], g)
    
    assert len(timeline) > 0
    assert "timestamp" in timeline[0]
    assert "event" in timeline[0]
    
    # Check ordering
    for i in range(len(timeline) - 1):
        assert timeline[i]["timestamp"] <= timeline[i+1]["timestamp"]

def test_risk_scoring():
    sim = FinalScenarios()
    paths, _ = _get_path_for_scenario(sim.get_scenario_3_identity_spoof)
    best_path = paths[0]
    exp = PathExplanation.generate(best_path)
    
    risk = RiskAssessment.calculate(best_path, exp)
    assert "risk_score" in risk
    assert "severity" in risk
    # Identity spoof is a severe penalty but increases risk
    # Since confidence drops, the final score depends on base score * conf * multiplier
    assert type(risk["risk_score"]) is float or type(risk["risk_score"]) is int

def test_full_investigation_pipeline():
    # Just run it to make sure it doesn't crash
    run_investigation(1)
    run_investigation(2)
