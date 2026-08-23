from dataclasses import dataclass, field
from typing import Optional, Any

@dataclass
class DeviceIdentityEvidence:
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    confidence: float = 1.0

@dataclass
class IdentityNode:
    user_id: Optional[str]
    device_evidence: DeviceIdentityEvidence

class SessionContinuity:
    """
    Evaluates identity continuity across a path reconstruction.
    This is instantiated per-path to avoid global mutable state.
    """
    
    def __init__(self):
        # Track the most recent known identity state for the path
        self.last_user: Optional[str] = None
        self.last_device: Optional[str] = None
        self.last_ip: Optional[str] = None
        
    def update_from_events(self, events: list):
        """Update path-local state based on a sequence of events."""
        for e in events:
            if e.user_id:
                self.last_user = e.user_id
            if e.device_id:
                self.last_device = e.device_id
            
            ip = e.metadata.get("ip_address")
            if ip:
                self.last_ip = ip

    def evaluate_transition(self, next_events: list) -> tuple[float, float, list[str]]:
        """
        Evaluate transition to the next step.
        Returns: (continuity_bonus, anomaly_penalty, reasons)
        """
        if not next_events:
            return 0.0, 0.0, []
            
        next_e = next_events[0]
        
        nxt_user = next_e.user_id
        nxt_device = next_e.device_id
        nxt_ip = next_e.metadata.get("ip_address")
        
        bonus = 0.0
        penalty = 0.0
        reasons = []
        
        # 1. Unknown / Spoofed identity detection
        if next_e.metadata.get("spoofed_identity", False):
            penalty += 40.0
            reasons.append("spoofed_identity_contradiction(-40.0)")
            return 0.0, penalty, reasons
            
        # 2. Strong Identity Continuity (User + Device matched)
        if self.last_user and nxt_user == self.last_user:
            if self.last_device and nxt_device == self.last_device:
                # Same device + changed IP/VPN = preserve continuity
                if self.last_ip and nxt_ip and self.last_ip != nxt_ip:
                    bonus += 30.0
                    reasons.append("vpn_rotation_continuity(+30.0)")
                else:
                    bonus += 30.0
                    reasons.append("strong_identity_continuity(+30.0)")
            else:
                # Stolen credential scenario: Same user, different device context (anomalous)
                if next_e.metadata.get("impossible_context", False):
                    penalty += 30.0
                    reasons.append("stolen_credential_anomaly(-30.0)")
                else:
                    # Generic user roam
                    bonus += 10.0
                    reasons.append("user_continuity(+10.0)")
                    
        elif self.last_device and nxt_device == self.last_device:
             bonus += 15.0
             reasons.append("device_continuity(+15.0)")
             
        return bonus, penalty, reasons

    def clone(self) -> 'SessionContinuity':
        """Clone to branch the path tracking safely."""
        c = SessionContinuity()
        c.last_user = self.last_user
        c.last_device = self.last_device
        c.last_ip = self.last_ip
        return c
