import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scenarios.judge_scenarios import JudgeScenarios
from app.engine import DynamicSecurityGraph, AttackReconstructor
from app.simulator import process_events
from app.hypotheses import AttackHypothesis
from app.threat_intel import MitreMapper
from app.investigation import InvestigationTimeline
from app.risk_engine import RiskAssessment
from app.explanation import PathExplanation
from app.soc_copilot import SOCCopilot
from app.response_engine import ResponseEngine

def showcase(scenario_idx: str = "1"):
    js = JudgeScenarios()
    scenarios = {
        "1": js.invisible_employee,
        "2": js.silent_insider,
        "3": js.ransomware_sprint,
        "4": js.apt_ghost_campaign
    }
    
    if scenario_idx not in scenarios:
        scenario_idx = "1"
        
    print(f"\n[+] Loading Showcase Scenario {scenario_idx}...")
    data = scenarios[scenario_idx]()
    
    print(f"[+] Processing {len(data.events)} raw telemetry events...")
    start_t = time.time()
    ready, _ = process_events(data.events)
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
    proc_t = (time.time() - start_t) * 1000
    
    print(f"[+] Reconstructing Attack Graph...")
    start_t = time.time()
    recon = AttackReconstructor()
    paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    recon_t = (time.time() - start_t) * 1000
    
    if not paths:
        print("[-] Reconstruction failed.")
        return
        
    print(f"[+] Applying Intelligence Layers...")
    best_hyp = AttackHypothesis.generate(paths)[0]
    best_path = best_hyp.attack_path
    
    exp = PathExplanation.generate(best_path)
    mitre = MitreMapper.extract_techniques(best_path, g)
    timeline = InvestigationTimeline.generate(best_path, g)
    risk = RiskAssessment.calculate(best_path, exp)
    
    copilot = SOCCopilot.generate_brief(exp, risk, timeline, mitre)
    plan = ResponseEngine.generate_plan(risk, mitre, [e for e in exp["evidence"] if "anomaly" in e.lower() or "stolen" in e.lower()])
    
    print("\n" + "="*50)
    print(" NEUROBRAIN X: HACKATHON GRAND FINALE SHOWCASE")
    print("="*50)
    print(f"\nSCENARIO: {data.name}")
    print(f"PERFORMANCE: Processing: {proc_t:.1f}ms | Reconstruction: {recon_t:.1f}ms")
    
    print(f"\n[ RISK ASSESSMENT ]")
    print(f"Score: {risk['risk_score']}/100 | Severity: {risk['severity']}")
    
    print(f"\n[ MITRE ATT&CK ]")
    for t in mitre:
        print(f" - {t['technique_id']}: {t['technique_name']}")
        
    print(f"\n[ SOC COPILOT ]")
    print(f"WHY: {copilot['why']}")
    print(f"WHAT HAPPENED: {copilot['what_happened']}")
    
    print(f"\n[ RESPONSE ENGINE ]")
    print(f"Recommended Plan ({plan['severity']} Priority):")
    for a in plan['actions']:
        print(f" -> {a}")
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    s_idx = sys.argv[1] if len(sys.argv) > 1 else "1"
    showcase(s_idx)
