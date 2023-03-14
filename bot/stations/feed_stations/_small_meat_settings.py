from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class SmallMeatStationSettings:
    """Contains the settings of the crystal station"""

    enabled: bool
    meat_beds: int
    meat_prefix: str
    meat_interval: int

    @staticmethod
    def load() -> SmallMeatStationSettings:
        with open("settings/settings.json") as f:
            data: dict = json.load(f)["small_meat"]
        
        data["enabled"] = data.pop("small_meat_enabled")
        data["meat_beds"] = data.pop("small_meat_beds")
        data["meat_prefix"] = data.pop("small_meat_prefix")
        data["meat_interval"] = data.pop("small_meat_interval") * 60

        return dacite.from_dict(SmallMeatStationSettings, data)
