import sys
import os
import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from demo.run_autonomous_soc import run_pipeline

def test_run_autonomous_soc_scenario_1(capsys):
    run_pipeline("1")
    captured = capsys.readouterr()
    output = captured.out
    
    assert "NEUROBRAIN X ENTERPRISE AUTONOMOUS SOC" in output
    assert "Risk:" in output
    assert "MITRE Techniques:" in output
    assert "SOC Copilot:" in output
    assert "Security Memory:" in output
    assert "Threat Prediction:" in output
    assert "Automated Playbook:" in output
    assert "Enterprise Impact:" in output
    assert "No attack paths reconstructed" not in output

def test_run_autonomous_soc_scenario_2(capsys):
    run_pipeline("2")
    captured = capsys.readouterr()
    assert "NEUROBRAIN X ENTERPRISE AUTONOMOUS SOC" in captured.out
    assert "No attack paths reconstructed" not in captured.out

def test_run_autonomous_soc_scenario_3(capsys):
    run_pipeline("3")
    captured = capsys.readouterr()
    assert "NEUROBRAIN X ENTERPRISE AUTONOMOUS SOC" in captured.out
    assert "No attack paths reconstructed" not in captured.out

def test_run_autonomous_soc_scenario_4(capsys):
    run_pipeline("4")
    captured = capsys.readouterr()
    assert "NEUROBRAIN X ENTERPRISE AUTONOMOUS SOC" in captured.out
    assert "No attack paths reconstructed" not in captured.out
