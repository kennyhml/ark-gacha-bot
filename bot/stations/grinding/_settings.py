from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class GrindingStationSettings:
    """Contains the settings of the crystal station"""



    @staticmethod
    def load() -> GrindingStationSettings:
        raise NotImplementedError
        
        with open("settings/settings.json") as f:
            data = json.load(f)["crystal"]
        return dacite.from_dict(GrindingStationSettings, data)
