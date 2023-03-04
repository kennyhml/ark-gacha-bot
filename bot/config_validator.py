import json
from pathlib import Path


class ConfigValidator:

    EXPECTED_CONFIG = {
        "main": {
            "account_name": "Kitten123",
            "game_launcher": "Epic",
            "ark_path": "F:/ARKSurvivalEvolved",
            "tesseract_path": "C:/Program Files/Tesseract-OCR/tesseract.exe",
            "map": "Other",
        },
        "player": {"health": 300, "food": 100, "water": 100, "weight": 1000},
        "discord": {
            "user_id": "",
            "webhook_alert": "",
            "webhook_gacha": "",
            "webhook_logs": "",
            "webhook_state": "",
            "state_message_id": "",
            "timer_pop": 30,
        },
        "ytrap": {
            "ytrap_enabled": True,
            "ytrap_beds": 52,
            "ytrap_prefix": "seed",
            "mode": "precise refill",
            "turn_direction": "right",
            "auto_level_gachas": True,
            "plot_stacks": 3,
            "plots_per_stack": 8,
            "min_pellet_coverage": 50,
            "crop_plot_turns": "[-130, *[-17] * 5, 50, -17]",
        },
        "crystal": {
            "crystal_beds": 1,
            "crystal_prefix": "crystal",
            "crystal_interval": 5,
            "stryder_depositing": True,
            "drop_items": "['prim']",
            "keep_items": "['riot', 'rifle', 'pistol', 'miner']",
            "min_ytraps_collected": 1000,
            "vault_above": False,
        },
        "berry": {
            "berry_enabled": False,
            "berry_beds": 4,
            "berry_prefix": "autoberry",
            "berry_interval": 300,
        },
        "meat": {
            "meat_enabled": False,
            "meat_beds": 4,
            "meat_prefix": "automeat",
            "meat_interval": 120,
        },
        "healing": {"pod_name": "Gacha Heal"},
        "grinding": {
            "grinding_enabled": True,
            "item_to_craft": "Heavy Auto Turret",
            "text_rgb": " (56, 232, 231)",
            "pearls_region": "(25,350,510,355)",
            "paste_region": "(17,697,560,370)",
            "electronics_region": "(593,390,590,303)",
            "ingots_region": "(570,730,640,305)",
            "crystal_region": "(1245,365,560,315)",
            "hide_region": "(1240,690,613,355)",
        },
        "arb": {"arb_enabled": True},
    }

    def __init__(self) -> None:
        self.settings_dir = Path.cwd() / "settings/settings.json"

    def __call__(self) -> None:
        if not self.settings_dir.exists():
            print("Settings do not exist. Adding defaults...")
            self._create_settings()
            return
        
        print("Validating settings...")
        self._load()
        self._validate_data_presence()
        self._remove_deprecated_keys()
        self._dump()
        print("Settings validated!")

    def _validate_data_presence(self, expected=None, data=None) -> None:
        data = data or self.data
        expected = expected or self.EXPECTED_CONFIG
        
        for k, v in expected.items():
            if k not in data:
                print(f"Adding '{k}', default value {v}...")
                data[k] = v

            elif isinstance(v, dict):
                self._validate_data_presence(v, data[k])

    def _remove_deprecated_keys(self, expected=None, data=None) -> None:
        data = data or self.data
        expected = expected or self.EXPECTED_CONFIG

        to_delete = []
        for k, v in data.items():
            if k not in expected:
                to_delete.append(k)

            elif isinstance(v, dict):
                self._remove_deprecated_keys(expected[k], v)

        for k in to_delete:
            print(f"Removing '{k}'...")
            data.pop(k)

    def _create_settings(self) -> None:
        self.settings_dir.parent.mkdir(exist_ok=True)
        with open(self.settings_dir, "w") as f:
            json.dump(self.EXPECTED_CONFIG, f, indent=4)

    def _load(self) -> None:
        with open(self.settings_dir) as f:
            self.data: dict = json.load(f)

    def _dump(self) -> None:
        with open(self.settings_dir, "w") as f:
            json.dump(self.data, f, indent=4)




