import math
from typing import Optional

import pyautogui as pg  # type: ignore[import]

from ark.exceptions import InventoryNotAccessibleError, NoItemsAddedError
from ark.inventories.inventory import Inventory
from ark.items import Item


class PlayerInventory(Inventory):
    """Represents the player inventory in ark.

    Handles player inventory related actions such as transferring items,
    dropping all items and opening crystals.

    Inherits from the `Inventory` class.
    """

    INVENTORY_REGION = (110, 90, 180, 60)
    SEARCHBAR = (180, 180)
    TRANSFER_ALL = (350, 180)
    DROP_ALL = (400, 180)
    ADDED_REGION = (10, 1000, 220, 80)
    ITEM_REGION = (110, 30, 580, 1000)
    CREATE_FOLDER = (513, 189)
    FIRST_SLOT = (166, 280)

    def __init__(self):
        super().__init__("Player", None)

    def has_item(self, item: Item) -> bool:
        """Checks if the inventory contains the given item."""
        return (
            self.locate_template(
                item.inventory_icon, region=self.ITEM_REGION, confidence=0.8
            )
            is not None
        )

    def find_item(self, item: Item) -> tuple | None:
        """Returns the position of the given item within the inventory."""
        return self.locate_template(
            item.inventory_icon, region=self.ITEM_REGION, confidence=0.8
        )

    def item_added(self) -> bool:
        """Checks if an item was added by matching for the added template"""
        return self.locate_template(
            f"templates/added.png", region=self.ADDED_REGION, confidence=0.7
        )

    def await_items_added(self) -> None:
        """Waits for items to be added to the inventory"""
        c = 0
        while not self.item_added():
            c += 1
            self.sleep(0.1)
            if c > 300:
                raise NoItemsAddedError("No Items added after 30 seconds!")

    def open(self) -> None:  # type: ignore[override]
        """Opens the inventory using the specified keybind.
        Times out after 30 seconds of unsuccessful attempts raising
        a `TimeoutError`.
        """
        c = 0
        while not self.is_open():
            c += 1
            self.press(self.keybinds.inventory)
            self.sleep(1.5)

            if c > 20:
                raise InventoryNotAccessibleError(f"Failed to open {self._name}!")

    def transfer_amount(self, item: Item, amount: int) -> None:
        """Transfers the amount of the given item into the target inventory.
        After each transfer, a check on the amount is made that may cancel the transfers if
        the OCR'd amount is in a valid range.

        Parameters:
        -----------
        item :class:`str`:
            The item to search for before transferring

        amount :class:`int`:
            The quantity of items to be transferred

        TODO: Make it more precise for smaller amounts
        """
        # make sure we dont transfer any other items
        self.search_for(item)

        # get total row transfers, add a little buffer for lag (1.5 by default)
        total_transfers = round(
            (int(math.ceil(amount / 100.0)) * 100 / item.stack_size) / 6 * 2
        )

        # transfer the items
        for _ in range(total_transfers):
            for pos in [(167 + (i * 95), 282) for i in range(6)]:
                pg.moveTo(pos)
                pg.press("t")

                # OCR the total amount transferred, None if undetermined
                transferred = self.get_amount_transferred()
                if not transferred:
                    continue

                # if the amount of items we transferred makes sense we can cancel
                if amount <= transferred <= amount + 3000:
                    return

    def transfer_all(self, inventory: Inventory, item: Optional[Item | str] = None):
        """Transfers all of the given item into the target inventory

        Parameters:
        -----------
        inventory: :class:`Inventory`:
            The inventory to receive the items

        item: :class:`Item`:
            The item to search for
        """
        if not inventory.is_open():
            print(
                f"{inventory._name} could not be found!\n"
                f'Theres no inventory to transfer "{item}" to!'
            )
            return
        if item:
            self.search_for(item)
        self.click_transfer_all()

    def pellets_left_to_tranfer(self) -> bool:
        """Checks if there are any pellets left to even transfer,
        we wouldnt wanna waste time clicking empty slots RIGHT @SLEEPY!!?"""
        return (
            self.locate_template(
                "templates/inventory_pellet.png",
                region=(116, 700, 95, 90),
                confidence=0.8,
            )
            is not None
        )

    def take_pellets(self, transfer_back: int = 8) -> bool:
        """Transfers some pellets into another inventory, likely a Gacha."""
        # ensure we even have pellets to transfer
        if not self.pellets_left_to_tranfer():
            return False

        # start transferring pellets, keep track of rows
        self.click_at(167, 745)
        rows = 0
        for _ in range(transfer_back):
            for i in range(6):
                self.move_to(167 + (i * 95), 745)
                pg.press("t")

            rows += 1
            # check again if we ran out of pellets yet
            if not self.pellets_left_to_tranfer():
                break
        return True
