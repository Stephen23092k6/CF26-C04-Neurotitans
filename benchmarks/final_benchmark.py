import sys
import time
import os
from pathlib import Path

# Fix python path for benchmarks running in a subdirectory
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scenarios.judge_scenarios import JudgeScenarios
from app.engine import DynamicSecurityGraph, AttackReconstructor
from app.simulator import process_events

def run_benchmarks():
    js = JudgeScenarios()
    scenarios = [
        js.invisible_employee(),
        js.silent_insider(),
        js.ransomware_sprint(),
        js.apt_ghost_campaign()
    ]
    
    print(f"{'SCENARIO':<40} | {'PROCESS (ms)':<12} | {'RECONSTRUCT (ms)':<16} | {'SCORE':<5}")
    print("-" * 80)
    
    for data in scenarios:
        t0 = time.perf_counter()
        ready, _ = process_events(data.events)
        g = DynamicSecurityGraph()
        for e in ready:
            g.apply(e)
        t1 = time.perf_counter()
        proc_time = (t1 - t0) * 1000
        
        t2 = time.perf_counter()
        recon = AttackReconstructor()
        paths = recon.reconstruct(g, data.ground_truth["seed"], data.ground_truth["target"])
        t3 = time.perf_counter()
        recon_time = (t3 - t2) * 1000
        
        score = paths[0].score if paths else 0.0
        
        print(f"{data.name[:38]:<40} | {proc_time:<12.2f} | {recon_time:<16.2f} | {score:<5.1f}")

if __name__ == "__main__":
    run_benchmarks()
