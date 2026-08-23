from scenarios.adversarial_scenarios import FinalScenarios
from app.simulator import ScenarioData

class ThreatActorProfile:
    def __init__(self, scenarios: FinalScenarios):
        self.scenarios = scenarios

    def simulate_apt(self) -> ScenarioData:
        data = self.scenarios.get_scenario_4_lotl()
        data.name = "APT"
        return data

    def simulate_insider(self) -> ScenarioData:
        data = self.scenarios.get_scenario_2_stolen_credential()
        data.name = "INSIDER"
        return data

    def simulate_credential_theft(self) -> ScenarioData:
        data = self.scenarios.get_scenario_3_identity_spoof()
        data.name = "CREDENTIAL_THEFT"
        return data

    def simulate_ransomware(self) -> ScenarioData:
        data = self.scenarios.get_scenario_4_lotl()
        data.name = "RANSOMWARE"
        return data
