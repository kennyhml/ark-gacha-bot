"""
Ark API module representing inventories in ark.
The `Inventory` parent class contains methods that make it easy to derive other inventories.
"""

import math
import os
from typing import Literal, Optional

import pyautogui as pg  # type: ignore[import]
import pydirectinput as input  # type: ignore[import]
import win32clipboard  # type: ignore[import]
from pytesseract import pytesseract as tes  # type: ignore[import]

from ark.exceptions import (
    InventoryNotAccessibleError,
    InventoryNotClosableError,
    ReceivingRemoveInventoryTimeout,
)
from ark.items import Item
from bot.ark_bot import ArkBot


class Inventory(ArkBot):
    """Represents the ark inventory, inherits from `ArkBot`.

    Parameters:
    -----------
    entity :class:`str`:
        The name of the structure / dino the inventory belongs to

    action_wheel_img :class:`str`:
        The path to the action wheel image of the item

    max_slots :class:`str`: [Optional]
        An image path containing the image of the max capacity.

    TODO:
    Make an action wheel class, reduce coupling a good amount.

    max_slots should be defined in a `Structure` rather than inventory
    because shit like dinos doesnt have a max_slot so it doesnt make a
    whole lot of sense despite being optional.
    """

    INVENTORY_REGION = (1235, 88, 184, 60)
    SEARCHBAR = (1300, 190)
    TRANSFER_ALL = (1425, 190)
    CRAFTING_tab = (1716, 118)
    INVENTORY_TAB = (1322, 118)
    ADDED_REGION = (40, 1020, 360, 60)
    ITEM_REGION = (1230, 220, 580, 720)
    DROP_ALL = (1477, 187)
    CREATE_FOLDER = (1584, 187)
    FIRST_SLOT = (1292, 294)

    def __init__(
        self, entity_name: str, action_wheel_img: str, max_slots: Optional[str] = None
    ) -> None:
        super().__init__()
        self._name = entity_name
        self._action_wheel_img = action_wheel_img
        self._max_slots_img = max_slots

    def click_drop_all(self) -> None:
        """Clicks the drop all button at the classes drop all position"""
        self.click_at(self.DROP_ALL, delay=0.2)

    def click_transfer_all(self) -> None:
        """Clicks the transfer all button at the classes transfer all position"""
        self.click_at(self.TRANSFER_ALL, delay=0.2)

    def open_craft(self) -> None:
        """Opens the crafting tab assuming the inventory is already open"""
        self.click_at(self.CRAFTING_tab, delay=0.3)

    def close_craft(self) -> None:
        """Opens the inventory tab assuming the inventory is already open"""
        self.click_at(self.INVENTORY_TAB, delay=0.3)

    def drop_all_items(self, item: Item | str) -> None:
        """Searches for the given item and drops all of it"""
        self.search_for(item)
        self.click_drop_all()

    def select_first_slot(self) -> None:
        """Moves to the first slot"""
        self.move_to(*self.FIRST_SLOT)

    def popcorn(self, item: Item) -> None:
        """Searches for the given item and popcorns it until there is none left."""
        self.search_for(item)
        self.select_first_slot()
        while self.has_item(item):
            self.press("o")

    def count_item(self, item: Item) -> int:
        """Returns the amount of stacks of the given item located within the inventory."""
        return len(
            self.locate_all_template(
                item.inventory_icon, region=self.ITEM_REGION, confidence=0.8
            )
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

    def is_open(self) -> bool:
        """Checks if the inventory is open."""
        return (
            self.locate_template(
                "templates/inventory.png", region=self.INVENTORY_REGION, confidence=0.8
            )
            is not None
        )

    def has_item(self, item: Item) -> bool:
        """Checks if the player inventory has the passed item.
        Beware that we grayscale the item to make it compatible
        across qualities.

        Parameters:
        ------------
        item :class:`Item`:
            The item object of the item to check for

        Returns whether the item is in the inventory or not.
        """
        return (
            self.locate_template(
                item.inventory_icon,
                region=self.ITEM_REGION,
                confidence=0.8,
                grayscale=True,
            )
            is not None
        )

    def search_for(self, item: Item | str) -> None:
        """Searches for a term in the target inventory using pyautogui typewrite"""
        self.check_status()

        # write the name into the search bar
        if isinstance(item, str):
            self.click_search()
            pg.typewrite(item, interval=0.001)
        else:
            self.click_search(delete_prior=item.search_name != "trap")
            pg.typewrite(item.search_name.lower(), interval=0.001)

        # escape out of the searchbar so presing f closes the inventory
        self.press("esc")

    def take_all_items(self, item: Item) -> None:
        """Searches the given item and takes all.

        Parameters:
        -----------
        item :class:`Item`:
            The item object to search for
        """
        # search for the item and hit take all
        self.search_for(item)
        self.click_transfer_all()

    def take_one_item(self, item: Item, slot: int) -> None:
        """Searches the given item and takes one.

        Parameters:
        -----------
        item :class:`Item`:
            The item object to search for

        slot :class:`int`:
            The slot to take from (in case the inventory has a folder)
            either 1 or 2
        """
        # search for the item and hit take all
        self.search_for(item)
        self.sleep(0.2)

        slots = {1: (1288, 285), 2: (1384, 281)}
        self.move_to(*slots[slot])
        pg.doubleClick(button="left", interval=0.2)

    def craft(self, item: Item, amount: int) -> None:
        """Crafts the given amount of the given item. Spams 'A' if
        there is more than 50 to craft.
        """
        self.search_for(item)
        self.click_at(1294, 290, delay=1)

        if amount < 50:
            for _ in range(amount):
                self.press("e")
                self.sleep(0.3)
            return

        for _ in range(math.ceil(amount / 100)):
            self.press("a")
            self.sleep(0.5)

    def get_slots(self) -> int:
        """Attempts to OCR the amount of slots occupied in the structure.
        Returns 0 upon failure.
        """
        slots = self.grab_screen((1090, 503, 41, 15))
        masked = self.denoise_text(
            slots, (251, 227, 124), variance=30, upscale=True, upscale_by=3
        )
        result = tes.image_to_string(
            masked,
            config="-c tessedit_char_whitelist=0123456789/ --psm 7 -l eng",
        ).rstrip()
        print(result)
        if not result:
            return 0

        if result[-1] == "/":
            result = result[:-1].replace("/", "7")

        # replace mistaken "0"s, strip off newlines
        return result.replace("O", "0") or 0

    def get_stack_index(self) -> int:
        """Returns the number of the crop plot in the stack by checking for
        the folder name from AAA to HHH, being 1 to 9."""

        options = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH"]
        for _ in range(3):
            for index, option in enumerate(options, start=1):
                if self.locate_template(
                    f"templates/folder_{option}.png",
                    region=(1240, 290, 55, 34),
                    confidence=0.9,
                ):
                    return index
            self.sleep(0.5)

        raise Exception("Index not determined")

    def create_folder(self, name: str) -> None:
        """Creates a folder in the inventory at the classes folder button"""
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(name, win32clipboard.CF_TEXT)
        win32clipboard.CloseClipboard()

        self.click_at(1585, 187)
        self.sleep(0.3)
        pg.hotkey("ctrl", "v", interval=0.2)
        self.sleep(0.3)
        self.click_at(961, 677)
        self.sleep(0.5)
        self.click("left")

    def is_full(self) -> bool:
        """Checks if the vault is full, raises an `AttributeError` if no
        max slot image path was defined."""
        if not self._max_slots_img:
            raise AttributeError(
                f"You need to define a 'max_slot_img' for '{self._name}' in order to use this method."
            )
        return (
            self.locate_template(
                self._max_slots_img, region=(1074, 500, 60, 23), confidence=0.9
            )
            is not None
        )

    def receiving_remote_inventory(self) -> bool:
        """Checks if the 'Receiving Remote Inventory' text is visible."""
        return (
            self.locate_template(
                "templates/remote_inventory.png",
                region=(1346, 563, 345, 43),
                confidence=0.8,
            )
            is not None
        )

    def get_transferred_frame(
        self, item: Item, mode: Literal["rm", "add"] = "rm"
    ) -> tuple | None:
        if not item.added_icon:
            raise Exception

        ytrap_position = self.locate_template(
            item.added_icon, region=(0, 970, 160, 350), confidence=0.7
        )

        if not ytrap_position:
            return None

        # get our region of interest
        text_start_x = ytrap_position[0] + ytrap_position[2]
        if mode == "rm":
            text_end = text_start_x + self.convert_width(130), ytrap_position[1]
        else:
            text_end = text_start_x + self.convert_width(95), ytrap_position[1]

        roi = (*text_end, self.convert_width(290), self.convert_height(25))

        if not item.added_text:
            raise Exception(f"You did not define an 'added_text' for {item}!")

        # find the items name to crop out the numbers
        name_text = self.locate_template(
            item.added_text, region=roi, confidence=0.7, convert=False
        )
        if not name_text:
            return None

        # get our region of interest (from end of "Removed:" to start of "Element")
        roi = (
            *text_end,
            self.convert_width(int(name_text[0] - text_end[0])),
            self.convert_height(25),
        )
        return roi

    def get_amount_transferred(
        self, item: Item, mode: Literal["rm", "add"] = "rm"
    ) -> int:
        """OCRs the amount transferred into the inventory by checking for the
        amount on the lefthand side of the screen."""
        # prepare the image
        for _ in range(10):
            roi = self.get_transferred_frame(item, mode)
            if roi:
                break
            self.sleep(0.1)

        if not roi:
            return 0

        img = self.grab_screen(roi, convert=False)
        img = self.denoise_text(
            img, denoise_rgb=(255, 255, 255), variance=10, upscale=True, upscale_by=3
        )
        # get the raw tesseract result
        raw_result = tes.image_to_string(
            img,
            config="-c tessedit_char_whitelist='0123456789liIxObL ' --psm 7 -l eng",
        )

        try:
            # replace all the mistaken "1"s
            for char in ["I", "l", "i", "b", "L"]:
                raw_result = raw_result.replace(char, "1")

            # replace mistaken "0"s, strip off newlines
            filtered = raw_result.replace("O", "0").replace("~", "x").rstrip()

            # find the x to slice out the actual number
            x = filtered.find("x")
            if x == -1 or not filtered or filtered == "x":
                return 0
            return int(filtered[:x])

        except:
            return 0

    def await_receiving_remove_inventory(self) -> None:
        """Waits until 'Receiving Remote Inventory' disappears.

        Raises:
        ------------
        `ReceivingRemoveInventoryTimeout` if it did not disappear after 30
        seconds, usually indicating a server crash.
        """
        c = 0
        while self.receiving_remote_inventory():
            self.sleep(0.1)
            c += 1
            if c > 300:
                raise ReceivingRemoveInventoryTimeout(
                    "Timed out waiting to receive remote inventory!"
                )

    def await_open(self) -> bool:
        """Waits for the inventory to be open, for time efficiency.

        Returns `True` if the inventory opened within 5 second else `False`
        """
        c = 0
        while not self.is_open():
            self.sleep(0.1)
            c += 1
            if c > 40:
                return False
        return True

    def await_closed(self) -> bool:
        """Waits for the inventory to be closed, for time efficiency.

        Returns `True` if the inventory closed within 5 second else `False`
        """
        c = 0
        while self.is_open():
            c += 1
            self.sleep(0.1)
            if c > 40:
                return False
        return True

    def in_access_range(self) -> bool:
        """Uses the action wheel to check if a structure or dinosaur is within
        access range to determine if we are unable to open it because of lag or
        if we are just not looking at it. Useful for time efficiency on crop plots.

        Returns `True` if the action wheel displays the structure / dinos name.
        """
        with pg.hold("e"):
            self.sleep(1)
            return (
                self.locate_template(
                    f"templates/{self._action_wheel_img}.png",
                    region=(840, 425, 240, 230),
                    confidence=0.7,
                )
                is not None
            )

    def open(self, default_key: bool = True) -> None:
        """Opens the inventory using the 'target inventory' keybind.

        If the inventory did not opened within 5 seconds, it will use the
        action wheel to determine if we are able to open it.

        Raises:
        ----------
        `InventoryNotAccessibleError` if the structure / dino name does not
        appear in the action wheel upon checking or if the inventory just cannot
        be opened after 30 seconds, indicating a server or game crash.

        """
        c = 0
        while not self.is_open():
            c += 1
            # wait for 1s if the crop plot opens
            self.press(
                self.keybinds.target_inventory if default_key else self.keybinds.use
            )
            if self.await_open():
                break

            # 10 seconds passed, check if we can access it at all
            if c == 2:
                if not self.in_access_range():
                    raise InventoryNotAccessibleError(f"Failed to access {self._name}!")

            if c >= 6:
                raise InventoryNotAccessibleError(f"Failed to access {self._name}!")

        self.await_receiving_remove_inventory()

    def close(self) -> None:
        """Closes the inventory using the 'target inventory' keybind.

        Raises:
        ----------
        `InventoryNotClosableError` if the inventory did not close
        within 30 seconds, indicating a server / game crash.
        """
        c = 0
        while self.is_open():
            c += 1
            self.press(self.keybinds.target_inventory)
            if self.await_closed():
                break

            if c >= 6:
                raise InventoryNotClosableError(f"Failed to close {self._name}!")
        self.sleep(0.3)

    def click_search(self, delete_prior: bool = True) -> None:
        """Clicks into the searchbar"""
        self.click_at(self.SEARCHBAR)
        if not delete_prior:
            return

        input.keyDown("ctrl")
        self.sleep(0.1)
        input.press("a")
        input.keyUp("ctrl")

    def delete_search(self) -> None:
        """Deletes the search"""
        self.click_search(delete_prior=True)
        self.press("backspace")
        self.press("esc")

    def can_craft(self, item: Item) -> bool:
        """Checks if the given item can be crafted."""
        self.search_for(item)
        self.sleep(0.5)
        return (
            self.locate_template(item.inventory_icon, self.ITEM_REGION, confidence=0.75)
            is not None
        )
