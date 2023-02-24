from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class GrindingStationSettings:
    """Contains the settings of the crystal station"""

    item_to_craft: str

    @staticmethod
    def load() -> GrindingStationSettings:

        with open("settings/settings.json") as f:
            data = json.load(f)["grinding"]
        return dacite.from_dict(GrindingStationSettings, data)
