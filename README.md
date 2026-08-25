# Neurobrain X

## Autonomous Spatial Cyber Threat Reconstruction and Defense Intelligence

> **Reconstruct the attack. Explain the evidence. Support the response.**

Neurobrain X is a deterministic cybersecurity research prototype developed for **C-04: Spatial Cyber Threat Reconstruction Engine**.

The platform reconstructs plausible cyberattack paths across **time, device identity, network topology, physical location, and authentication context**, including scenarios where telemetry is incomplete, delayed, duplicated, or otherwise degraded.

---

## Overview

Modern security environments produce large volumes of isolated events:

```text
Authentication
     |
Device Activity
     |
Network Transition
     |
Lateral Movement
     |
Critical Asset Access
```

The difficult problem is not detecting an individual event.

The difficult problem is determining:

> **How did these events form a coherent attack, and how confident are we in that reconstruction?**

Neurobrain X addresses this problem through an evidence-driven security graph and deterministic attack-path reconstruction.

---

## Core Architecture

```text
Security Telemetry
        |
        v
Event Processing
        |
        v
Dynamic Security Graph
        |
        v
Temporal + Spatial + Network + Identity Reasoning
        |
        v
Attack Reconstruction
        |
        +------------------+
        |                  |
        v                  v
   Explanation          Investigation
        |
        +----------+-----------+
        |          |           |
        v          v           v
      MITRE      Risk      Hypotheses
        |
        +----------+-----------+
                   |
                   v
       Prediction / SOC Copilot
                   |
                   v
          Response Playbooks
```

The frontend visualizes these results but does not make the underlying security decisions.

---

## Core Capabilities

### Dynamic Security Graph

Represents relationships among:

* users
* devices
* endpoints
* servers
* databases
* network segments
* physical locations
* security events

### Attack Reconstruction

Reconstructs plausible paths from an attack seed to a target using contextual evidence.

### Identity Continuity

Treats identity as contextual rather than relying solely on IP addresses.

Signals can include:

* user identity
* device context
* session continuity
* network changes
* physical location
* temporal consistency
* contradictory evidence

### Incomplete Telemetry Reasoning

Supports controlled degradation involving:

* missing events
* delayed events
* duplicated events
* out-of-order events
* network-origin changes
* identity manipulation

### Explainability

Separates:

```text
Observed Evidence
        from
Inferred Relationships
```

The system does not silently convert an inference into an observed event.

### MITRE ATT&CK Mapping

Maps reconstructed behavior to techniques such as:

| Technique | Description                       |
| --------- | --------------------------------- |
| T1078     | Valid Accounts                    |
| T1021     | Remote Services                   |
| T1059     | Command and Scripting Interpreter |
| T1003     | OS Credential Dumping             |

### Risk Assessment

Produces:

* risk score
* severity
* evidence-based confidence/context

### Threat Prediction

Ranks plausible next attacker actions using deterministic rules and available historical context.

### SOC Copilot

Produces structured analyst information covering:

* what happened
* why it was detected
* attack summary
* recommended questions
* next actions

### Response and Playbooks

Generates simulated containment actions such as:

* endpoint isolation
* account/session disablement
* credential reset
* evidence collection

### Enterprise Context

Associates security events with:

* asset criticality
* department
* asset type
* enterprise context

---

## Identity Continuity

A central design principle is:

> **IP address is not identity.**

An attacker can rotate:

```text
IP
VPN endpoint
Network
Proxy
```

without necessarily changing the underlying device or user context.

Conversely, valid credentials may appear on:

```text
unexpected device
unexpected location
unexpected network
```

and create an identity anomaly.

Neurobrain X evaluates identity using contextual evidence rather than treating a single network attribute as authoritative.

---

## Evidence and Uncertainty

Example:

```text
Observed
A --------> B

Inferred
B - - - - -> C

Observed
C --------> D
```

The inferred relationship is treated differently from observed evidence.

This allows the system to remain useful when telemetry is missing without pretending that missing evidence was actually observed.

---

## Threat Scenarios

| Scenario | Description        |
| -------- | ------------------ |
| 1        | Invisible Employee |
| 2        | Silent Insider     |
| 3        | Ransomware Sprint  |
| 4        | APT Ghost Campaign |

The project also contains adversarial identity scenarios covering conditions such as VPN rotation, IP churn, stolen credentials, and identity spoofing.

