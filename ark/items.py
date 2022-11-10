"""
Ark API module representing items in ark.

Item is a dataclass containing the items name, inventory icon, 
added icon, added text and minimum deposit length (optional).

Items objects can be created here if they are needed in multiple modules,
or in their needed module directly.
"""
from dataclasses import dataclass


@dataclass
class Item:
    """Represents an ark item"""

    name: str
    inventory_icon: str
    added_icon: str
    added_text: str
    min_len_deposits: int = None


dust = Item(
    name="Element Dust",
    inventory_icon=None,
    added_icon="templates/dust_deposited.png",
    added_text="templates/dust_text.png",
    min_len_deposits=4,
)


black_pearl = Item(
    name="Black Pearl",
    inventory_icon=None,
    added_icon="templates/black_pearl_deposited.png",
    added_text="templates/black_pearl_text.png",
    min_len_deposits=2,
)


y_trap = Item(
    name="Y Trap",
    inventory_icon="templates/ytrap.png",
    added_icon=None,
    added_text=None,
)

pellet = Item(
    name="Snow Owl Pellet",
    inventory_icon="templates/pellet.png",
    added_icon=None,
    added_text=None,
)

gacha_crystal = Item(
    name="Gacha Crystal",
    inventory_icon="templates/gacha_crystal.png",
    added_icon=None,
    added_text=None,
)

riot_helmet = Item(
    name="Riot Helmet",
    inventory_icon="templates/riot_helmet.png",
    added_icon=None,
    added_text=None,
)

riot_chest = Item(
    name="Chest",
    inventory_icon="templates/riot_chest.png",
    added_icon=None,
    added_text=None,
)

riot_leggs = Item(
    name="Leggings",
    inventory_icon="templates/riot_leggs.png",
    added_icon=None,
    added_text=None,
)

riot_gauntlets = Item(
    name="Gauntlets",
    inventory_icon="templates/riot_gauntlets.png",
    added_icon=None,
    added_text=None,
)

riot_boots = Item(
    name="Boots",
    inventory_icon="templates/riot_boots.png",
    added_icon=None,
    added_text=None,
)

crystal = Item(
    name="Crystal",
    inventory_icon="templates/crystal.png",
    added_icon=None,
    added_text=None,
)

assault_rifle = Item(
    name="Assault",
    inventory_icon="templates/assault_rifle.png",
    added_icon=None,
    added_text=None,
)

pumpgun = Item(
    name="Pump",
    inventory_icon="templates/pumpgun.png",
    added_icon=None,
    added_text=None,
)

metal_ingot = Item(
    name="Ingot",
    inventory_icon="templates/metal_ingot.png",
    added_icon=None,
    added_text=None,
)

fabricated_sniper = Item(
    name="Sniper",
    inventory_icon="templates/fabricated_sniper.png",
    added_icon=None,
    added_text=None,
)

fabricated_pistol = Item(
    name="Pistol",
    inventory_icon="templates/fabricated_pistol.png",
    added_icon=None,
    added_text=None,
)

auto_turret = Item(
    name="Auto Turret",
    inventory_icon="templates/auto_turret.png",
    added_icon=None,
    added_text=None,
)

heavy_auto_turret = Item(
    name="Heavy Auto Turret",
    inventory_icon="templates/heavy_auto_turret.png",
    added_icon=None,
    added_text=None,
)

miner_helmet = Item(
    name="Miner Helmet",
    inventory_icon="templates/miner_helmet.png",
    added_icon=None,
    added_text=None,
)
