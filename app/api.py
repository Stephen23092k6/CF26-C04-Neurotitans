
from __future__ import annotations
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys, json, asyncio

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.engine import DynamicSecurityGraph, AttackReconstructor
from app.simulator import BuildingSimulator, process_events, get_legacy_sim

from app.risk_engine import RiskAssessment
from app.soc_copilot import SOCCopilot
from app.threat_intel import MitreMapper
from app.playbook_engine import SecurityPlaybookEngine
from app.prediction_engine import ThreatPredictionEngine
from app.security_memory import SecurityMemory
from app.explanation import PathExplanation
from app.enterprise import EnterpriseEnvironment

app = FastAPI(title="Neurobrain X", version="0.2.0")
app.mount("/ui", StaticFiles(directory=str(ROOT/"frontend"), html=True), name="ui")

memory = SecurityMemory()
prediction_engine = ThreatPredictionEngine(memory)
playbook_engine = SecurityPlaybookEngine()
enterprise = EnterpriseEnvironment()
enterprise.add_asset("D-999", "CRITICAL", "DBA Team", "PostgreSQL")
enterprise.add_asset("S-02", "HIGH", "IAM Team", "Active Directory")

sim = get_legacy_sim()
processor_events, processor = process_events(sim.normal_events(120))
for e in processor_events:
    sim.graph.apply(e)

def run_attack(scenario: str = "1"):
    if scenario == "APT":
        scenario = "4"
    elif scenario == "INSIDER":
        scenario = "2"
    elif scenario == "RANSOMWARE":
        scenario = "3"
        
    if scenario == "1":
        from scenarios.judge_scenarios import JudgeScenarios
        attack_events = JudgeScenarios().invisible_employee().events
    elif scenario == "2":
        from scenarios.judge_scenarios import JudgeScenarios
        attack_events = JudgeScenarios().silent_insider().events
    elif scenario == "3":
        from scenarios.judge_scenarios import JudgeScenarios
        attack_events = JudgeScenarios().ransomware_sprint().events
    elif scenario == "4":
        from scenarios.judge_scenarios import JudgeScenarios
        attack_events = JudgeScenarios().apt_ghost_campaign().events
    else:
        attack_events = sim.attack_scenario()
        
    ready, proc = process_events(attack_events, reorder_window=8)
    g = DynamicSecurityGraph()
    for e in processor_events + ready:
        g.apply(e)
    recon = AttackReconstructor(time_window=120, max_depth=6)
    
    # Target and seed logic based on scenario
    seed, target = "D-007", "D-999"
    if scenario == "2":
        seed, target = "D-010", "S-01"
    elif scenario == "3":
        seed, target = "D-050", "S-02"
    elif scenario == "4":
        seed, target = "D-007", "D-999"
    elif scenario == "1":
        seed, target = "D-015", "S-01"
        
    paths = recon.reconstruct(g, seed, target)
    return g, paths, proc

def enrich_response(base_response, best_path, g):
    if not best_path:
        return base_response
        
    timeline = []
    for e in g.events:
        timeline.append({
            "timestamp": e.event_time,
            "event": e.event_type,
            "source": e.source,
            "destination": e.destination,
            "explanation": "anomaly" if e.severity >= 0.5 else ""
        })
        
    explanation_dict = PathExplanation.generate(best_path)
    risk = RiskAssessment.calculate(best_path, explanation_dict)
    mitre = MitreMapper.extract_techniques(best_path, g)
    tech_ids = [m["technique_id"] for m in mitre]
    playbook = playbook_engine.generate_playbook(risk["severity"], tech_ids)
    prediction = prediction_engine.predict(best_path, mitre)
    copilot = SOCCopilot.generate_brief(explanation_dict, risk, timeline, mitre)
    
    intel = {
        "risk": risk,
        "timeline": timeline,
        "responses": playbook[:3],
        "copilot": copilot,
        "mitre": mitre,
        "enterprise_assets": enterprise.get_critical_assets(),
        "prediction": prediction,
        "memory": {"similar_incidents": memory.retrieve_similar_incidents(tech_ids, top_k=1)},
        "playbook": playbook
    }
    
    base_response.update(intel)
    return base_response

@app.get("/")
def root():
    return FileResponse(ROOT/"frontend/index.html")

