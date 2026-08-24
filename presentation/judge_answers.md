# Judge Q&A Cheat Sheet

**Q: Why not just use an LLM for everything?**
**A**: LLMs are great for summarization, but they hallucinate. In enterprise security, if you isolate a critical database server or terminate a CEO's session, you need 100% auditability. Neurobrain X uses a deterministic graph engine to reconstruct the path and calculate risk. We only use LLM-like structures to format the final narrative (SOC Copilot), ensuring the core reasoning remains mathematically sound and explainable.

**Q: How do you handle VPN attackers or identity spoofing?**
**A**: This is solved by our Identity Continuity Layer. If an attacker steals credentials and logs in from a new VPN IP, traditional SIEMs see this as a disjointed event. Neurobrain X tracks the temporal proximity and spatial discontinuity, applying a "continuity penalty." This flags the identity transition as an anomaly and connects the nodes via an inferred gap.

**Q: What happens with missing telemetry?**
**A**: Perfect telemetry doesn't exist in the real world. Our `AttackReconstructor` algorithm specifically allows for a configurable number of `max_inferred_gaps`. If telemetry drops, the engine evaluates the temporal proximity, network topology, and identity continuity of the surrounding events. If the plausibility score meets the threshold, it bridges the gap explicitly, labeling it as inferred so analysts know exactly where data was missing.

**Q: How is this different from a standard SIEM?**
**A**: A SIEM gives you alerts. Neurobrain X gives you the story, the prediction, and the playbook. SIEMs require analysts to query data manually to build an incident report. Neurobrain X autonomously builds the attack graph, translates it into English, maps it to MITRE, predicts the next move, and drafts the response playbook instantaneously.

**Q: How does it scale?**
**A**: Because Neurobrain X is not performing deep neural network inferences, it scales beautifully. Graph traversal is limited by `max_depth` and `time_window`, meaning the algorithm performs locally around an alert cluster in O(N) time, rather than querying the entire data lake. It is designed to run synchronously on event ingestion streams.
