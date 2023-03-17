from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import dacite


@dataclass
class MedbrewStationSettings:
    """Contains the settings of the crystal station"""

    enabled: bool
    beds: int
    prefix: str
    
    @staticmethod
    def load() -> MedbrewStationSettings:
        with open("settings/settings.json") as f:
            data: dict[str, Any] = json.load(f)["medbrew"]

        settings = {k.removeprefix("medbrew_"): v for k, v in data.items()}
        return dacite.from_dict(MedbrewStationSettings, settings)
