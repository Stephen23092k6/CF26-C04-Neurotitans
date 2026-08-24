import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.engine import DynamicSecurityGraph, AttackReconstructor
from app.simulator import BuildingSimulator
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

def run_pipeline():
    print("Initializing Neurobrain X Enterprise Autonomous SOC Pipeline...")
    
    # 1. Setup Enterprise Environment
    enterprise = EnterpriseEnvironment()
    enterprise.add_asset("wkstn-88", "MEDIUM", "Engineering")
    enterprise.add_asset("db-server-01", "CRITICAL", "Finance", asset_type="server")
    enterprise.add_asset("dc-01", "CRITICAL", "IT", asset_type="server")
    
    # 2. Threat Actor Simulation
    sim = BuildingSimulator()
    scenario = sim.generate_scenario("APT Campaign", multi_path=True)
    
    # 3. Graph Ingestion
    graph = DynamicSecurityGraph()
    for ev in scenario.events:
        graph.apply(ev)
        
    # 4. Attack Reconstruction
    recon = AttackReconstructor(use_identity_layer=True)
    paths = recon.reconstruct(graph, seed="wkstn-88")
    if not paths:
        print("No attack paths reconstructed.")
        return
        
    path = paths[0]
    
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
        incident_id="INC-CURRENT",
        techniques=technique_ids,
        pattern="Detected Current APT",
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
    copilot_summary = copilot['what_happened']
    
    # 11. Playbook Generator
    playbook_engine = SecurityPlaybookEngine()
    playbook = playbook_engine.generate_playbook(risk_score["severity"], technique_ids)
    
    # Output the Final Enterprise SOC Report
    print("\n================================================")
    print("NEUROBRAIN X AUTONOMOUS SOC REPORT")
    print("================================================\n")
    
    print("Incident:")
    print("APT Ghost Campaign (Simulation)")
    print(f"\nRisk:")
    print(f"{risk_score['severity']} {risk_score['risk_score']}/100")
    
    print("\nDetected Techniques:")
    for t in mitre_techniques:
        print(f"- {t['technique_id']} {t['technique_name']}")
        
    print("\nPredicted Next Actions:")
    for pa in prediction["predicted_actions"]:
        print(f"- {pa}")
    print(f"(Confidence: {prediction['confidence']}%)")
    print("Reasoning:")
    for r in prediction["reasoning"]:
        print(f"  > {r}")
        
    print("\nRecommended Playbook:")
    for step in playbook:
        print(step)
        
    print("\n================================================")

if __name__ == "__main__":
    run_pipeline()
