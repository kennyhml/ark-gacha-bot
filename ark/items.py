"""
Ark API module representing items in ark.

Item is a dataclass containing the items name, inventory icon, 
added icon, added text and minimum deposit length (optional).

Items objects can be created here if they are needed in multiple modules,
or in their needed module directly.
"""
from dataclasses import dataclass
from pickletools import stackslice
from typing import Optional


@dataclass
class Item:
    """Represents an ark item"""

    name: str
    search_name: str
    stack_size: int
    inventory_icon: str
    added_icon: Optional[str] = None
    added_text: Optional[str] = None
    min_len_deposits: Optional[int] = None

    def __hash__(self):
        return hash(self.name)


DUST = Item(
    name="Element Dust",
    search_name="dust",
    stack_size=1000,
    inventory_icon="templates/inventory_dust.png",
    added_icon="templates/dust_deposited.png",
    added_text="templates/dust_text.png",
    min_len_deposits=4,
)


BLACK_PEARL = Item(
    name="Black Pearl",
    search_name="black",
    stack_size=200,
    inventory_icon="templates/inventory_black_pearl.png",
    added_icon="templates/black_pearl_deposited.png",
    added_text="templates/black_pearl_text.png",
    min_len_deposits=2,
)


Y_TRAP = Item(
    name="Y Trap",
    search_name="trap",
    stack_size=10,
    inventory_icon="templates/inventory_ytrap.png",
    added_text="templates/y_trap_added.png",
    added_icon="templates/plant_species_y_trap.png"
)

PELLET = Item(
    name="Snow Owl Pellet",
    search_name="pellet",
    stack_size=1,
    inventory_icon="templates/inventory_pellet.png",
)

GACHA_CRYSTAL = Item(
    name="Gacha Crystal",
    search_name="gacha",
    stack_size=1,
    inventory_icon="templates/inventory_gacha_crystal.png",
)

RIOT_HELMET = Item(
    name="Riot Helmet",
    search_name="helmet",
    stack_size=1,
    inventory_icon="templates/inventory_riot_helmet.png",
)

RIOT_CHEST = Item(
    name="Riot Chest",
    search_name="chest",
    stack_size=1,
    inventory_icon="templates/inventory_riot_chest.png",
)

RIOT_LEGGS = Item(
    name="Riot Leggings",
    search_name="legg",
    stack_size=1,
    inventory_icon="templates/inventory_riot_leggs.png",
)

RIOT_GAUNTLETS = Item(
    name="Riot Gauntlets",
    search_name="gaunt",
    stack_size=1,
    inventory_icon="templates/inventory_riot_gauntlets.png",
)

RIOT_BOOTS = Item(
    name="Riot Boots",
    search_name="boots",
    stack_size=1,
    inventory_icon="templates/inventory_riot_boots.png",
)

CRYSTAL = Item(
    name="Crystal",
    search_name="crystal",
    stack_size=100,
    inventory_icon="templates/inventory_crystal.png",
)

ASSAULT_RIFLE = Item(
    name="Assault Rifle",
    search_name="ass",
    stack_size=1,
    inventory_icon="templates/inventory_assault_rifle.png",
)

PUMPGUN = Item(
    name="Pump-Action Shotgun",
    search_name="pump",
    stack_size=1,
    inventory_icon="templates/inventory_pumpgun.png",
)

METAL_INGOT = Item(
    name="Ingot",
    search_name="ingot",
    stack_size=300,
    inventory_icon="templates/inventory_metal_ingot.png",
    added_icon="templates/ingot_icon.png",
    added_text="templates/ingot_text.png"
)

FABRICATED_SNIPER = Item(
    name="Fabricated Sniper Rifle",
    search_name="sniper",
    stack_size=1,
    inventory_icon="templates/inventory_fabricated_sniper.png",
)

FABRICATED_PISTOL = Item(
    name="Fabricated Pistol",
    search_name="pistol",
    stack_size=1,
    inventory_icon="templates/inventory_fabricated_pistol.png",
)

AUTO_TURRET = Item(
    name="Auto Turret",
    search_name="auto turret",
    stack_size=1,
    inventory_icon="templates/auto_turret.png",
)

HEAVY_AUTO_TURRET = Item(
    name="Heavy Auto Turret",
    search_name="heavy",
    stack_size=1,
    inventory_icon="templates/inventory_heavy_auto_turret.png",
)

