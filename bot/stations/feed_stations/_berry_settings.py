from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class BerryStationSettings:
    """Contains the settings of the crystal station"""

    enabled: bool
    berry_beds: int
    berry_prefix: str
    berry_interval: int

    @staticmethod
    def load() -> BerryStationSettings:
        with open("settings/settings.json") as f:
            data: dict = json.load(f)["berry"]
            data["enabled"] = data.pop("berry_enabled")

        return dacite.from_dict(BerryStationSettings, data)
