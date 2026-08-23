# Live Demo Script

**Step 1: The Command Center Interface**
- "Welcome to the Neurobrain X Command Center."
- Show the standalone dashboard.
- "We are going to simulate 4 different attacker profiles today."

**Step 2: APT Ghost Campaign**
- Run `python demo/final_showcase.py 4` in the terminal.
- "Notice how the engine processes the events in under 5 milliseconds."
- "The SOC Copilot immediately answers the three critical questions: Why it was flagged, What happened, and What to do next."

**Step 3: Identity Layer Deep Dive**
- Run `python demo/final_showcase.py 1` (Invisible Employee).
- "Here, an attacker tried to use stolen credentials. Our Identity Layer detected the geographic anomaly and instantly downgraded confidence in the session, escalating the risk to Critical."

**Step 4: Automated Response**
- "Finally, notice the Response Engine. Because it mapped the behavior to MITRE T1078, it didn't just tell us to 'investigate'—it automatically drafted a plan to isolate the endpoint and force a credential reset."
