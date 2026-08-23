import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scenarios.judge_scenarios import JudgeScenarios
from demo.final_showcase import showcase
from benchmarks.final_benchmark import run_benchmarks

def test_judge_scenarios():
    js = JudgeScenarios()
    
    s1 = js.invisible_employee()
    assert "Invisible" in s1.name
    
    s2 = js.silent_insider()
    assert "Insider" in s2.name
    
    s3 = js.ransomware_sprint()
    assert "Ransomware" in s3.name
    
    s4 = js.apt_ghost_campaign()
    assert "APT" in s4.name

def test_final_showcase():
    # Should run flawlessly for all 4 profiles
    showcase("1")
    showcase("2")
    showcase("3")
    showcase("4")

def test_final_benchmarks():
    # Should run flawlessly
    run_benchmarks()
