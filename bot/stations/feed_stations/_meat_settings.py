from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class MeatStationSettings:
    """Contains the settings of the crystal station"""

    enabled: bool
    meat_beds: int
    meat_prefix: str
    meat_interval: int

    @staticmethod
    def load() -> MeatStationSettings:
        with open("settings/settings.json") as f:
            data: dict = json.load(f)["meat"]
            data["enabled"] = data.pop("meat_enabled")

        return dacite.from_dict(MeatStationSettings, data)
