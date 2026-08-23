import sys, json, time, csv, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.simulator import BuildingSimulator, process_events
from app.engine import DynamicSecurityGraph, AttackReconstructor
from app.baselines import IsolatedAlertBaseline, SlidingWindowBaseline, StaticGraphBaseline
from app.adversary import IdentityAdversarySimulator

SCENARIOS = {
    "S0-Clean":          {"missing": 0.0, "delayed": 0.0, "duplicate": 0.0, "is_benign": False},
    "S1-Loss-Low":       {"missing": 0.1, "delayed": 0.0, "duplicate": 0.0, "is_benign": False},
    "S2-Loss-Med":       {"missing": 0.2, "delayed": 0.0, "duplicate": 0.0, "is_benign": False},
    "S3-Loss-High":      {"missing": 0.4, "delayed": 0.0, "duplicate": 0.0, "is_benign": False},
    "S4-Jitter-Low":     {"missing": 0.0, "delayed": 4.0, "duplicate": 0.0, "is_benign": False},
    "S5-Jitter-High":    {"missing": 0.0, "delayed": 12.0, "duplicate": 0.0, "is_benign": False},
    "S6-Dup-Storm":      {"missing": 0.0, "delayed": 0.0, "duplicate": 0.4, "is_benign": False},
    "S7-Compound-A":     {"missing": 0.15, "delayed": 5.0, "duplicate": 0.1, "is_benign": False},
    "S8-Compound-B":     {"missing": 0.3, "delayed": 10.0, "duplicate": 0.2, "is_benign": False},
    "S9-Multi-Path":     {"missing": 0.1, "delayed": 2.0, "duplicate": 0.0, "is_benign": False, "multi_path": True},
    "BENIGN_ANOMALY":    {"missing": 0.0, "delayed": 0.0, "duplicate": 0.0, "is_benign": True},
    "PARTIAL_FLOOR_LOSS":{"missing": 0.0, "delayed": 0.0, "duplicate": 0.0, "is_benign": False, "floor_loss": 3},
    "S10-VPN-Rotation":  {"missing": 0.0, "delayed": 0.0, "duplicate": 0.0, "is_benign": False, "identity_sim": "vpn"},
    "S11-IP-Churn":      {"missing": 0.0, "delayed": 0.0, "duplicate": 0.0, "is_benign": False, "identity_sim": "churn"},
    "S12-Stolen-Creds":  {"missing": 0.0, "delayed": 0.0, "duplicate": 0.0, "is_benign": False, "identity_sim": "stolen"},
    "S13-Identity-Spoof":{"missing": 0.0, "delayed": 0.0, "duplicate": 0.0, "is_benign": False, "identity_sim": "spoof"},
}

MODELS = {
    "NeurobrainX (No Identity)": AttackReconstructor(use_identity_layer=False),
    "NeurobrainX (With Identity)": AttackReconstructor(use_identity_layer=True)
}

def jaccard(set1, set2):
    s1, s2 = set(set1), set(set2)
    if not s1 and not s2: return 1.0
    return len(s1 & s2) / len(s1 | s2) if len(s1 | s2) > 0 else 0.0

