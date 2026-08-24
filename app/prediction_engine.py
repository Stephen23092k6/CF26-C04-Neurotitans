from typing import Dict, List, Any
from app.engine import AttackPath, DynamicSecurityGraph
from app.security_memory import SecurityMemory

class ThreatPredictionEngine:
    """
    Deterministic engine to predict possible next attacker actions.
    """
    
    def __init__(self, memory: SecurityMemory):
        self.memory = memory
        
    def predict(self, path: AttackPath, mitre_techniques: List[Dict[str, Any]]) -> Dict[str, Any]:
        techniques = [t.get("technique_id") for t in mitre_techniques if "technique_id" in t]
        
        predicted_actions = []
        reasoning = []
        confidence = 0
        
        # Rule 1: Lateral Movement -> Privilege Escalation / Data Exfiltration
        if "T1021" in techniques:
            predicted_actions.append("Privilege Escalation")
            predicted_actions.append("Data Access")
            reasoning.append("Lateral movement (T1021) detected; typical next step is privilege escalation or accessing sensitive data.")
            confidence += 40
            
        # Rule 2: Credential Dumping -> Lateral Movement
        if "T1003" in techniques:
            if "T1021" not in techniques:
                predicted_actions.append("Lateral Movement")
                reasoning.append("Detected credential dumping (T1003); attackers usually follow up with lateral movement using harvested credentials.")
                confidence += 30
                
        # Rule 3: Identity anomaly in path
        identity_issues = any(e.continuity_penalty > 0 for e in path.edges) if hasattr(path, 'edges') else False
        if identity_issues:
            if "Defense Evasion" not in predicted_actions:
                predicted_actions.append("Defense Evasion")
            reasoning.append("Multiple identity transitions or anomalies detected; attacker may attempt defense evasion.")
            confidence += 25
            
        # Match with historical memory
        if techniques:
            similar = self.memory.retrieve_similar_incidents(techniques, top_k=1)
            if similar and similar[0]["incident_similarity"] > 0.5:
                past_pattern = similar[0]["previous_pattern"]
                if "Credential" in past_pattern and "Privilege Escalation" not in predicted_actions:
                    predicted_actions.append("Privilege Escalation")
                reasoning.append(f"Behavior matches historical pattern: {past_pattern}.")
                confidence += 20
                
        # Base case / fallback
        if not predicted_actions:
            predicted_actions = ["Discovery", "Lateral Movement"]
            reasoning.append("Initial stages of attack detected; expected discovery and lateral movement.")
            confidence = 50
            
        # Deduplicate and cap confidence
        predicted_actions = list(dict.fromkeys(predicted_actions))
        confidence = min(95, confidence if confidence > 0 else 50)
        
        return {
            "predicted_actions": predicted_actions,
            "confidence": confidence,
            "reasoning": reasoning
        }
