import json
from typing import Dict, List, Any, Optional

class SecurityMemory:
    """
    Deterministic long-term memory for previous incidents and attack patterns.
    """
    
    def __init__(self):
        self.incidents: List[Dict[str, Any]] = []
        self.attack_patterns: Dict[str, Dict[str, Any]] = {}
        self.mitre_frequency: Dict[str, int] = {}
        self.analyst_feedback: List[Dict[str, Any]] = []
        
        # Seed with some baseline historical memory to allow similarities to match out of the box
        self._seed_baseline_memory()
        
    def _seed_baseline_memory(self):
        self.add_incident(
            incident_id="INC-001",
            techniques=["T1078", "T1003", "T1021"],
            pattern="Credential Abuse",
            family="APT",
            response=["Disable identity", "Collect endpoint telemetry", "Isolate endpoint"]
        )
        self.add_incident(
            incident_id="INC-002",
            techniques=["T1190", "T1486"],
            pattern="Public Facing Exploit & Ransomware",
            family="Ransomware-Syndicate",
            response=["Disconnect network", "Restore from backup", "Block external IP"]
        )
        self.add_incident(
            incident_id="INC-003",
            techniques=["T1059", "T1053"],
            pattern="Scripting & Scheduled Tasks",
            family="Generic Insider",
            response=["Review scheduled tasks", "Revoke script execution policy"]
        )
        
    def add_incident(self, incident_id: str, techniques: List[str], pattern: str, family: str, response: List[str]) -> None:
        incident = {
            "incident_id": incident_id,
            "techniques": sorted(techniques),
            "pattern": pattern,
            "family": family,
            "response": response
        }
        self.incidents.append(incident)
        
        # Update pattern and MITRE frequencies
        if pattern not in self.attack_patterns:
            self.attack_patterns[pattern] = {"count": 0, "associated_techniques": set()}
        
        self.attack_patterns[pattern]["count"] += 1
        for t in techniques:
            self.attack_patterns[pattern]["associated_techniques"].add(t)
            self.mitre_frequency[t] = self.mitre_frequency.get(t, 0) + 1
            
    def _jaccard_similarity(self, list1: List[str], list2: List[str]) -> float:
        set1 = set(list1)
        set2 = set(list2)
        if not set1 and not set2:
            return 1.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    def retrieve_similar_incidents(self, current_techniques: List[str], top_k: int = 1) -> List[Dict[str, Any]]:
        if not current_techniques:
            return []
            
        scored = []
        for inc in self.incidents:
            sim = self._jaccard_similarity(current_techniques, inc["techniques"])
            scored.append((sim, inc))
            
        scored.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for sim, inc in scored[:top_k]:
            results.append({
                "incident_similarity": round(sim, 2),
                "previous_pattern": inc["pattern"],
                "known_attack_family": inc["family"],
                "recommended_response": inc["response"]
            })
        return results

    def match_attack_pattern(self, current_techniques: List[str]) -> Optional[str]:
        # Returns the most likely pattern based on technique overlap
        best_match = None
        highest_overlap = 0
        current_set = set(current_techniques)
        
        for pattern, data in self.attack_patterns.items():
            overlap = len(current_set.intersection(data["associated_techniques"]))
            if overlap > highest_overlap:
                highest_overlap = overlap
                best_match = pattern
                
        return best_match

    def get_threat_history(self) -> Dict[str, Any]:
        return {
            "total_incidents_in_memory": len(self.incidents),
            "top_mitre_techniques": sorted(self.mitre_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            "known_patterns": list(self.attack_patterns.keys())
        }
