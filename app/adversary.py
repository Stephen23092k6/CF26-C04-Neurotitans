from app.simulator import BuildingSimulator, ScenarioData

class IdentityAdversarySimulator(BuildingSimulator):
    """
    Extends BuildingSimulator to generate specific identity-centric adversary simulations
    for evaluating the Phase 4 Identity Continuity Layer.
    """
    
    def simulate_vpn_rotation(self) -> ScenarioData:
        """
        Adversary rapidly changes IP address via VPN proxy while using the same device 
        fingerprint and user session. Expected to preserve continuity.
        """
        t = self.base_time - 100
        events = [
            self._event("v1", "AUTHENTICATION", t, "D-007", "S-01", floor=1, severity=0.3, user_id="USER-ALICE", network="N-01", meta={"ip_address": "192.168.1.50"}),
            # VPN Hop 1
            self._event("v2", "NETWORK_CONNECTION", t+10, "D-007", "S-02", floor=3, severity=0.6, user_id="USER-ALICE", network="N-03", meta={"ip_address": "10.0.0.1"}),
            # VPN Hop 2
            self._event("v3", "RESOURCE_ACCESS", t+20, "D-007", "D-999", floor=5, severity=0.8, user_id="USER-ALICE", network="N-05", meta={"ip_address": "172.16.0.45"}),
        ]
        
        gt = {
            "seed": "D-007",
            "target": "D-999",
            "expected_nodes": ["D-007", "S-02", "D-999"],
            "event_ids": ["v1", "v2", "v3"]
        }
        return ScenarioData("VPN_ROTATION", events + self.normal_events(50), gt)

    def simulate_stolen_credential(self) -> ScenarioData:
        """
        Adversary uses stolen credentials from an impossible/anomalous device context.
        Should reduce confidence and trigger anomaly penalties.
        """
        t = self.base_time - 100
        events = [
            # Legitimate user activity
            self._event("s1", "AUTHENTICATION", t, "D-010", "S-01", floor=2, severity=0.1, user_id="USER-BOB", network="N-02", meta={"ip_address": "192.168.2.10"}),
            
            # Stolen credential login from unexpected device / location
            self._event("s2", "AUTHENTICATION", t+30, "D-040", "S-01", floor=5, severity=0.9, user_id="USER-BOB", network="N-05", meta={"ip_address": "203.0.113.5", "impossible_context": True}),
            self._event("s3", "RESOURCE_ACCESS", t+40, "D-040", "D-999", floor=5, severity=1.0, user_id="USER-BOB", network="N-05", meta={"ip_address": "203.0.113.5"}),
        ]
        
        gt = {
            "seed": "D-010",
            "target": "D-999",
            "expected_nodes": ["D-010", "D-040", "D-999"],
            "event_ids": ["s1", "s2", "s3"]
        }
        return ScenarioData("STOLEN_CREDENTIAL", events + self.normal_events(50), gt)

    def simulate_identity_spoofing(self) -> ScenarioData:
        """
        Adversary spoofs identity / manipulates telemetry.
        Should trigger contradictory penalties and fail or severely degrade reconstruction.
        """
        t = self.base_time - 100
        events = [
            self._event("f1", "AUTHENTICATION", t, "D-015", "S-01", floor=2, severity=0.4, user_id="USER-EVE", network="N-02", meta={"ip_address": "192.168.2.15"}),
            # Spoofed identity
            self._event("f2", "NETWORK_CONNECTION", t+15, "D-015", "S-02", floor=3, severity=0.9, user_id="SYS-ADMIN", network="N-03", meta={"spoofed_identity": True}),
            self._event("f3", "RESOURCE_ACCESS", t+25, "D-015", "D-999", floor=5, severity=0.9, user_id="SYS-ADMIN", network="N-05", meta={"spoofed_identity": True}),
        ]
        
        gt = {
            "seed": "D-015",
            "target": "D-999",
            "expected_nodes": ["D-015", "S-02", "D-999"],
            "event_ids": ["f1", "f2", "f3"]
        }
        return ScenarioData("IDENTITY_SPOOFING", events + self.normal_events(50), gt)

    def simulate_ip_churn(self) -> ScenarioData:
        """
        Device churns IP rapidly (e.g. DHCP release/renew storm) but is otherwise benign.
        Continuity should absorb it.
        """
        t = self.base_time - 100
        events = [
            self._event("c1", "DEVICE_TELEMETRY", t, "D-020", "D-020", floor=3, severity=0.1, meta={"ip_address": "10.0.3.20"}),
            self._event("c2", "DEVICE_TELEMETRY", t+5, "D-020", "D-020", floor=3, severity=0.2, meta={"ip_address": "10.0.3.21"}),
            self._event("c3", "NETWORK_CONNECTION", t+10, "D-020", "S-02", floor=3, severity=0.4, meta={"ip_address": "10.0.3.22"}),
        ]
        
        gt = {
            "seed": "D-020",
            "target": "S-02",
            "expected_nodes": ["D-020", "S-02"],
            "event_ids": ["c1", "c2", "c3"]
        }
        return ScenarioData("IP_CHURN", events + self.normal_events(20), gt)
