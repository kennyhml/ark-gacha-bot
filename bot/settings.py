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
    tower_name: str
    load_method: str
    abberation_mode: bool
    account_name: str
    afk_bed: str
    bed_x: int
    bed_y: int
    crystal_prefix: str
    crystal_beds: int
    crystal_interval: int
    seed_prefix: str
    seed_beds: int
    drop_suits: bool
    drop_items: list
    keep_items: list
    game_launcher: str
    dedis_amount: int
    open_logs: bool
    log_interval: int
    pickup_method: str
    poly_vaults: str
    save_time: int
    server_name: str
    server_search: str
    suicide_bed: str
    suicide_interval: int
    suicide_method: str
    turn_direction: str
    single_player: bool = False

@dataclass
class DiscordSettings:
    webhook_gacha: str
    webhook_alert: str
    webhook_logs: str
    tag_level_0: str
    tag_level_1: str
    tag_level_2: str
    tag_level_3: str
    tag_level_4: str
    tag_level_5: str




    
    
    



