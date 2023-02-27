from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class GrindingStationSettings:
    """Contains the settings of the crystal station"""

    item_to_craft: str
    text_rgb: tuple[int, int, int]
    pearls_region: tuple[int, int, int, int]
    paste_region: tuple[int, int, int, int] 
    electronics_region: tuple[int, int, int, int] 
    ingots_region: tuple[int, int, int, int] 
    crystal_region: tuple[int, int, int, int] 
    hide_region: tuple[int, int, int, int] 
    
    @staticmethod
    def load() -> GrindingStationSettings:

        with open("settings/settings.json") as f:
            data: dict = json.load(f)["grinding"]

        for k, v in data.items():
            if k == "text_rgb" or "region" in k:
                data[k] = eval(v)
        
        return dacite.from_dict(GrindingStationSettings, data)
