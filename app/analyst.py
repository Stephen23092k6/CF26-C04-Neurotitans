from typing import Any
from .explanation import PathExplanation

class AnalystReportGenerator:
    """
    SOC Analyst report generator. Translates deterministic explanation reports
    into human-readable threat assessments without using LLMs.
    """
    
    @staticmethod
    def generate(explanation_dict: dict[str, Any]) -> str:
        conf = explanation_dict["confidence"]
        
        # Threat Title
        if explanation_dict["identity_analysis"]["identity_spoofing"]:
            threat = "Telemetry Spoofing / Severe Identity Compromise"
        elif explanation_dict["identity_analysis"]["credential_risk"]:
            threat = "Compromised Credentials / Lateral Movement"
        elif explanation_dict["identity_analysis"]["vpn_rotation_detected"]:
            threat = "Evasive Lateral Movement (VPN Rotation)"
        else:
            threat = "Possible lateral movement detected"
            
        # Risk Band
        if conf >= 90:
            risk = "HIGH"
        elif conf >= 70:
            risk = "MEDIUM"
        else:
            risk = "LOW"
            
        # Reasoning
        reasoning_lines = []
        if explanation_dict["identity_analysis"]["device_continuity"]:
            reasoning_lines.append("✓ Device identity remained consistent")
        if explanation_dict["identity_analysis"]["vpn_rotation_detected"]:
            reasoning_lines.append("✓ VPN rotation explained network change")
        if "Temporal correlation confirmed" in explanation_dict["evidence"]:
            reasoning_lines.append("✓ Temporal sequence matched known attack behavior")
        if explanation_dict["identity_analysis"]["credential_risk"]:
            reasoning_lines.append("⚠ Identity anomaly: Credential used on suspicious device context")
        if explanation_dict["identity_analysis"]["identity_spoofing"]:
            reasoning_lines.append("⚠ SEVERE: Identity spoofing or impossible teleportation detected")
            
        if not reasoning_lines:
            reasoning_lines.append("⚠ Insufficient correlated evidence")
            
        reasoning_block = "\n".join(reasoning_lines)
        
        # Recommended Action
        if risk == "HIGH":
            if explanation_dict["identity_analysis"]["credential_risk"]:
                action = "Force credential reset for involved users and isolate target endpoints."
            else:
                action = "Investigate affected endpoints immediately."
        elif risk == "MEDIUM":
            action = "Monitor endpoints for further suspicious activity."
        else:
            action = "Close as informational or low priority."

        report = f"""=================================
NEUROBRAIN X INCIDENT REPORT
=================================

Threat:
{threat}

Confidence:
{conf}%

Reasoning:

{reasoning_block}

Risk:
{risk}

Recommended analyst action:
{action}
"""
        return report
