from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

import dacite


@dataclass
class YTrapStationSettings:
    """Contains the settings of the crystal station"""

    mode: Literal["precise", "precise refill", "normal", "set folders"]
    plot_stacks: int
    plots_per_stack: int
    min_pellet_coverage: float
    turn_direction: Literal["left", "right"]
    crop_plot_turns: list[int]

    @staticmethod
    def load() -> YTrapStationSettings:
        with open("settings/settings.json") as f:
            data = json.load(f)["ytrap"]
        data["crop_plot_turns"] = eval(data["crop_plot_turns"])
        return dacite.from_dict(YTrapStationSettings, data)
