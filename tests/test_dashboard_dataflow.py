import pytest
from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_dashboard_dataflow_dynamic():
    """
    Ensures that the API returns dynamic intelligence parameters instead of
    forcing the frontend to rely on static mockData.
    """
    # 1. Baseline Incident (APT)
    res_base = client.get("/api/incident?scenario=APT")
    assert res_base.status_code == 200
    data_base = res_base.json()
    
    assert "risk" in data_base
    assert "copilot" in data_base
    assert "mitre" in data_base
    
    risk_score_base = data_base["risk"]["risk_score"]
    
    # 2. Degraded Telemetry (Loss 40%)
    res_deg = client.get("/api/resilience?loss=0.4&delay=4&duplicate=0.1&scenario=APT")
    assert res_deg.status_code == 200
    data_deg = res_deg.json()
    
    # 3. Test scenario switching (RANSOMWARE)
    res_scen = client.get("/api/resilience?loss=0.0&delay=0&duplicate=0.0&scenario=RANSOMWARE")
    assert res_scen.status_code == 200
    data_scen = res_scen.json()
    
    # 4. Compare outputs to ensure dynamic behavior
    risk_score_deg = data_deg.get("risk", {}).get("risk_score") if data_deg.get("best_path") else None
    risk_score_scen = data_scen.get("risk", {}).get("risk_score")
    
    assert data_base != data_deg, "Degraded output should differ from baseline"
    assert data_base != data_scen, "Scenario RANSOMWARE output should differ from APT"
    
    # If baseline and degraded outputs genuinely happen to be identical, the test should verify that the request was actually recomputed.
    # We verify this by checking that the input missing telemetry is respected.
    assert data_deg["input"]["missing"] == 0.4
    assert data_deg["accepted_events"] < data_base["events"].__len__(), "Should have dropped some events"
    
    if data_deg.get("best_path"):
        assert data_deg["copilot"]["why"] is not None
        assert isinstance(data_deg["mitre"], list)

    print("Dashboard Dataflow Test Passed!")
