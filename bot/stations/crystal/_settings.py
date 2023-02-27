from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class CrystalStationSettings:
    """Contains the settings of the crystal station"""

    drop_items: list[str]
    keep_items: list[str]
    min_ytraps_collected: int 
    crystal_interval: int
    stryder_depositing: bool

    @staticmethod
    def load() -> CrystalStationSettings:
        with open("settings/settings.json") as f:
            data = json.load(f)["crystal"]

        for k, v in data.items():
            if "items" in k:
                data[k] = eval(v)

        return dacite.from_dict(CrystalStationSettings, data)
