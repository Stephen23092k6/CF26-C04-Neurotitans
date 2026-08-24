from typing import Dict, Any, List

class EnterpriseEnvironment:
    """
    Represents enterprise assets for multi-tenant security modeling.
    """
    def __init__(self):
        self.assets: Dict[str, Dict[str, Any]] = {}
        
    def add_asset(self, asset_id: str, criticality: str, owner: str, asset_type: str = "endpoint") -> None:
        """
        Criticality levels: LOW, MEDIUM, HIGH, CRITICAL
        """
        self.assets[asset_id] = {
            "asset": asset_id,
            "criticality": criticality,
            "owner": owner,
            "type": asset_type
        }
        
    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        return self.assets.get(asset_id, {
            "asset": asset_id,
            "criticality": "UNKNOWN",
            "owner": "UNKNOWN",
            "type": "UNKNOWN"
        })
        
    def get_critical_assets(self) -> List[Dict[str, Any]]:
        return [a for a in self.assets.values() if a["criticality"] in ("HIGH", "CRITICAL")]
