# Anticipated Judge Questions

**Q1: Why not just use an LLM (like GPT-4) to reconstruct the attacks?**
**A1:** Hallucinations. An LLM might invent a network hop that doesn't exist, which is unacceptable in an enterprise SOC. Our `AttackReconstructor` is 100% deterministic and rule-based. We only use AI/LLMs for summarization, not for the core detection math.

**Q2: How does the system handle missing logs?**
**A2:** That is our core innovation. Our `AttackReconstructor` uses a bounded BFS graph search with a configurable `max_inferred_gaps`. It uses spatial topology (e.g., floor numbers) and network segmentation to logically deduce where an attacker must have traveled, even if the logs were deleted.

**Q3: How scalable is this?**
**A3:** Extremely. Our `EventProcessor` prunes and deduplicates raw telemetry before it hits the graph. As you saw in the benchmarks, processing and reconstructing a scenario takes less than 10 milliseconds.

**Q4: Is the dashboard real or mocked?**
**A4:** The Command Center dashboard connects directly to our backend engine outputs. While the 3D Spline visualization provides a fallback, the core UI is fully functional Vanilla JS rendering live JSON data.