def run_monte_carlo(runs=20, target_guided=True):
    results = []
    
    for run_idx in range(runs):
        seed = 1000 + run_idx
        sim = IdentityAdversarySimulator(config=None)
        sim.rng.seed(seed)
        
        for sc_name, sc_params in SCENARIOS.items():
            idsim = sc_params.get("identity_sim")
            if idsim == "vpn":
                data = sim.simulate_vpn_rotation()
                data.name = sc_name
            elif idsim == "churn":
                data = sim.simulate_ip_churn()
                data.name = sc_name
            elif idsim == "stolen":
                data = sim.simulate_stolen_credential()
                data.name = sc_name
            elif idsim == "spoof":
                data = sim.simulate_identity_spoofing()
                data.name = sc_name
            else:
                data = sim.generate_scenario(sc_name, is_benign=sc_params.get("is_benign", False), 
                                             multi_path=sc_params.get("multi_path", False))
            
            p_events = sim.perturb_stream(data, 
                                          missing=sc_params.get("missing", 0.0),
                                          delayed=sc_params.get("delayed", 0.0),
                                          duplicate=sc_params.get("duplicate", 0.0),
                                          floor_loss=sc_params.get("floor_loss"))
            
            t0 = time.time()
            # Fixed 8s reorder window regardless of jitter to test late-event behavior fairly
            ready, proc = process_events(p_events, reorder_window=8.0)
            ingest_latency = time.time() - t0
            
            g = DynamicSecurityGraph()
            for e in ready:
                g.apply(e)
                
            gt_nodes = data.ground_truth["expected_nodes"]
            target = data.ground_truth["target"] if target_guided and data.ground_truth["target"] != "None" else None
            
            for model_name, model in MODELS.items():
                t1 = time.time()
                paths = model.reconstruct(g, data.ground_truth["seed"], target)
                recon_latency = time.time() - t1
                
                best = paths[0] if paths else None
                
                path_nodes = best.nodes if best else []
                target_reached = 1.0 if target and target in path_nodes else 0.0
                jaccard_score = jaccard(path_nodes, gt_nodes)
                
                # Path completeness: ratio of true nodes recovered
                completeness = len(set(path_nodes) & set(gt_nodes)) / len(gt_nodes) if gt_nodes else 0.0
                
                # Structural validity: must hit target, start at seed, and have good fidelity
                structurally_valid = 1.0 if (target_reached and path_nodes and path_nodes[0] == data.ground_truth["seed"] and jaccard_score > 0.5) else 0.0
                
                is_benign = sc_params.get("is_benign", False)
                fpr = 1.0 if is_benign and best and best.score > 50 else 0.0
                
                inferred_gaps = sum(1 for e in best.edges if getattr(e, "is_inferred", False)) if best else 0
                
                results.append({
                    "seed": seed,
                    "scenario": sc_name,
                    "model": model_name,
                    "path_found": bool(best),
                    "target_reached": target_reached,
                    "structurally_valid": structurally_valid,
                    "path_completeness": completeness,
                    "jaccard": jaccard_score,
                    "fpr": fpr,
                    "score": best.score if best else 0.0,
                    "confidence": best.confidence if best else 0.0,
                    "latency": ingest_latency + recon_latency,
                    "inferred_gaps": inferred_gaps,
                    "late_events": proc.late_events,
                    "duplicates_removed": proc.dropped_duplicates
                })
                
    return results

def aggregate(results):
    summary = {}
    for r in results:
        key = (r["scenario"], r["model"])
        if key not in summary:
            summary[key] = {"target": [], "struct_valid": [], "completeness": [], "jaccard": [], "fpr": [], "score": [], "confidence": [], "latency": [], "inferred": [], "late": []}
        summary[key]["target"].append(r["target_reached"])
        summary[key]["struct_valid"].append(r["structurally_valid"])
        summary[key]["completeness"].append(r["path_completeness"])
        summary[key]["jaccard"].append(r["jaccard"])
        summary[key]["fpr"].append(r["fpr"])
        summary[key]["score"].append(r["score"])
        summary[key]["confidence"].append(r["confidence"])
        summary[key]["latency"].append(r["latency"])
        summary[key]["inferred"].append(r["inferred_gaps"])
        summary[key]["late"].append(r["late_events"])
        
    final = []
    for (sc, mod), mets in summary.items():
        final.append({
            "Scenario": sc,
            "Model": mod,
            "Target Reached": statistics.mean(mets["target"]),
            "Struct Valid": statistics.mean(mets["struct_valid"]),
            "Path Completeness": statistics.mean(mets["completeness"]),
            "Jaccard": statistics.mean(mets["jaccard"]),
            "FPR": statistics.mean(mets["fpr"]),
            "Threat Score": statistics.mean(mets["score"]),
            "Confidence": statistics.mean(mets["confidence"]),
            "Latency": statistics.mean(mets["latency"]),
            "Inferred Gaps": statistics.mean(mets["inferred"]),
            "Late Events": statistics.mean(mets["late"])
        })
    return final

