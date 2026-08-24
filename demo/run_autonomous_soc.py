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
from app.enterprise import EnterpriseEnvironment

def run_pipeline(scenario_idx: str = "1"):
    print("Initializing Neurobrain X Enterprise Autonomous SOC Pipeline...\n")
    
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
    
    # 1. Setup Enterprise Environment
    enterprise = EnterpriseEnvironment()
    enterprise.add_asset("D-999", "CRITICAL", "Finance", asset_type="server")
    enterprise.add_asset("S-02", "HIGH", "IT", asset_type="server")
    enterprise.add_asset(data.ground_truth["seed"], "MEDIUM", "Engineering")
    
    # 2. Process Events and Graph Ingestion
    ready, _ = process_events(data.events)
    graph = DynamicSecurityGraph()
    for e in ready:
        graph.apply(e)
        
    # 3. Attack Reconstruction
    recon = AttackReconstructor()
    paths = recon.reconstruct(graph, data.ground_truth["seed"], data.ground_truth["target"])
    
    if not paths:
        print("No attack paths reconstructed.")
        return
        
    # 4. Attack Hypothesis
    best_hyp = AttackHypothesis.generate(paths)[0]
    path = best_hyp.attack_path
    
    # 5. Explanation Layer
    exp = PathExplanation.generate(path)
    
    # 6. MITRE Mapping
    mitre_techniques = MitreMapper.extract_techniques(path, graph)
    
    # 7. Risk Engine
    risk_score = RiskAssessment.calculate(path, exp)
    
    # 8. Security Memory
    memory = SecurityMemory()
    technique_ids = [t.get("technique_id") for t in mitre_techniques if "technique_id" in t]
    memory.add_incident(
        incident_id=f"INC-{scenario_idx}",
        techniques=technique_ids,
        pattern=f"Detected {data.name}",
        family="Unknown",
        response=[]
    )
    similar_incidents = memory.retrieve_similar_incidents(technique_ids, top_k=1)
    
    # 9. Threat Prediction
    predictor = ThreatPredictionEngine(memory)
    prediction = predictor.predict(path, mitre_techniques)
    
    # 10. SOC Copilot
    timeline = InvestigationTimeline.generate(path, graph)
    copilot = SOCCopilot.generate_brief(exp, risk_score, timeline, mitre_techniques)
    
    # 11. Playbook Generator
    playbook_engine = SecurityPlaybookEngine()
    playbook = playbook_engine.generate_playbook(risk_score["severity"], technique_ids)
    
    # 12. Response Engine (From Phase 8/9, optional integration)
    plan = ResponseEngine.generate_plan(risk_score, mitre_techniques, [e for e in exp["evidence"] if "anomaly" in e.lower() or "stolen" in e.lower()])

    # Find affected assets
    affected_assets = []
    for node in path.nodes:
        asset_info = enterprise.get_asset(node)
        if asset_info["criticality"] != "UNKNOWN":
            affected_assets.append(asset_info)
    
    # Output the Final Enterprise SOC Report
    print("================================================")
    print("NEUROBRAIN X ENTERPRISE AUTONOMOUS SOC")
    print("================================================\n")
    
    print("Scenario:")
    print(data.name)
    print(f"\nRisk:")
    print(f"{risk_score['severity']} {risk_score['risk_score']}/100")
    
    print("\nMITRE Techniques:")
    for t in mitre_techniques:
        print(f"- {t['technique_id']}: {t['technique_name']}")
        
    print("\nSOC Copilot:")
    print("- Why detected:")
    print(f"  {copilot['why']}")
    print("- What happened:")
    print(f"  {copilot['what_happened']}")
    
    print("\nSecurity Memory:")
    if similar_incidents:
        for sim in similar_incidents:
            print(f"- Similar incidents found: Pattern '{sim['previous_pattern']}' ({int(sim['incident_similarity']*100)}% Match)")
    else:
        print("- No highly similar past incidents found.")
        
    print("\nThreat Prediction:")
    print("- Predicted next attacker actions:")
    for pa in prediction["predicted_actions"]:
        print(f"  > {pa}")
    print(f"- Confidence: {prediction['confidence']}%")
    print("- Reasoning:")
    for r in prediction["reasoning"]:
        print(f"  > {r}")
        
    print("\nAutomated Playbook:")
    print("- Response steps:")
    for step in playbook:
        print(f"  {step}")
        
    print("\nEnterprise Impact:")
    print("- Affected assets:")
    if affected_assets:
        for a in affected_assets:
            print(f"  > {a['asset']} (Criticality: {a['criticality']}, Owner: {a['owner']})")
    else:
        print("  > No registered critical assets affected.")
        
    print("\n================================================")

if __name__ == "__main__":
    s_idx = sys.argv[1] if len(sys.argv) > 1 else "1"
    run_pipeline(s_idx)
