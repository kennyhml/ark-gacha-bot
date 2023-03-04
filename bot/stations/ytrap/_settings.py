from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

import dacite


@dataclass
class YTrapStationSettings:
    """Contains the settings of the crystal station"""

    enabled: bool
    ytrap_beds: int
    ytrap_prefix: str
    auto_level_gachas: bool
    mode: Literal["precise", "precise refill", "normal", "set folders"]
    plot_stacks: int
    plots_per_stack: int
    min_pellet_coverage: float
    gacha_turn: int
    plot_delay: float
    turn_direction: Literal["left", "right"]
    crop_plot_turns: list[int]

    @staticmethod
    def load() -> YTrapStationSettings:
        with open("settings/settings.json") as f:
            data: dict = json.load(f)["ytrap"]
            
        data["min_pellet_coverage"] /= 100
        data["enabled"] = data.pop("ytrap_enabled")
        data["plot_delay"] = data.pop("ytrap_plot_delay")
        data["gacha_turn"] = data.pop("ytrap_gacha_turn")
        data["crop_plot_turns"] = eval(data["crop_plot_turns"])
        return dacite.from_dict(YTrapStationSettings, data)
