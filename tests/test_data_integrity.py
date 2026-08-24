import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.api import app

client = TestClient(app)

def test_data_integrity_on_telemetry_change():
    """
    Verify that when UI sliders change (loss, delay, duplicate),
    the request payload changes, backend processes it, and
    returned intelligence is derived from new computation.
    """
    # Baseline
    res1 = client.get("/api/resilience?loss=0.0&delay=0&duplicate=0.0")
    assert res1.status_code == 200
    data1 = res1.json()
    
    # Change sliders
    res2 = client.get("/api/resilience?loss=0.1&delay=2&duplicate=0.2")
    assert res2.status_code == 200
    data2 = res2.json()
    
    # 1. request payload actually changes - implicit via different endpoints
    assert data1["input"] != data2["input"]
    
    # 2. backend actually processes the changed telemetry
    # Duplicate processing should be different
    assert data1["processor"]["dropped_duplicates"] != data2["processor"]["dropped_duplicates"]
    
    # 3. returned intelligence is derived from new computation
    # For example, different events should result in a different timeline size 
    # or risk scores/events being parsed. If the underlying data is exactly the same, 
    # it might be identical, but these values guarantee different telemetry.
    assert data1.get("timeline") != data2.get("timeline")
    
def test_no_hardcoded_dashboard_intelligence():
    """
    Verify that dashboard.js does not contain production-path hardcoded intelligence.
    """
    dashboard_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dashboard", "dashboard.js")
    with open(dashboard_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check for hardcoded risk score
    assert "risk_score: 94" not in content, "Hardcoded risk score found in dashboard.js"
    
    # Check for fixed Copilot text
    assert "Anomalous lateral movement detected using compromised service accounts." not in content, "Hardcoded Copilot text found"
    
    # Check for fixed MITRE technique arrays
    assert "T1078" not in content or "T1068" not in content, "Fixed MITRE techniques found in dashboard.js"
    
    # Check for fixed playbook actions
    assert "Isolate infected endpoints" not in content, "Fixed playbook action found in dashboard.js"
