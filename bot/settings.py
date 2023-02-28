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

    @staticmethod
    def load() -> TowerSettings:
        with open("settings/settings.json") as f:
            data = json.load(f)["main"]
        return dacite.from_dict(TowerSettings, data)