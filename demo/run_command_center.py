import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.threat_actor import ThreatActorProfile
from scenarios.adversarial_scenarios import FinalScenarios
from app.engine import DynamicSecurityGraph, AttackReconstructor
from app.simulator import process_events
from app.hypotheses import AttackHypothesis
from app.threat_intel import MitreMapper
from app.investigation import InvestigationTimeline
from app.risk_engine import RiskAssessment
from app.explanation import PathExplanation
from app.soc_copilot import SOCCopilot
from app.response_engine import ResponseEngine

def run_cmd_center(scenario_id: str):
    scenarios = FinalScenarios()
    actor = ThreatActorProfile(scenarios)
    
    profiles = {
        "1": actor.simulate_apt,
        "2": actor.simulate_insider,
        "3": actor.simulate_credential_theft,
        "4": actor.simulate_ransomware
    }
    
    data = profiles.get(scenario_id, actor.simulate_apt)()
    
    ready, _ = process_events(data.events)
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
        
    recon = AttackReconstructor()
    paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    
    if not paths:
        print("No paths reconstructed.")
        return
        
    hyps = AttackHypothesis.generate(paths)
    best_hyp = hyps[0]
    best_path = best_hyp.attack_path
    
    exp = PathExplanation.generate(best_path)
    mitre = MitreMapper.extract_techniques(best_path, g)
    timeline = InvestigationTimeline.generate(best_path, g)
    risk = RiskAssessment.calculate(best_path, exp)
    
    copilot = SOCCopilot.generate_brief(exp, risk, timeline, mitre)
    plan = ResponseEngine.generate_plan(risk, mitre, [e for e in exp["evidence"] if "anomaly" in e.lower() or "stolen" in e.lower()])
    
    print("==========================")
    print("NEUROBRAIN X COMMAND CENTER")
    print("==========================\n")
    
    print(f"ATTACK DETECTED:\nProfile: {data.name}\nTarget: {data.ground_truth['target']}\n")
    
    print("MITRE:\n" + "\n".join([f"- {t['technique_id']}: {t['technique_name']}" for t in mitre]) + "\n")
    
    print(f"RISK:\n{risk['risk_score']}/100 ({risk['severity']})\n")
    
    print("SOC COPILOT:\n")
    print(f"What happened?\n{copilot['what_happened']}\n")
    print(f"Why was this detected?\n{copilot['why']}\n")
    print(f"Summary:\n{copilot['attack_summary']}\n")
    
    print("AUTOMATED RESPONSE:\n")
    print(f"Severity: {plan['severity']}")
    print("Actions:")
    for a in plan['actions']:
        print(f" - {a}")
    print("\n==========================")

if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "1"
    run_cmd_center(scenario)
