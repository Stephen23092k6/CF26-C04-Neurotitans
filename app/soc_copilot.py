class SOCCopilot:
    """
    Deterministic SOC analyst assistant.
    """
    @staticmethod
    def generate_brief(explanation: dict, risk: dict, timeline: list[dict], mitre: list[dict]) -> dict:
        ev = "\n- ".join(explanation.get("evidence", []))
        why = f"Detected via structural path correlation and identity layer anomalies:\n- {ev}" if ev else "Detected via topological path reconstruction."
        
        what = f"An incident spanning {len(timeline)} chronological events was detected. "
        if timeline:
            what += f"Initiated at {timeline[0].get('source', 'unknown')} and terminating at {timeline[-1].get('destination', 'unknown')}."
            
        summary = f"Risk severity is {risk['severity']} (Score: {risk['risk_score']}). "
        if mitre:
            techs = ", ".join([t['technique_id'] for t in mitre])
            summary += f"Identified ATT&CK techniques: {techs}."
            
        questions = [
            "What was the initial entry vector?",
            "Were any high-value assets compromised?",
            "Is the compromised identity still active?"
        ]
        
        actions = []
        if risk['severity'] in ['HIGH', 'CRITICAL']:
            actions.append("Initiate immediate endpoint isolation.")
        actions.append("Review timeline for lateral movement indicators.")
        
        return {
            "what_happened": what,
            "why": why,
            "attack_summary": summary,
            "recommended_questions": questions,
            "next_actions": actions
        }