@app.get("/api/health")
def health():
    return {"status":"ok","product":"Neurobrain X","problem":"C-04"}

@app.get("/api/graph")
def graph():
    return sim.graph.export()

@app.get("/api/incident")
def incident(scenario: str = Query("APT")):
    g, paths, proc = run_attack(scenario)
    best = paths[0] if paths else None
    res = {
        "best_path": None if best is None else {
            "nodes": best.nodes,
            "score": best.score,
            "confidence": best.confidence,
            "explanation": best.explanation,
            "edges": [vars(e) for e in best.edges],
        },
        "processor": {
            "dropped_duplicates": proc.dropped_duplicates,
            "late_events": proc.late_events,
        },
        "graph": g.export(),
        "events": [vars(e) for e in g.events]
    }
    return enrich_response(res, best, g)

@app.get("/api/resilience")
def resilience(loss: float=Query(0.2, ge=0, le=0.8), delay: float=Query(4, ge=0, le=20), duplicate: float=Query(0.1, ge=0, le=0.8), scenario: str = Query("APT")):
    if scenario == "APT":
        scenario = "4"
    elif scenario == "INSIDER":
        scenario = "2"
    elif scenario == "RANSOMWARE":
        scenario = "3"
        
    if scenario == "1":
        from scenarios.judge_scenarios import JudgeScenarios
        scenario_data = JudgeScenarios().invisible_employee()
    elif scenario == "2":
        from scenarios.judge_scenarios import JudgeScenarios
        scenario_data = JudgeScenarios().silent_insider()
    elif scenario == "3":
        from scenarios.judge_scenarios import JudgeScenarios
        scenario_data = JudgeScenarios().ransomware_sprint()
    elif scenario == "4":
        from scenarios.judge_scenarios import JudgeScenarios
        scenario_data = JudgeScenarios().apt_ghost_campaign()
    else:
        scenario_data = sim.generate_scenario("legacy")

    events = sim.perturb_stream(scenario_data, loss, delay, duplicate)
    ready, proc = process_events(events, reorder_window=max(5, delay+2))
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
    recon = AttackReconstructor(time_window=120, max_depth=6)
    
    seed, target = "D-007", "D-999"
    if scenario == "2":
        seed, target = "D-010", "S-01"
    elif scenario == "3":
        seed, target = "D-050", "S-02"
    elif scenario == "4":
        seed, target = "D-007", "D-999"
    elif scenario == "1":
        seed, target = "D-015", "S-01"
        
    paths = recon.reconstruct(g, seed, target)
    best = paths[0] if paths else None
    res = {
        "input": {"missing":loss,"delay":delay,"duplicate":duplicate},
        "accepted_events": len(ready),
        "duplicates_removed": proc.dropped_duplicates,
        "late_events": proc.late_events,
        "path_found": best is not None,
        "confidence": None if best is None else best.confidence,
        "score": None if best is None else best.score,
        "nodes": None if best is None else best.nodes,
        "best_path": None if best is None else {
            "nodes": best.nodes,
            "score": best.score,
            "confidence": best.confidence,
            "explanation": best.explanation,
            "edges": [vars(e) for e in best.edges],
        },
        "processor": {
            "dropped_duplicates": proc.dropped_duplicates,
            "late_events": proc.late_events,
        },
        "graph": g.export(),
        "events": [vars(e) for e in g.events]
    }
    return enrich_response(res, best, g)

@app.get("/api/benchmark")
def benchmark():
    # Deterministic illustrative local benchmark run. For competition claims,
    # rerun this harness repeatedly and record output artifacts.
    cases=[("clean",0,0,0),("missing_10",.10,0,0),("missing_20",.20,0,0),("delayed",0,8,0),("duplicates",0,0,.2)]
    rows=[]
    for name, loss, delay, dup in cases:
        events=sim.mixed_scenario(loss, delay, dup)
        ready,_=process_events(events, reorder_window=max(8,delay+2))
        g=DynamicSecurityGraph()
        for e in ready: g.apply(e)
        paths=AttackReconstructor().reconstruct(g,"D-007","D-999")
        best=paths[0] if paths else None
        rows.append({"scenario":name,"events":len(ready),"path_found":bool(best),
                     "score":None if best is None else best.score,
                     "confidence":None if best is None else best.confidence})
    return {"rows":rows}

