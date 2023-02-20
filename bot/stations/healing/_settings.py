from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class HealingStationSettings:
    """Contains the settings of the crystal station"""

    pod_name: str

    @staticmethod
    def load() -> HealingStationSettings:
        with open("settings/settings.json") as f:
            data = json.load(f)["healing"]
        return dacite.from_dict(HealingStationSettings, data)
