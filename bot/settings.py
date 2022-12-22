from dataclasses import dataclass


@dataclass
class Keybinds:
    console: str
    crouch: str
    drop: str
    inventory: str
    prone: str
    target_inventory: str
    toggle_hud: str
    use: str
    logs: str
    hotbar_0: str
    hotbar_1: str
    hotbar_2: str
    hotbar_3: str
    hotbar_4: str
    hotbar_5: str
    hotbar_6: str
    hotbar_7: str
    hotbar_8: str
    hotbar_9: str

@dataclass
class TowerSettings:
    account_name: str
    bed_position: list
    crystal_prefix: str
    crystal_beds: int
    seed_prefix: str
    seed_beds: int
    berry_prefix: str
    berry_beds: int
    meat_prefix: str
    meat_beds: int
    crystal_interval: int
    drop_items: list
    keep_items: list
    game_launcher: str
    server_name: str
    server_search: str
    pod_name: str
    stryder_depositing: bool

@dataclass
class DiscordSettings:
    webhook_gacha: str
    webhook_alert: str
    webhook_logs: str




    
    
    



