class RiskAssessment:
    @staticmethod
    def calculate(path, explanation) -> dict:
        base_score = path.score
        conf = path.confidence
        
        # Asset criticality check
        has_critical = any(n in ["D-999", "S-02"] for n in path.nodes)
        asset_multiplier = 1.2 if has_critical else 1.0
        
        # Identity anomaly multiplier
        id_multiplier = 1.0
        if explanation["identity_analysis"].get("identity_spoofing"):
            id_multiplier = 1.5
        elif explanation["identity_analysis"].get("credential_risk"):
            id_multiplier = 1.3
            
        final_score = min(100.0, base_score * (conf / 100.0) * asset_multiplier * id_multiplier)
        
        if final_score <= 25:
            severity = "LOW"
        elif final_score <= 50:
            severity = "MEDIUM"
        elif final_score <= 75:
            severity = "HIGH"
        else:
            severity = "CRITICAL"
            
        return {
            "risk_score": round(final_score, 1),
            "severity": severity
        }
