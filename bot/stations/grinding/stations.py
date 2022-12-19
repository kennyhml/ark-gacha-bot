from enum import Enum
from typing import Literal

from ark.items import (CRYSTAL, ELECTRONICS, HIDE, METAL_INGOT, PASTE,
                       SILICA_PEARL, Item)


class Stations(str, Enum):
    """An enum class representing the different stations to
    avoid typos."""

    GRINDER = "Grinder"
    EXO_MEK = "Exo Mek"
    VAULT = "Vault"
    CRYSTAL = "Crystal"
    HIDE = "Hide"
    INGOTS = "Ingot"
    ELECTRONICS = "Electronics"
    PEARLS = "Pearls"
    PASTE = "Paste"
    GEAR_VAULT = "Gear Vault"
    
    @staticmethod
    def from_item(item: Item) -> str:
        """Returns the station corresponding to the item"""
        if item not in ITEM_TO_STATION:
            raise
        return ITEM_TO_STATION[item]

ITEM_TO_STATION: dict[Item, Stations] = {
    PASTE: Stations.PASTE,
    ELECTRONICS: Stations.ELECTRONICS,
    METAL_INGOT: Stations.INGOTS,
    HIDE: Stations.HIDE,
    SILICA_PEARL: Stations.PEARLS,
    CRYSTAL: Stations.CRYSTAL,
}


