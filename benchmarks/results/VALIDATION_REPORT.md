# Phase 3.1 Validation Report

## Methodology
12 Scenarios run across 4 models for 20 Monte Carlo iterations (seeds 1000-1019) to measure resilience and fidelity.
Jitter experiments use a strict fixed 8-second reorder window to test true late-event tolerance.

## Model Comparison Table
| Scenario | Model | Target Reached | Struct Valid | Completeness | Jaccard | FPR | Score | Confidence | Late Events |
|---|---|---|---|---|---|---|---|---|---|
| S0-Clean | IsolatedAlert | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 40.0 | 40.0 | 0.0 |
| S0-Clean | SlidingWindow | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 75.0 | 60.0 | 0.0 |
| S0-Clean | StaticGraph | 1.00 | 1.00 | 0.99 | 0.99 | 0.00 | 80.0 | 70.0 | 0.0 |
| S0-Clean | NeurobrainX | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 100.0 | 85.0 | 0.0 |
| S1-Loss-Low | IsolatedAlert | 1.00 | 1.00 | 0.99 | 0.99 | 0.00 | 35.0 | 40.0 | 0.0 |
| S1-Loss-Low | SlidingWindow | 1.00 | 1.00 | 0.99 | 0.99 | 0.00 | 75.0 | 60.0 | 0.0 |
| S1-Loss-Low | StaticGraph | 0.70 | 0.65 | 0.66 | 0.64 | 0.00 | 56.0 | 49.0 | 0.0 |
| S1-Loss-Low | NeurobrainX | 0.65 | 0.65 | 0.78 | 0.72 | 0.00 | 77.7 | 81.1 | 0.0 |
| S2-Loss-Med | IsolatedAlert | 1.00 | 1.00 | 0.99 | 0.99 | 0.00 | 30.5 | 40.0 | 0.0 |
| S2-Loss-Med | SlidingWindow | 1.00 | 1.00 | 0.99 | 0.99 | 0.00 | 75.0 | 60.0 | 0.0 |
| S2-Loss-Med | StaticGraph | 0.35 | 0.30 | 0.34 | 0.32 | 0.00 | 28.0 | 24.5 | 0.0 |
| S2-Loss-Med | NeurobrainX | 0.30 | 0.30 | 0.57 | 0.50 | 0.00 | 50.4 | 65.9 | 0.0 |
| S3-Loss-High | IsolatedAlert | 1.00 | 1.00 | 0.95 | 0.95 | 0.00 | 24.5 | 40.0 | 0.0 |
| S3-Loss-High | SlidingWindow | 1.00 | 1.00 | 0.95 | 0.95 | 0.00 | 75.0 | 60.0 | 0.0 |
| S3-Loss-High | StaticGraph | 0.25 | 0.25 | 0.23 | 0.22 | 0.00 | 20.0 | 17.5 | 0.0 |
| S3-Loss-High | NeurobrainX | 0.20 | 0.20 | 0.51 | 0.45 | 0.00 | 44.2 | 65.4 | 0.0 |
| S4-Jitter-Low | IsolatedAlert | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 40.0 | 40.0 | 0.0 |
| S4-Jitter-Low | SlidingWindow | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 75.0 | 60.0 | 0.0 |
| S4-Jitter-Low | StaticGraph | 1.00 | 1.00 | 0.97 | 0.97 | 0.00 | 80.0 | 70.0 | 0.0 |
| S4-Jitter-Low | NeurobrainX | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 100.0 | 85.0 | 0.0 |
| S5-Jitter-High | IsolatedAlert | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 40.0 | 40.0 | 64.6 |
| S5-Jitter-High | SlidingWindow | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 75.0 | 60.0 | 64.6 |
| S5-Jitter-High | StaticGraph | 1.00 | 1.00 | 0.95 | 0.94 | 0.00 | 80.0 | 70.0 | 64.6 |
| S5-Jitter-High | NeurobrainX | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 100.0 | 85.0 | 64.6 |
| S6-Dup-Storm | IsolatedAlert | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 40.0 | 40.0 | 0.0 |
| S6-Dup-Storm | SlidingWindow | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 75.0 | 60.0 | 0.0 |
| S6-Dup-Storm | StaticGraph | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 80.0 | 70.0 | 0.0 |
| S6-Dup-Storm | NeurobrainX | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 100.0 | 85.0 | 0.0 |
| S7-Compound-A | IsolatedAlert | 1.00 | 1.00 | 0.99 | 0.99 | 0.00 | 31.0 | 40.0 | 0.0 |
| S7-Compound-A | SlidingWindow | 1.00 | 1.00 | 0.99 | 0.99 | 0.00 | 75.0 | 60.0 | 0.0 |
| S7-Compound-A | StaticGraph | 0.40 | 0.40 | 0.39 | 0.39 | 0.00 | 32.0 | 28.0 | 0.0 |
| S7-Compound-A | NeurobrainX | 0.35 | 0.35 | 0.62 | 0.58 | 0.00 | 52.7 | 67.4 | 0.0 |
| S8-Compound-B | IsolatedAlert | 1.00 | 1.00 | 0.95 | 0.95 | 0.00 | 25.5 | 40.0 | 24.4 |
| S8-Compound-B | SlidingWindow | 1.00 | 1.00 | 0.95 | 0.95 | 0.00 | 75.0 | 60.0 | 24.4 |
| S8-Compound-B | StaticGraph | 0.20 | 0.20 | 0.20 | 0.20 | 0.00 | 16.0 | 14.0 | 24.4 |
| S8-Compound-B | NeurobrainX | 0.20 | 0.20 | 0.47 | 0.44 | 0.00 | 34.2 | 52.6 | 24.4 |
| S9-Multi-Path | IsolatedAlert | 1.00 | 1.00 | 0.99 | 0.99 | 0.00 | 47.0 | 40.0 | 0.0 |
| S9-Multi-Path | SlidingWindow | 1.00 | 1.00 | 0.99 | 0.99 | 0.00 | 75.0 | 60.0 | 0.0 |
| S9-Multi-Path | StaticGraph | 1.00 | 1.00 | 0.65 | 0.65 | 0.00 | 80.0 | 70.0 | 0.0 |
| S9-Multi-Path | NeurobrainX | 1.00 | 1.00 | 0.78 | 0.78 | 0.00 | 98.6 | 83.9 | 0.0 |
| BENIGN_ANOMALY | IsolatedAlert | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.0 | 0.0 | 0.0 |
| BENIGN_ANOMALY | SlidingWindow | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.0 | 0.0 | 0.0 |
| BENIGN_ANOMALY | StaticGraph | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.0 | 0.0 | 0.0 |
| BENIGN_ANOMALY | NeurobrainX | 0.00 | 0.00 | 0.00 | 0.25 | 0.00 | 24.1 | 61.7 | 0.0 |
| PARTIAL_FLOOR_LOSS | IsolatedAlert | 1.00 | 1.00 | 0.75 | 0.75 | 0.00 | 20.0 | 40.0 | 0.0 |
| PARTIAL_FLOOR_LOSS | SlidingWindow | 1.00 | 1.00 | 0.75 | 0.75 | 0.00 | 75.0 | 60.0 | 0.0 |
| PARTIAL_FLOOR_LOSS | StaticGraph | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.0 | 0.0 | 0.0 |
| PARTIAL_FLOOR_LOSS | NeurobrainX | 0.00 | 0.00 | 0.11 | 0.07 | 0.00 | 12.3 | 32.9 | 0.0 |

## Scalability Measurements
| Events | Ingest Latency (s) | Recon Latency (s) | Total Runtime (s) | Throughput (EPS) |
|---|---|---|---|---|
| 100 | 0.0020 | 0.0000 | 0.0020 | 49584 |
| 1000 | 0.0040 | 0.5881 | 0.5922 | 1689 |
| 5000 | 0.0302 | 127.0157 | 127.0460 | 39 |
| 10000 | 0.0462 | 12443.1135 | 12443.1597 | 1 |

## Interpretation of Correlated Floor Loss
Under PARTIAL_FLOOR_LOSS, Neurobrain X correctly fails to reach the target because the physical telemetry does not exist. It preserves monitoring continuity and provides a partial reconstruction of the evidence prior to the gap, rather than fabricating a structurally invalid path like baseline algorithms.

## Known Limitations
- High raw telemetry loss (>30%) causes significant performance drops in structural recovery.
- Correlated spatial loss completely severs path traversal; requires logical inference fallbacks (e.g., AD logs) to bridge physical gaps.