def run_scalability_test():
    sizes = [100, 1000, 5000, 10000]
    results = []
    sim = BuildingSimulator()
    for size in sizes:
        events = sim.normal_events(size)
        
        t0 = time.time()
        ready, _ = process_events(events, reorder_window=8.0)
        ingest_time = time.time() - t0
        
        g = DynamicSecurityGraph()
        for e in ready:
            g.apply(e)
            
        t1 = time.time()
        AttackReconstructor().reconstruct(g, "D-001", "D-999")
        recon_time = time.time() - t1
        
        total_time = max(0.001, ingest_time + recon_time)
        throughput = size / total_time
        
        results.append({
            "events": size,
            "ingest_latency_s": ingest_time,
            "recon_latency_s": recon_time,
            "total_runtime_s": total_time,
            "throughput_eps": throughput
        })
    return results

if __name__ == "__main__":
    print("Running Monte Carlo Benchmark (20 runs)...")
    raw_results = run_monte_carlo(20, target_guided=True)
    agg_results = aggregate(raw_results)
    
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    
    with open(out_dir / "raw_results.json", "w") as f:
        json.dump(raw_results, f, indent=2)
        
    with open(out_dir / "aggregated.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=agg_results[0].keys())
        writer.writeheader()
        writer.writerows(agg_results)
        
    print("Running Scalability Benchmark...")
    scale_results = run_scalability_test()
    
    with open(out_dir / "scalability.json", "w") as f:
        json.dump(scale_results, f, indent=2)
        
    print("Generating PHASE_4B_ADVERSARIAL_REPORT.md...")
    md = "# Phase 4B Adversarial Validation Report\n\n"
    md += "## Methodology\nScenarios S10-S13 run specifically against identity-centric attacks, evaluating Neurobrain X with and without the Identity Continuity Layer.\n\n"
    
    md += "## Model Comparison Table\n"
    md += "| Scenario | Model | Target Reached | Struct Valid | Completeness | Jaccard | FPR | Score | Confidence | Late Events |\n"
    md += "|---|---|---|---|---|---|---|---|---|---|\n"
    for r in agg_results:
        md += f"| {r['Scenario']} | {r['Model']} | {r['Target Reached']:.2f} | {r['Struct Valid']:.2f} | {r['Path Completeness']:.2f} | {r['Jaccard']:.2f} | {r['FPR']:.2f} | {r['Threat Score']:.1f} | {r['Confidence']:.1f} | {r['Late Events']:.1f} |\n"
        
    md += "\n## Identity Attack Resilience Score\n"
    md += "Resilience Score is computed as the relative performance preservation (or correct rejection) in S10-S13 when the Identity Layer is active compared to inactive.\n"
    
    # Calculate simple resilience score difference for S10-S13
    resilience_md = ""
    for sc in ["S10-VPN-Rotation", "S11-IP-Churn", "S12-Stolen-Creds", "S13-Identity-Spoof"]:
        no_id = next((r for r in agg_results if r["Scenario"] == sc and "No Identity" in r["Model"]), None)
        with_id = next((r for r in agg_results if r["Scenario"] == sc and "With Identity" in r["Model"]), None)
        if no_id and with_id:
            # We look at confidence primarily for resilience
            resilience_md += f"- **{sc}**: Confidence shifted from {no_id['Confidence']:.1f} -> {with_id['Confidence']:.1f}. \n"
    
    md += resilience_md
    
    with open(out_dir / "PHASE_4B_ADVERSARIAL_REPORT.md", "w") as f:
        f.write(md)
        
    print("Done. Results written to benchmarks/results/")
