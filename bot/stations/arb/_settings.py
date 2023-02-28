from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class ArbStationSettings:
    """Contains the settings of the crystal station"""

    enabled: bool

    @staticmethod
    def load() -> ArbStationSettings:
        with open("settings/settings.json") as f:
            data: dict = json.load(f)["arb"]
            data["enabled"] = data.pop("arb_enabled")

        return dacite.from_dict(ArbStationSettings, data)
