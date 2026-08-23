class ResponseEngine:
    @staticmethod
    def generate_plan(risk: dict, techniques: list[dict], identity_anomalies: list[str] = None) -> dict:
        actions = []
        sev = risk.get("severity", "LOW")
        
        if sev == "CRITICAL":
            actions.append("Disable compromised session")
            actions.append("Isolate endpoint")
            actions.append("Collect forensic evidence")
        elif sev == "HIGH":
            actions.append("Isolate endpoint")
            
        t_ids = [t["technique_id"] for t in techniques]
        if "T1078" in t_ids or "T1003" in t_ids or (identity_anomalies and len(identity_anomalies) > 0):
            actions.append("Force credential reset")
            
        if not actions:
            actions.append("Monitor assets")
            
        return {
            "severity": sev,
            "actions": actions
        }
