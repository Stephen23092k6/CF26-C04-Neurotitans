# Final Demo Script: 5-Minute Judge Demonstration

**Presenter**: "Welcome to Neurobrain X, the Enterprise Autonomous SOC."

## 1. Show Attack Simulation (0:00 - 1:00)
- "Traditional SIEMs generate hundreds of isolated alerts. Today, we'll simulate a complex APT campaign involving credential theft, lateral movement, and defense evasion."
- *Action*: Run the ThreatSimulator or point to the ingested telemetry.
- "Notice how the events are disparate. A human would take hours to correlate this."

## 2. Show Reconstruction (1:00 - 2:00)
- "Neurobrain X ingests this into our Dynamic Security Graph. Using deterministic rules—temporal, spatial, and identity continuity—it reconstructs the exact attack path."
- *Action*: Show the AttackReconstructor output, highlighting an `INFERRED_GAP` where telemetry was missing.
- "We don't need perfect telemetry. Our engine infers logical steps just like a seasoned analyst would."

## 3. Show Explanation (2:00 - 3:00)
- "But a graph isn't enough. We need explainability."
- *Action*: Show the SOC Copilot and the generated narrative.
- "Our Explanation Layer translates the graph into a human-readable story and maps it directly to the MITRE ATT&CK framework."

## 4. Show Prediction (3:00 - 4:00)
- "Now for the enterprise intelligence layer. What is the attacker going to do next?"
- *Action*: Point to the Threat Prediction panel on the dashboard.
- "By cross-referencing the current MITRE techniques with our Security Memory of past incidents, Neurobrain X deterministically predicts the next moves—in this case, Privilege Escalation—with 90% confidence."

## 5. Show Automated Response (4:00 - 5:00)
- "Finally, how do we stop it?"
- *Action*: Show the Automated Playbook Viewer.
- "Neurobrain X generates an automated, step-by-step incident response playbook tailored to the exact risk level and attack pattern. It bridges the gap between detection and response, autonomously."
- "Neurobrain X: The explainable, deterministic, autonomous SOC."
