class InvestigationTimeline:
    @staticmethod
    def generate(path, graph) -> list[dict]:
        timeline = []
        event_lookup = {e.event_id: e for e in graph.events}
        for e in path.edges:
            for sub_e_id in e.supporting_events:
                sub_e = event_lookup.get(sub_e_id)
                if not sub_e: continue
                timeline.append({
                    "timestamp": sub_e.event_time,
                    "event": sub_e.event_type,
                    "source": sub_e.source,
                    "destination": sub_e.destination,
                    "evidence": sub_e.event_id,
                    "explanation": e.inference_reason
                })
        timeline.sort(key=lambda x: x["timestamp"])
        return timeline
