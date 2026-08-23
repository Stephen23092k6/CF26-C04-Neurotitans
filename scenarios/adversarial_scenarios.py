from app.adversary import IdentityAdversarySimulator
from app.simulator import ScenarioData

class FinalScenarios(IdentityAdversarySimulator):
    """
    Wraps the adversary simulator to provide the 4 official scenarios for Phase 6.
    """
    
    def get_scenario_1_vpn_rotation(self) -> ScenarioData:
        """
        Scenario 1: VPN Rotation Attack
        Flow: Same user, same device, multiple IPs/networks.
        Expected: Identity continuity remains high.
        """
        data = self.simulate_vpn_rotation()
        data.name = "VPN Rotation Attack"
        return data
        
    def get_scenario_2_stolen_credential(self) -> ScenarioData:
        """
        Scenario 2: Stolen Credential Attack
        Flow: Same user ID, new device, impossible context.
        Expected: Identity contradiction penalty.
        """
        data = self.simulate_stolen_credential()
        data.name = "Stolen Credential Attack"
        return data
        
    def get_scenario_3_identity_spoof(self) -> ScenarioData:
        """
        Scenario 3: Identity Spoof Attack
        Flow: Fake user/device metadata injected.
        Expected: Contradiction detection.
        """
        data = self.simulate_identity_spoofing()
        data.name = "Identity Spoof Attack"
        return data
        
    def get_scenario_4_lotl(self) -> ScenarioData:
        """
        Scenario 4: Living-off-the-land attack
        Flow: Legitimate tools, suspicious sequence, low network anomaly.
        Expected: Behavioral suspicion (Temporal + Topology but no obvious anomaly).
        """
        t = self.base_time - 100
        events = []
        gt = {
            "seed": "D-050",
            "target": "S-02",
            "expected_nodes": ["D-050", "S-02"],
            "expected_edges": ["D-050->S-02"]
        }
        
        # Legitimate login
        events.append(self._event("L1", "AUTHENTICATION", t, "D-050", "D-050", floor=2, severity=0.1, user_id="SYS-ADMIN", network="N-02"))
        
        # Legitimate RDP/SSH tool usage (low severity)
        events.append(self._event("L2", "NETWORK_CONNECTION", t+10, "D-050", "S-02", floor=3, severity=0.3, network="N-03", user_id="SYS-ADMIN", meta={"tool": "mstsc.exe"}))
        
        # Database access (low severity)
        events.append(self._event("L3", "RESOURCE_ACCESS", t+15, "S-02", "S-02", floor=3, severity=0.2, network="N-03", user_id="SYS-ADMIN", meta={"process": "sqlcmd.exe"}))

        events.extend(self.normal_events(100))
        self.rng.shuffle(events)
        
        return ScenarioData("Living-off-the-land Attack", events, gt)
