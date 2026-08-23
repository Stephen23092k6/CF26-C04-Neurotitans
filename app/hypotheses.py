from .engine import AttackPath
from .explanation import PathExplanation

class AttackHypothesis:
    def __init__(self, name: str, attack_path: AttackPath, confidence: float, supporting_evidence: list[str], contradicting_evidence: list[str], affected_assets: list[str]):
        self.name = name
        self.attack_path = attack_path
        self.confidence = confidence
        self.supporting_evidence = supporting_evidence
        self.contradicting_evidence = contradicting_evidence
        self.affected_assets = affected_assets
        
    @staticmethod
    def generate(paths: list[AttackPath]) -> list['AttackHypothesis']:
        hypotheses = []
        for p in paths:
            exp = PathExplanation.generate(p)
            name = "Malware / Lateral Movement"
            if exp["identity_analysis"].get("credential_risk"):
                name = "Credential Abuse"
            elif exp["identity_analysis"].get("identity_spoofing"):
                name = "Identity Compromise / Spoofing"
            elif exp["identity_analysis"].get("vpn_rotation_detected"):
                name = "Evasive Lateral Movement (VPN Rotation)"
            
            supporting = exp.get("evidence", [])
            contradicting = [r["reason"] for r in exp.get("rejected_hypotheses", [])]
            assets = p.nodes
            
            h = AttackHypothesis(name, p, p.confidence, supporting, contradicting, assets)
            hypotheses.append(h)
            
        hypotheses.sort(key=lambda x: x.confidence, reverse=True)
        return hypotheses
