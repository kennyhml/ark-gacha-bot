from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

import dacite


@dataclass
class TowerSettings:
    account_name: str
    game_launcher: Literal["Steam", "Epic"]
    ark_path: str
    tesseract_path: str
    map: Literal["Genesis 2", "Aberration", "Other"]

    ytrap_beds: int
    ytrap_prefix: str
    crystal_beds: int
    crystal_prefix: str

    ytrap_station: bool
    grinding_station: bool
    arb_station: bool
    berry_station: bool
    meat_station: bool

    @staticmethod
    def load() -> TowerSettings:
        with open("settings/settings.json") as f:
            data = json.load(f)["main"]
        return dacite.from_dict(TowerSettings, data)

    
@dataclass
class FeedStationSettings:
    berry_beds: int
    berry_prefix: str
    berry_interval: int

    meat_beds: int
    meat_prefix: str
    meat_interval: int

    @staticmethod
    def load() -> FeedStationSettings:
        with open("settings/settings.json") as f:
            data = json.load(f)["feedstation"]
        return dacite.from_dict(FeedStationSettings, data)