
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

app = FastAPI(title="Neurobrain X", version="0.2.0")
app.mount("/ui", StaticFiles(directory=str(ROOT/"frontend"), html=True), name="ui")

sim = get_legacy_sim()
processor_events, processor = process_events(sim.normal_events(120))
for e in processor_events:
    sim.graph.apply(e)

def run_attack():
    attack_events = sim.attack_scenario()
    ready, proc = process_events(attack_events, reorder_window=8)
    g = DynamicSecurityGraph()
    for e in processor_events + ready:
        g.apply(e)
    recon = AttackReconstructor(time_window=120, max_depth=6)
    # choose D-007 as seed and D-999 as target
    paths = recon.reconstruct(g, "D-007", "D-999")
    return g, paths, proc

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
def incident():
    g, paths, proc = run_attack()
    best = paths[0] if paths else None
    return {
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

@app.get("/api/resilience")
def resilience(loss: float=Query(0.2, ge=0, le=0.8), delay: float=Query(4, ge=0, le=20), duplicate: float=Query(0.1, ge=0, le=0.8)):
    events = sim.mixed_scenario(loss, delay, duplicate)
    ready, proc = process_events(events, reorder_window=max(5, delay+2))
    g = DynamicSecurityGraph()
    for e in ready:
        g.apply(e)
    recon = AttackReconstructor(time_window=120, max_depth=6)
    paths = recon.reconstruct(g, "D-007", "D-999")
    best = paths[0] if paths else None
    return {
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
