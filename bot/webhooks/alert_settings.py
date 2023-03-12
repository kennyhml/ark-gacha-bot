from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class AlertSettings:
    """Contains the settings of the crystal station"""

    mention_cooldown: int
    destroyed_id: str
    killed_id: str
    tek_sensor_id: str
    mass_event_mention: bool
    mention_at_events: int
    
    @staticmethod
    def load() -> AlertSettings:
        with open("settings/settings.json") as f:
            data = json.load(f)["alerts"]

        return dacite.from_dict(AlertSettings, data)
