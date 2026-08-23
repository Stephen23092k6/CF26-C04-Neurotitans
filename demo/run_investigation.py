import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scenarios.adversarial_scenarios import FinalScenarios
from app.simulator import process_events
from app.engine import DynamicSecurityGraph, AttackReconstructor
from app.hypotheses import AttackHypothesis
from app.threat_intel import MitreMapper
from app.investigation import InvestigationTimeline
from app.risk_engine import RiskAssessment
from app.explanation import PathExplanation

def run_investigation(sc_idx=1):
    sim = FinalScenarios()
    
    scenarios = {
        1: sim.get_scenario_1_vpn_rotation,
        2: sim.get_scenario_2_stolen_credential,
        3: sim.get_scenario_3_identity_spoof,
        4: sim.get_scenario_4_lotl
    }
    
    if sc_idx not in scenarios:
        print("Invalid scenario")
        return
        
    data = scenarios[sc_idx]()
        
    ready, _ = process_events(data.events)
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
        
    recon = AttackReconstructor()
    paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    
    if not paths:
        print("No attack paths reconstructed.")
        return
        
    hyps = AttackHypothesis.generate(paths)
    best_hyp = hyps[0]
    
    exp = PathExplanation.generate(best_hyp.attack_path)
    mitre = MitreMapper.extract_techniques(best_hyp.attack_path, g)
    timeline = InvestigationTimeline.generate(best_hyp.attack_path, g)
    risk = RiskAssessment.calculate(best_hyp.attack_path, exp)
    
    print("====================================")
    print(" NEUROBRAIN X SOC INVESTIGATION ")
    print("====================================")
    
    print(f"\nINCIDENT TYPE:\n{data.name}")
    print("\nATTACK HYPOTHESES:")
    for i, h in enumerate(hyps[:3]):
        print(f"{i+1}.")
        print(f"Name:\n{h.name}")
        print(f"Confidence:\n{h.confidence}%\n")
        
    print("MITRE TECHNIQUES:")
    if not mitre:
        print("None")
    for m in mitre:
        print(f"- {m['technique_id']} {m['technique_name']} (Confidence: {m['confidence']})")
        
    print("\nIDENTITY ANALYSIS:")
    for k, v in exp["identity_analysis"].items():
        if v:
            print(f"- {k.upper()} detected")
            
    print("\nTIMELINE:")
    for t in timeline:
        print(f"{t['timestamp']:.1f} | {t['event']} | {t['source']} -> {t['destination']}")
        
    print(f"\nRISK SCORE:\n{risk['risk_score']} ({risk['severity']})")
    print("\nRECOMMENDED ACTIONS:")
    if risk["severity"] in ["HIGH", "CRITICAL"]:
        print("Isolate affected assets and force credential rotations.")
    else:
        print("Monitor for further activity.")
        
    print("\n====================================")

if __name__ == "__main__":
    run_investigation(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