All scenarios are software simulations rather than real-world intrusion activity.

---

## Technology Stack

| Layer            | Technology                       |
| ---------------- | -------------------------------- |
| Core Engine      | Python                           |
| API              | FastAPI                          |
| Graph Reasoning  | Dynamic Security Graph           |
| Frontend         | HTML, CSS, Vanilla JavaScript    |
| 3D Visualization | Spline                           |
| Testing          | Pytest                           |
| Intelligence     | Deterministic rule-based engines |

The security-critical reasoning path does not depend on an external ML or LLM service.

---

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the platform

```bash
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
```

### Open the Command Center

```text
http://127.0.0.1:8000/ui/
```

### Run the command-line judge demonstration

```bash
python demo/judge_mode.py 4
```

Scenario mapping:

```text
1 = Invisible Employee
2 = Silent Insider
3 = Ransomware Sprint
4 = APT Ghost Campaign
```

### Run the autonomous SOC pipeline

```bash
python demo/run_autonomous_soc.py 4
```

---

## Validation

The project includes automated tests for:

* attack reconstruction
* identity continuity
* adversarial scenarios
* explanation
* MITRE mapping
* risk assessment
* SOC intelligence
* response planning
* enterprise intelligence
* dashboard/backend dataflow
* regression behavior

Current validated project state:

```text
60 tests passed
```

Additional experiments cover telemetry degradation, identity manipulation, scenario switching, and deterministic backend-to-frontend dataflow.

Benchmark values are workload-specific prototype measurements and should not be interpreted as production performance guarantees.

---

## Data and Evaluation

Neurobrain X uses **self-generated synthetic telemetry**.

This is intentional: C-04 defines a simulated software-only environment. The simulator provides controlled ground truth so attack reconstruction can be evaluated against known attack seeds and targets.

Synthetic data represents:

* users
* endpoints
* servers
* databases
* network segments
* physical locations
* authentication events
* device activity
* network activity
* attack transitions
* telemetry degradation

The evaluation strategy focuses on reconstruction quality, resilience, identity continuity, explainability, and end-to-end system behavior.

---

## Frontend

The Command Center provides:

* attack graph visualization
* incident timeline
* risk assessment
* MITRE ATT&CK mapping
* threat prediction
* SOC Copilot
* response/playbook output
* attack replay visualization

The frontend is a presentation and interaction layer. Security decisions remain backend-owned.

---

## Limitations

Neurobrain X is a **research and hackathon prototype**, not a production SOC platform.

Current limitations include:

* synthetic rather than real enterprise telemetry
* simulated attack behavior
* simulated response execution
* prototype-scale graph processing
* limited production persistence and integrations
* no guarantee of real-world detection accuracy
* no direct production firewall or EDR enforcement

A production implementation would require durable storage, streaming telemetry connectors, distributed graph processing, enterprise identity integration, and controlled SOAR integration.

---

## Future Work

Potential next steps include:

* real SIEM and EDR connectors
* streaming event ingestion
* durable event storage
* distributed graph processing
* enterprise identity provider integration
* STIX/TAXII integration
* production SOAR integration
* large-scale distributed benchmarking
* expanded spatial reasoning
* optional ML-assisted ranking while preserving deterministic security controls

---

## AI-Assisted Development Disclosure

AI-assisted development was used during the project for:

* code generation
* debugging
* test generation
* documentation
* architecture exploration
* design exploration

The team remains responsible for:

* architecture
* correctness
* security behavior
* validation
* benchmark interpretation
* technical claims
* final implementation

The security-critical reasoning in Neurobrain X is intentionally deterministic.

---

## Hackathon Context

**Track:** Intelligent Systems — Cybersecurity & Digital Trust

**Challenge:** C-04 — Spatial Cyber Threat Reconstruction Engine

Neurobrain X focuses on the challenge requirements around:

* temporal correlation
* explicit device identity
* network relationships
* physical location
* incomplete telemetry
* attack-path reconstruction
* lateral-movement reasoning
* explainability
* resilience to telemetry loss

---

## Final Perspective

Traditional security workflows often answer:

> **What alert happened?**

Neurobrain X is designed to answer:

> **How did the attack plausibly evolve, what evidence supports that interpretation, how confident are we, and what should the SOC do next?**

### Observe → Reconstruct → Explain → Prioritize → Predict → Defend
