from __future__ import annotations

import json
from dataclasses import dataclass

import dacite


@dataclass
class DiscordSettings:
    """Contains the settings of the crystal station"""

    user_id: str
    timer_pop: int
    webhook_alert: str
    webhook_gacha: str
    webhook_logs: str
    webhook_state: str
    state_message_id: str
    
    @staticmethod
    def load() -> DiscordSettings:
        with open("settings/settings.json") as f:
            data = json.load(f)["discord"]

        return dacite.from_dict(DiscordSettings, data)
