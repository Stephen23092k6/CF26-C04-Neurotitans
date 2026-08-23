
# Neurobrain X — Judge Defense Sheet

## Why graph?
Attacks propagate through relationships: user → device → network → server → asset.

## Why temporal?
Ordering and timing distinguish unrelated events from coordinated sequences.

## Why spatial?
C-04 explicitly requires a multi-floor environment and physical-location context.

## Why not a SIEM?
Neurobrain X focuses on reconstructing and explaining candidate attack paths, not only aggregating alerts.

## Why AI?
The core detection/reconstruction path is auditable and deterministic. AI is optional for explanation and analyst interaction.

## What happens with missing telemetry?
Known evidence remains usable; confidence is reduced rather than inventing missing facts.

## How do you validate?
Controlled synthetic attack scenarios against an isolated-event baseline, with reproducible experiments.

## What's the limitation?
This is a prototype-scale simulated environment. Real deployment needs production telemetry contracts, larger-scale benchmarks, stronger detection models, governance and security controls.

## What is novel?
A spatio-temporal graph view that treats incident response as a reconstruction problem under imperfect telemetry.
