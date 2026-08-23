# Phase 4B Adversarial Validation Report

## Methodology
Scenarios S10-S13 run specifically against identity-centric attacks, evaluating Neurobrain X with and without the Identity Continuity Layer.

## Model Comparison Table
| Scenario | Model | Target Reached | Struct Valid | Completeness | Jaccard | FPR | Score | Confidence | Late Events |
|---|---|---|---|---|---|---|---|---|---|
| S0-Clean | NeurobrainX (No Identity) | 1.00 | 1.00 | 1.00 | 0.99 | 0.00 | 100.0 | 85.8 | 0.0 |
| S0-Clean | NeurobrainX (With Identity) | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 100.0 | 98.8 | 0.0 |
| S1-Loss-Low | NeurobrainX (No Identity) | 0.75 | 0.65 | 0.81 | 0.80 | 0.00 | 76.4 | 73.2 | 0.0 |
| S1-Loss-Low | NeurobrainX (With Identity) | 0.75 | 0.65 | 0.81 | 0.81 | 0.00 | 80.1 | 85.3 | 0.0 |
| S2-Loss-Med | NeurobrainX (No Identity) | 0.80 | 0.55 | 0.79 | 0.79 | 0.00 | 77.6 | 76.6 | 0.0 |
| S2-Loss-Med | NeurobrainX (With Identity) | 0.80 | 0.55 | 0.79 | 0.79 | 0.00 | 84.3 | 90.7 | 0.0 |
| S3-Loss-High | NeurobrainX (No Identity) | 0.45 | 0.25 | 0.55 | 0.55 | 0.00 | 48.3 | 55.1 | 0.0 |
| S3-Loss-High | NeurobrainX (With Identity) | 0.45 | 0.25 | 0.55 | 0.55 | 0.00 | 56.5 | 67.0 | 0.0 |
| S4-Jitter-Low | NeurobrainX (No Identity) | 1.00 | 1.00 | 1.00 | 0.98 | 0.00 | 100.0 | 86.3 | 0.0 |
| S4-Jitter-Low | NeurobrainX (With Identity) | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 100.0 | 98.8 | 0.0 |
| S5-Jitter-High | NeurobrainX (No Identity) | 1.00 | 1.00 | 1.00 | 0.98 | 0.00 | 100.0 | 86.4 | 64.2 |
| S5-Jitter-High | NeurobrainX (With Identity) | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 100.0 | 98.0 | 64.2 |
| S6-Dup-Storm | NeurobrainX (No Identity) | 1.00 | 1.00 | 1.00 | 0.98 | 0.00 | 100.0 | 86.0 | 0.0 |
| S6-Dup-Storm | NeurobrainX (With Identity) | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 100.0 | 100.0 | 0.0 |
| S7-Compound-A | NeurobrainX (No Identity) | 0.75 | 0.40 | 0.70 | 0.69 | 0.00 | 72.2 | 75.1 | 0.0 |
| S7-Compound-A | NeurobrainX (With Identity) | 0.75 | 0.40 | 0.70 | 0.69 | 0.00 | 81.2 | 89.3 | 0.0 |
| S8-Compound-B | NeurobrainX (No Identity) | 0.40 | 0.30 | 0.50 | 0.49 | 0.00 | 43.8 | 49.8 | 28.6 |
| S8-Compound-B | NeurobrainX (With Identity) | 0.40 | 0.30 | 0.50 | 0.49 | 0.00 | 49.1 | 58.4 | 28.6 |
| S9-Multi-Path | NeurobrainX (No Identity) | 1.00 | 0.95 | 0.70 | 0.70 | 0.00 | 93.0 | 80.1 | 0.0 |
| S9-Multi-Path | NeurobrainX (With Identity) | 1.00 | 0.95 | 0.70 | 0.70 | 0.00 | 97.9 | 92.9 | 0.0 |
| BENIGN_ANOMALY | NeurobrainX (No Identity) | 0.00 | 0.00 | 0.00 | 0.45 | 0.00 | 10.6 | 32.7 | 0.0 |
| BENIGN_ANOMALY | NeurobrainX (With Identity) | 0.00 | 0.00 | 0.00 | 0.45 | 0.00 | 18.9 | 40.9 | 0.0 |
| PARTIAL_FLOOR_LOSS | NeurobrainX (No Identity) | 0.30 | 0.00 | 0.19 | 0.18 | 0.00 | 24.0 | 31.1 | 0.0 |
| PARTIAL_FLOOR_LOSS | NeurobrainX (With Identity) | 0.30 | 0.00 | 0.19 | 0.18 | 0.00 | 30.8 | 37.8 | 0.0 |
| S10-VPN-Rotation | NeurobrainX (No Identity) | 1.00 | 1.00 | 0.67 | 0.67 | 0.00 | 80.2 | 72.2 | 0.0 |
| S10-VPN-Rotation | NeurobrainX (With Identity) | 1.00 | 1.00 | 0.67 | 0.67 | 0.00 | 99.5 | 98.3 | 0.0 |
| S11-IP-Churn | NeurobrainX (No Identity) | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 75.5 | 75.5 | 0.0 |
| S11-IP-Churn | NeurobrainX (With Identity) | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 90.5 | 90.5 | 0.0 |
| S12-Stolen-Creds | NeurobrainX (No Identity) | 0.25 | 0.25 | 0.42 | 0.35 | 0.00 | 30.2 | 61.9 | 0.0 |
| S12-Stolen-Creds | NeurobrainX (With Identity) | 0.25 | 0.25 | 0.42 | 0.35 | 0.00 | 56.4 | 88.2 | 0.0 |
| S13-Identity-Spoof | NeurobrainX (No Identity) | 1.00 | 1.00 | 0.67 | 0.67 | 0.00 | 82.3 | 72.3 | 0.0 |
| S13-Identity-Spoof | NeurobrainX (With Identity) | 0.00 | 0.00 | 0.33 | 0.25 | 0.00 | 58.0 | 93.0 | 0.0 |

## Identity Attack Resilience Score
Resilience Score is computed as the relative performance preservation (or correct rejection) in S10-S13 when the Identity Layer is active compared to inactive.
- **S10-VPN-Rotation**: Confidence shifted from 72.2 -> 98.3. 
- **S11-IP-Churn**: Confidence shifted from 75.5 -> 90.5. 
- **S12-Stolen-Creds**: Confidence shifted from 61.9 -> 88.2. 
- **S13-Identity-Spoof**: Confidence shifted from 72.3 -> 93.0. 
