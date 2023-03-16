from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class MedbrewStationSettings:
    """Contains the settings of the crystal station"""

    medbrew_beds: int
    medbrew_prefix: str
    medbrew_interval: int

    @staticmethod
    def load() -> MedbrewStationSettings:
        with open("settings/settings.json") as f:
            data: dict = json.load(f)["medbrew"]
            
        return dacite.from_dict(MedbrewStationSettings, data)
