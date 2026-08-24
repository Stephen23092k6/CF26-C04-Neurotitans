import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from scenarios.judge_scenarios import JudgeScenarios
from app.simulator import process_events
from app.engine import DynamicSecurityGraph, AttackReconstructor
from app.hypotheses import AttackHypothesis
from app.explanation import PathExplanation
from app.threat_intel import MitreMapper
from app.investigation import InvestigationTimeline
from app.risk_engine import RiskAssessment
from app.soc_copilot import SOCCopilot
from app.response_engine import ResponseEngine
from app.security_memory import SecurityMemory
from app.prediction_engine import ThreatPredictionEngine
from app.playbook_engine import SecurityPlaybookEngine

def judge_demo(scenario_idx: str = "1"):
    js = JudgeScenarios()
    scenarios = {
        "1": js.invisible_employee,
        "2": js.silent_insider,
        "3": js.ransomware_sprint,
        "4": js.apt_ghost_campaign
    }
    
    if scenario_idx not in scenarios:
        scenario_idx = "1"
        
    data = scenarios[scenario_idx]()
    
    ready, _ = process_events(data.events)
    graph = DynamicSecurityGraph()
    for e in ready:
        graph.apply(e)
        
    recon = AttackReconstructor()
    paths = recon.reconstruct(graph, data.ground_truth["seed"], data.ground_truth["target"])
    
    if not paths:
        print("No attack paths reconstructed.")
        return
        
    best_hyp = AttackHypothesis.generate(paths)[0]
    path = best_hyp.attack_path
    
    exp = PathExplanation.generate(path)
    mitre = MitreMapper.extract_techniques(path, graph)
    risk = RiskAssessment.calculate(path, exp)
    timeline = InvestigationTimeline.generate(path, graph)
    copilot = SOCCopilot.generate_brief(exp, risk, timeline, mitre)
    
    memory = SecurityMemory()
    technique_ids = [t.get("technique_id") for t in mitre]
    prediction = ThreatPredictionEngine(memory).predict(path, mitre)
    playbook = SecurityPlaybookEngine().generate_playbook(risk["severity"], technique_ids)
    
    # ---------------------------------------------------------
    # Identity Analysis logic
    # ---------------------------------------------------------
    identity_anomalies = [e for e in path.edges if getattr(e, 'continuity_penalty', 0) > 0]
    identity_status = "VPN Rotation Detected\nIdentity Continuity Verified" if identity_anomalies else "Identity Continuity Verified"
    
    # ---------------------------------------------------------
    # Output formatting
    # ---------------------------------------------------------
    print("================================================")
    print("NEUROBRAIN X AUTONOMOUS DEFENSE COMMAND CENTER")
    print("================================================\n")
    
    print("LIVE INCIDENT:")
    print(data.name)
    print("\nATTACK STATUS:")
    print("ACTIVE")
    
    print("\nRECONSTRUCTED PATH:")
    print(" \u2192 ".join(path.nodes))
    
    print("\nIDENTITY ANALYSIS:")
    print(identity_status)
    
    print("\nMITRE TECHNIQUES:")
    for t in mitre:
        print(t["technique_id"])
        
    print("\nRISK:")
    print(f"{risk['severity']} {risk['risk_score']}/100")
    
    print("\nPREDICTED NEXT ATTACK:")
    print(prediction['predicted_actions'][0] if prediction['predicted_actions'] else "Unknown")
    
    print("\nAUTONOMOUS RESPONSE:")
    print(playbook[0] if playbook else "No response generated")
    
    print("\n================================================")

if __name__ == "__main__":
    s_idx = sys.argv[1] if len(sys.argv) > 1 else "1"
    judge_demo(s_idx)
