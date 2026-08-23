
# Neurobrain X — 12-Hour Prototype Architecture

```text
Synthetic Building Simulator
        ↓
Event Ingestion
        ↓
Validation / Dedup / Bounded Reordering
        ↓
Dynamic Security Graph
        ↓
Temporal + Spatial Correlation
        ↓
Candidate Attack-Path Search
        ↓
Evidence-Based Threat Score + Confidence
        ↓
Explainable Incident View
        ↓
Resilience + Validation Lab
```

## Why this is credible
C-04 explicitly requires a simulated multi-floor environment, explicit device/network/location representation, temporal relationships, attack-path reconstruction, explainability, and resilience under imperfect telemetry.

## Production evolution
- Kafka/Redpanda for stream ingestion
- Neo4j or another graph store
- FastAPI services
- React/TypeScript SOC
- OpenTelemetry metrics
- RBAC/audit
- event provenance
- horizontal workers

## Core safety
No live network access. No intrusion/scanning. All attack scenarios are synthetic.
