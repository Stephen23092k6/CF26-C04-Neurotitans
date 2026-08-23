from .engine import Event

class MitreMapper:
    @staticmethod
    def map_event(event: Event) -> dict:
        mapping = None
        if event.event_type == "AUTHENTICATION":
            mapping = {"technique_id": "T1078", "technique_name": "Valid Accounts", "confidence": "High"}
        elif event.event_type == "NETWORK_CONNECTION":
            mapping = {"technique_id": "T1021", "technique_name": "Remote Services", "confidence": "Medium"}
        elif event.event_type == "COMMAND_EXECUTION":
            mapping = {"technique_id": "T1059", "technique_name": "Command and Scripting Interpreter", "confidence": "High"}
        elif event.event_type == "RESOURCE_ACCESS":
            mapping = {"technique_id": "T1003", "technique_name": "OS Credential Dumping", "confidence": "Medium"}
            
        if mapping:
            return {**mapping, "evidence": event.event_id}
        return None
        
    @staticmethod
    def extract_techniques(path, graph) -> list[dict]:
        techs = []
        seen = set()
        event_lookup = {e.event_id: e for e in graph.events}
        for e in path.edges:
            for sub_e_id in e.supporting_events:
                sub_e = event_lookup.get(sub_e_id)
                if not sub_e: continue
                m = MitreMapper.map_event(sub_e)
                if m and m["technique_id"] not in seen:
                    techs.append(m)
                    seen.add(m["technique_id"])
        return techs
