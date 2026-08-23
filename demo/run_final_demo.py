import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scenarios.adversarial_scenarios import FinalScenarios
from app.simulator import process_events
from app.engine import DynamicSecurityGraph, AttackReconstructor
from app.explanation import PathExplanation
from app.analyst import AnalystReportGenerator

def run_demo(scenario_num=1):
    sim = FinalScenarios()
    
    if scenario_num == 1:
        data = sim.get_scenario_1_vpn_rotation()
    elif scenario_num == 2:
        data = sim.get_scenario_2_stolen_credential()
    elif scenario_num == 3:
        data = sim.get_scenario_3_identity_spoof()
    elif scenario_num == 4:
        data = sim.get_scenario_4_lotl()
    else:
        print("Invalid scenario")
        return
        
    print(f"Loading Scenario: {data.name}...")
    
    # Process events
    ready, _ = process_events(data.events)
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
        
    # Reconstruct
    recon = AttackReconstructor()
    paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
    
    if not paths:
        print("\nNo paths reconstructed! Attack successfully rejected or undetected.")
        return
        
    best_path = paths[0]
    
    # Explainability
    explanation = PathExplanation.generate(best_path)
    
    # Analyst Report
    report = AnalystReportGenerator.generate(explanation)
    
    # Demo Output Formatting
    print("\n" + "="*33)
    print("NEUROBRAIN X FINAL DEMO")
    print("="*33 + "\n")
    print(f"Scenario:\n{data.name}\n")
    print(f"Attack Path:\n{' -> '.join(best_path.nodes)}\n")
    
    print(report)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_demo(int(sys.argv[1]))
    else:
        # Run Scenario 1 by default
        run_demo(1)
