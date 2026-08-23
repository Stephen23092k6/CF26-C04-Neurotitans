import time

class AnalystMemory:
    def __init__(self):
        self.decisions = []
        
    def store_decision(self, incident_id: str, analyst_action: str, notes: str):
        assert analyst_action in ["ACCEPT", "REJECT", "FALSE_POSITIVE"]
        self.decisions.append({
            "incident_id": incident_id,
            "analyst_action": analyst_action,
            "timestamp": time.time(),
            "notes": notes
        })
