import sys
import os
import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.security_memory import SecurityMemory
from app.prediction_engine import ThreatPredictionEngine
from app.playbook_engine import SecurityPlaybookEngine
from app.enterprise import EnterpriseEnvironment
from demo.run_autonomous_soc import run_pipeline

def test_security_memory():
    memory = SecurityMemory()
    assert len(memory.incidents) == 3  # Based on seeded data
    
    memory.add_incident("INC-999", ["T1001", "T1002"], "Test Pattern", "Test Family", ["Do nothing"])
    assert len(memory.incidents) == 4
    
    history = memory.get_threat_history()
    assert history["total_incidents_in_memory"] == 4
    assert "Test Pattern" in history["known_patterns"]

def test_incident_similarity():
    memory = SecurityMemory()
    memory.add_incident("INC-100", ["T1", "T2", "T3"], "Pattern A", "Family A", [])
    
    similar = memory.retrieve_similar_incidents(["T1", "T2"])
    assert len(similar) == 1
    assert similar[0]["previous_pattern"] == "Pattern A"

def test_prediction_engine():
    memory = SecurityMemory()
    engine = ThreatPredictionEngine(memory)
    
    # Mocking AttackPath
    class MockEdge:
        continuity_penalty = 0
    class MockPath:
        edges = [MockEdge()]
        
    prediction = engine.predict(MockPath(), [{"technique_id": "T1021"}])
    assert "Privilege Escalation" in prediction["predicted_actions"]
    assert prediction["confidence"] >= 40
    
def test_playbook_generation():
    engine = SecurityPlaybookEngine()
    playbook = engine.generate_playbook("CRITICAL", ["T1003", "T1021"])
    
    # Needs to include T1003 and T1021 specific steps
    found_t1003 = any("LSASS" in step or "passwords" in step for step in playbook)
    found_t1021 = any("SMB/RDP" in step for step in playbook)
    
    assert found_t1003
    assert found_t1021
    
    sim_result = engine.execute_simulation(playbook)
    assert sim_result["status"] == "simulated_success"

def test_enterprise_assets():
    env = EnterpriseEnvironment()
    env.add_asset("server-1", "CRITICAL", "IT")
    env.add_asset("wkstn-1", "LOW", "HR")
    
    criticals = env.get_critical_assets()
    assert len(criticals) == 1
    assert criticals[0]["asset"] == "server-1"
    
    asset = env.get_asset("wkstn-1")
    assert asset["owner"] == "HR"

def test_autonomous_soc_pipeline():
    # Should run without crashing
    try:
        run_pipeline()
        success = True
    except Exception as e:
        success = False
        print(e)
    assert success