MINER_HELMET = Item(
    name="Miner Helmet",
    search_name="miner helmet",
    stack_size=1,
    inventory_icon="templates/miner_helmet.png",
)

MEJOBERRY = Item(
    name="Mejoberry",
    search_name="mejoberry",
    stack_size=100,
    inventory_icon="templates/mejoberries.png",
)

RAW_MEAT = Item(
    name="Raw Meat",
    search_name="meat",
    stack_size=1,
    inventory_icon="templates/raw_meat.png",
)

FLINT = Item(
    name="Flint",
    search_name="flint",
    stack_size=100,
    inventory_icon="templates/inventory_flint.png",
)

STONE = Item(
    name="Stone",
    search_name="stone",
    stack_size=100,
    inventory_icon="templates/inventory_stone.png",
    added_icon="templates/stone_icon.png",
    added_text="templates/stone_text.png"
)

FUNGAL_WOOD = Item(
    name="Fungal wood",
    search_name="wood",
    stack_size=100,
    inventory_icon="templates/inventory_fungal_wood.png",
)

PASTE = Item(
    name="Paste",
    search_name="paste",
    stack_size=100,
    inventory_icon="templates/inventory_paste.png",
    added_icon="templates/paste_icon.png",
    added_text="templates/paste_text.png"
)

SILICA_PEARL = Item(
    name="Silica Pearl",
    search_name="pearls",
    stack_size=100,
    inventory_icon="templates/inventory_silica_pearl.png",
    added_icon="templates/pearls_icon.png",
    added_text="templates/pearls_text.png"

)

ELECTRONICS = Item(
    name="Electronics",
    search_name="electronics",
    stack_size=100,
    inventory_icon="templates/inventory_electronics.png",
    added_icon="templates/electronics_icon.png",
    added_text="templates/electronics_text.png"
)

HIDE = Item(
    name="Hide",
    search_name="hide",
    stack_size=100,
    inventory_icon="templates/inventory_hide.png",
)

POLYMER = Item(
    name="Polymer",
    search_name="poly",
    stack_size=100,
    inventory_icon="templates/inventory_poly.png",
)


RIOT = Item(
    name="Riot",
    search_name="riot",
    stack_size=1,
    inventory_icon="templates/inventory_riot_chest.png",
)

FAB = Item(
    name="Fab",
    search_name="fab",
    stack_size=1,
    inventory_icon="templates/inventory_fabricated_sniper.png",
)

BEHEMOTH_GATEWAY = Item(
    name="Behemoth Gateway",
    search_name="behemoth",
    stack_size=100,
    inventory_icon="templates/inventory_behemoth_gateway.png",
)

BEHEMOTH_GATE = Item(
    name="Behemoth Gate",
    search_name="behemoth",
    stack_size=100,
    inventory_icon="templates/inventory_behemoth_gate.png",
)


TREE_PLATFORM = Item(
    name="Tree Platform",
    search_name="tree",
    stack_size=100,
    inventory_icon="templates/inventory_tree_platform.png",
)

METAL_GATEWAY = Item(
    name="Metal Gateway",
    search_name="gateway",
    stack_size=100,
    inventory_icon="templates/inventory_metal_gateway.png",
)

METAL_GATE = Item(
    name="Metal Gate",
    search_name="gate",
    stack_size=100,
    inventory_icon="templates/inventory_metal_gate.png",
)

SPOILED_MEAT = Item(
    name="Spoiled Meat",
    search_name="spoiled",
    stack_size=100,
    inventory_icon="templates/inventory_spoiled_meat.png",
)

GASOLINE = Item(
    name="Gasoline",
    search_name="gasoline",
    stack_size=100,
    inventory_icon="templates/inventory_gasoline.png"


)

CHARCOAL = Item(
    name="Charcoal",
    search_name="coal",
    stack_size=100,
    inventory_icon="templates/inventory_charcoal.png"

)

SPARKPOWDER = Item(
    name="Sparkpowder",
    search_name="spark",
    stack_size=100,
    inventory_icon="templates/inventory_sparkpowder.png"
)



GUNPOWDER = Item(
    name="Gunpowder",
    search_name="gunpowder",
    stack_size=100,
    inventory_icon="templates/inventory_gunpowder.png"
)

ARB = Item(
    name="Advanced Rifle Bullet",
    search_name="advanced",
    stack_size=100,
    inventory_icon="templates/inventory_arb.png",
    added_icon="templates/arb_icon.png",
    added_text="templates/arb_text.png"
)