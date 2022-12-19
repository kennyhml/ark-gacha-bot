from typing import Optional, Protocol
from ark.inventories.inventory import Inventory
from bot.ark_bot import ArkBot


class Structure(ArkBot):

    def __init__(
        self, name: str, action_wheel: str, max_slots: Optional[str] = None
    ) -> None:
        super().__init__()
        self.inventory = Inventory(name, action_wheel, max_slots)
