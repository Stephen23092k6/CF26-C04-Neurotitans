
from pathlib import Path
import sys, json, statistics
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.simulator import BuildingSimulator, process_events
from app.engine import DynamicSecurityGraph, AttackReconstructor

sim=BuildingSimulator()
cases=[
    ("clean",0,0,0),
    ("missing_10",.10,0,0),
    ("missing_20",.20,0,0),
    ("delayed_8",0,8,0),
    ("duplicate_20",0,0,.20),
]
rows=[]
for name,loss,delay,dup in cases:
    events=sim.mixed_scenario(loss,delay,dup)
    ready,proc=process_events(events,reorder_window=max(8,delay+2))
    g=DynamicSecurityGraph()
    for e in ready:g.apply(e)
    paths=AttackReconstructor().reconstruct(g,"D-007","D-999")
    best=paths[0] if paths else None
    rows.append({
        "scenario":name,
        "input_events":len(events),
        "accepted_events":len(ready),
        "duplicates_removed":proc.dropped_duplicates,
        "late_events":proc.late_events,
        "path_found":bool(best),
        "score":None if not best else best.score,
        "confidence":None if not best else best.confidence,
    })

out=Path(__file__).with_name("results.json")
out.write_text(json.dumps(rows,indent=2),encoding="utf-8")
print(json.dumps(rows,indent=2))
