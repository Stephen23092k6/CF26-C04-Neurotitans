import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
from app.soc_copilot import SOCCopilot
from app.threat_actor import ThreatActorProfile
from scenarios.adversarial_scenarios import FinalScenarios
from app.response_engine import ResponseEngine

def test_soc_copilot_generation():
    exp = {"evidence": ["Identity mismatch"]}
    risk = {"severity": "CRITICAL", "risk_score": 90}
    timeline = [{"timestamp": 0, "event": "AUTH", "source": "A", "destination": "B"}]
    mitre = [{"technique_id": "T1078", "technique_name": "Valid Accounts"}]
    
    brief = SOCCopilot.generate_brief(exp, risk, timeline, mitre)
    assert "Identity mismatch" in brief["why"]
    assert "1 chronological events" in brief["what_happened"]
    assert "T1078" in brief["attack_summary"]

def test_threat_actor_profiles():
    actor = ThreatActorProfile(FinalScenarios())
    assert actor.simulate_apt().name == "APT"
    assert actor.simulate_insider().name == "INSIDER"
    assert actor.simulate_credential_theft().name == "CREDENTIAL_THEFT"
    assert actor.simulate_ransomware().name == "RANSOMWARE"

def test_response_engine_mapping():
    plan = ResponseEngine.generate_plan({"severity": "CRITICAL"}, [{"technique_id": "T1078"}], ["anomaly"])
    assert plan["severity"] == "CRITICAL"
    assert "Isolate endpoint" in plan["actions"]
    assert "Force credential reset" in plan["actions"]

def test_command_center_pipeline():
    from demo.run_command_center import run_cmd_center
    # Ensure it runs without exception
    run_cmd_center("1")
    run_cmd_center("2")
    run_cmd_center("3")
    run_cmd_center("4")

def test_dashboard_files_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "frontend" / "dashboard" / "index.html").exists()
    assert (root / "frontend" / "dashboard" / "dashboard.js").exists()
