from scenarios.adversarial_scenarios import FinalScenarios
from app.simulator import ScenarioData

class JudgeScenarios:
    """
    Polished demonstrations for hackathon judges.
    """
    def __init__(self):
        self.base = FinalScenarios()
        
    def invisible_employee(self) -> ScenarioData:
        data = self.base.get_scenario_3_identity_spoof()
        data.name = "1. Invisible Employee (Identity Spoof)"
        return data
        
    def silent_insider(self) -> ScenarioData:
        data = self.base.get_scenario_2_stolen_credential()
        data.name = "2. Silent Insider (Stolen Credential)"
        return data
        
    def ransomware_sprint(self) -> ScenarioData:
        data = self.base.get_scenario_4_lotl()
        data.name = "3. Ransomware Sprint (Lateral Movement)"
        return data
        
    def apt_ghost_campaign(self) -> ScenarioData:
        data = self.base.get_scenario_1_vpn_rotation()
        data.name = "4. APT Ghost Campaign (VPN Evasion)"
        return data
