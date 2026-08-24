import sys
import os
import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from demo.judge_mode import judge_demo

def test_judge_mode_execution(capsys):
    """Validate that the judge mode pipeline runs end-to-end without errors."""
    try:
        judge_demo("4")
        success = True
    except Exception as e:
        success = False
        print(f"Judge demo failed: {e}")
        
    assert success
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Check for expected presentation output
    assert "NEUROBRAIN X AUTONOMOUS DEFENSE COMMAND CENTER" in output
    assert "LIVE INCIDENT:" in output
    assert "RECONSTRUCTED PATH:" in output
    assert "IDENTITY ANALYSIS:" in output
    assert "MITRE TECHNIQUES:" in output
    assert "RISK:" in output
    assert "PREDICTED NEXT ATTACK:" in output
    assert "AUTONOMOUS RESPONSE:" in output

def test_documentation_exists():
    """Verify that the required hackathon polish documents exist."""
    assert os.path.exists(os.path.join(os.path.dirname(__file__), "..", "README_FINAL.md"))
    assert os.path.exists(os.path.join(os.path.dirname(__file__), "..", "presentation", "judge_answers.md"))
    assert os.path.exists(os.path.join(os.path.dirname(__file__), "..", "benchmarks", "HACKATHON_RESULTS.md"))

def test_dashboard_panels_exist():
    """Verify that the new premium panels are integrated into the dashboard HTML."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dashboard", "index.html")
    assert os.path.exists(html_path)
    
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "ui-live-status" in content
    assert "ui-attack-path" in content
    assert "ui-autonomous-defense" in content
