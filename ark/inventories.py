"""
Ark API module representing inventories in ark.

The `Inventory` parent class contains methods that make it easy to derive other inventories.

The `PlayerInventory` class derives from the `Inventory` class, mainly checking the left side instead.

All sub-classes in this module derive from the `Inventory` class.
"""
import pyautogui as pg
import pydirectinput as input

from pytesseract import pytesseract as tes

from ark.exceptions import (
    InventoryNotAccessibleError,
    InventoryNotClosableError,
    NoItemsDepositedError,
    ReceivingRemoveInventoryTimeout,
    NoGasolineError,
)
from ark.items import Item, pellet
from bot.ark_bot import ArkBot
import math


class Inventory(ArkBot):
    """Represents the ark inventory, inherits from `ArkBot`.

    Parameters:
    -----------
    entity :class:`str`:
        The name of the structure / dino the inventory belongs to

    action_wheel_img :class:`str`:
        The path to the action wheel image of the item

    """

    INVENTORY_REGION = (1235, 88, 184, 60)
    SEARCHBAR = (1300, 190)
    TRANSFER_ALL = (1425, 190)
    ADDED_REGION = (40, 1020, 360, 60)
    ITEM_REGION = (1230, 220, 580, 720)
    DROP_ALL = (1477, 187)

    def __init__(self, entity, action_wheel_img):
        super().__init__()
        self._name = entity
        self._action_wheel_img = action_wheel_img

    def is_open(self) -> bool:
        """Checks if the inventory is open."""
        return (
            self.locate_template(
                "templates/inventory.png", region=self.INVENTORY_REGION, confidence=0.8
            )
            is not None
        )

    def drop_all(self) -> None:
        self.click_at(self.DROP_ALL)
        
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

    def get_amount_transferred(self) -> int:
        img = self.grab_screen((168, 1036, 217, 33), convert=False)
        img = self.denoise_text(img, denoise_rgb=(255, 255, 255), variance=5)

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
                return None

            return int(filtered[:x])
        except:
            return None

    def has_item(self, item: Item) -> bool:
        """Checks if the player inventory has the passed item.

        Parameters:
        ------------

        item :class:`Item`:
            The item object of the item to check for

        Returns:
        ------------
        `True` if the item was found else `False`
        """
        return (
            self.locate_template(
                item.inventory_icon if isinstance(item, Item) else item,
                region=self.ITEM_REGION,
                confidence=0.8,
                grayscale=True,
            )
            is not None
        )

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
                raise ReceivingRemoveInventoryTimeout

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

    def open(self) -> None:
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
            self.press(self.keybinds.target_inventory)
            if self.await_open():
                break

            # 10 seconds passed, check if we can access it at all
            if c == 2:
                if not self.in_access_range():
                    raise InventoryNotAccessibleError(self._name)
                print("Timer appears to be popping, or the server is lagging!")

            if c >= 6:
                raise InventoryNotAccessibleError(self._name)

        self.await_receiving_remove_inventory()
        print(f"Opened {self._name}!")

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
                raise InventoryNotClosableError(self._name)
        self.sleep(0.2)

    def click_search(self, delete_prior: bool = True) -> None:
        """Clicks into the searchbar"""
        self.click_at(self.SEARCHBAR)
        if not delete_prior:
            return

        input.keyDown("ctrl")
        self.sleep(0.1)
        input.press("a")
        input.keyUp("ctrl")

    def search_for(self, term: str) -> None:
        """Searches for a term in the target inventory using pyautogui typewrite"""
        self.check_status()

        # double check to ensure the inventory is really open
        # if not self.is_open():
        #    self.open()

        if isinstance(term, Item):
            term = term.name

        # write the name into the search bar
        self.click_search(delete_prior=term != "trap")
        pg.typewrite(term.lower(), interval=0.001)

        # escape out of the searchbar so presing f closes the inventory
        self.press("esc")

    def take_all(self) -> None:
        """Clicks the take all button"""
        self.click_at(self.TRANSFER_ALL)

    def take_all_items(self, item: Item | str) -> None:
        """Searches the given item and takes all.

        Parameters:
        -----------
        item :class:`Item` or `str`:
            The item object or raw string to search for
        """
        # check if we got an item object passed
        if isinstance(item, Item):
            item = item.name

        # search for the item and hit take all
        self.search_for(item)
        self.take_all()

    def take_one_item(self, item: Item | str, slot: int, inventory) -> None:
        """Searches the given item and takes all.

        Parameters:
        -----------
        item :class:`Item` or `str`:
            The item object or raw string to search for
        """
        # check if we got an item object passed
        if isinstance(item, Item):
            item = item.name

        # search for the item and hit take all
        inventory.search_for(item)
        self.sleep(0.2)

        if slot == 1:
            self.move_to(1288, 285)
        elif slot == 2:
            self.move_to(1384, 281)

        pg.doubleClick(button="left", interval=0.2)

    def get_slots(self) -> int:
        slots = self.grab_screen((1090, 503, 41, 15))
        masked = self.denoise_text(slots, (251 ,227, 124), variance=30, upscale=True)

        result = tes.image_to_string(
            masked,
            config="-c tessedit_char_whitelist=0123456789/ --psm 6 -l eng",
        ).rstrip()

        if not result:
            return None

        if result[-1] == "/":
            result = result[:-1].replace("/", "7")

        # replace mistaken "0"s, strip off newlines
        return result.replace("O", "0") or 0

    def open_craft(self) -> None:
        self.click_at(1716, 118, delay=0.3)

    def close_craft(self) -> None:
        self.click_at(1322, 118, delay=0.3)

    def can_craft(self, item: Item) -> bool:
        self.search_for(item.name)
        self.sleep(0.5)
        return (
            self.locate_template(item.inventory_icon, self.ITEM_REGION, confidence=0.75)
            is not None
        )

    def craft(self, item, amount: int) -> None:
        print(f"Crafting {amount} {item}!")
        self.search_for(item)
        self.click_at(1294, 290, delay=1)

        if amount < 30:
            for _ in range(amount):
                self.press("e")
                self.sleep(0.3)
            return

        for _ in range(10):
            self.press("a")
            self.sleep(0.5)


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

    def __init__(self):
        super().__init__("Player", None)

    def open(self) -> None:
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
                raise InventoryNotAccessibleError(self._name)

    def transfer_amount(self, item: str, amount: int, stacksize: int) -> None:
        """Transfers the amount of the given item into the target inventory.
        After each transfer, a check on the amount is made that may cancel the transfers if 
        the OCR'd amount is in a valid range.

        Parameters:
        -----------
        item :class:`str`:
            The item to search for before transferring

        amount :class:`int`:
            The quantity of items to be transferred
        
        stacksize :class:`int`
            The amount the item stacks to to calculate transfers
        """
        # make sure we dont transfer any other items
        self.search_for(item)

        # get total row transfers, add a little buffer for lag (1.5 by default)
        total_transfers = round((int(math.ceil(amount / 100.0)) * 100 / stacksize) / 6 * 2)

        # transfer the items
        for _ in range(total_transfers):
            for pos in [(167 + (i * 95), 282) for i in range(6)]:
                pg.moveTo(pos)
                pg.press("t")

                # OCR the total amount transferred, None if undetermined
                transferred = self.get_amount_transferred()
                if not transferred:
                    continue
                
                print(f"Transferred {transferred}...")

                # if the amount of items we transferred makes sense we can cancel
                if amount <= transferred <= amount + 3000:
                    print("Enough items transferred!")
                    return

    def has_item(self, item: Item) -> bool:
        """Checks if the inventory contains the given item."""
        return (
            self.locate_template(
                item.inventory_icon, region=self.ITEM_REGION, confidence=0.8
            )
            is not None
        )

    def find_item(self, item: Item | str) -> tuple | None:
        """Returns the position of the given item within the inventory."""
        if isinstance(item, Item):
            item = item.inventory_icon
        return self.locate_template(item, region=self.ITEM_REGION, confidence=0.8)

    def find_items(self, item: Item | str) -> tuple | None:
        """Returns all positions of the given item within the inventory."""
        if isinstance(item, Item):
            item = item.inventory_icon

        return self.locate_all_template(item, region=self.ITEM_REGION, confidence=0.8)

    def count_item(self, item: Item | str) -> int:
        """Returns the amount of stacks of the given item located within the inventory."""
        if isinstance(item, Item):
            item = item.inventory_icon

        return len(
            self.locate_all_template(item, region=self.ITEM_REGION, confidence=0.8)
        )

    def has_pellets(self) -> bool:
        """Checks whether the player has pellets."""
        return (
            self.locate_template(
                "templates/pellet.png", region=self.ITEM_REGION, confidence=0.75
            )
            is not None
        )

    def item_added(self) -> bool:
        """Checks if the item was added by matching for the added template"""
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
                raise TimeoutError("No Items added after 30 seconds!")

    def transfer_all(self, inventory: Inventory, item: str = None):
        """Transfers all of the given item into the target inventory

        Parameters:
        -----------
        inventory: :class:`Inventory`:
            The inventory meant to receive the items

        item: :class:`str`:
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
        self.click_at(self.TRANSFER_ALL)
        self.sleep(0.1)

    def pellets_left_to_tranfer(self) -> bool:
        """Checks if there are any pellets left to even transfer,
        we wouldnt wanna waste time clicking empty slots RIGHT @SLEEPY!!?"""
        return (
            self.locate_template(
                "templates/pellet.png", region=(116, 700, 95, 90), confidence=0.8
            )
            is not None
        )

    def transfer_some_pellets(self, inventory: Inventory) -> bool:
        """Transfers some pellets into another inventory, likely a Gacha.

        Parameters:
        -----------
        inventory: :class:`Inventory`:
            The inventory meant to receive the items

        If the given inventory cannot be found, it will skip the task.
        Transferring pellets will be stopped as soon as there is no pellets
        left in the rows we transfer.
        """
        self.check_status()
        # ensure the target inventory is open
        if not inventory.is_open():
            print(
                "Theres no inventory to transfer pellets to!\n"
                f"{inventory._name} inventory could not be found!"
            )
            return

        # ensure we even have pellets to transfer
        if not self.pellets_left_to_tranfer():
            print("Can not transfer any pellets!")
            return

        # start transferring pellets, keep track of rows
        print(f"Transferring Pellets to {inventory._name}...")
        self.click_at(167, 745)
        rows = 0
        for _ in range(6):
            for i in range(6):
                self.move_to(167 + (i * 95), 745)
                pg.press("t")

            rows += 1
            # check again if we ran out of pellets yet
            if not self.pellets_left_to_tranfer():
                print("There is no more pellets to transfer!")
                break

        print(
            f"Transferred approximately {rows} rows of pellets into {inventory._name}!"
        )

    def open_inv_drop_all(self) -> None:
        self.open()
        self.drop_all()
        self.close()

    def drop_all_items(self, item) -> None:
        self.search_for(item)
        self.drop_all()


class CropPlot(Inventory):
    """Represents the Crop Plot in ark.

    Handles the crop plot inventory related actions such as taking traps
    and transferring pellets into the crop plot.

    Inherits from the `Inventory` class.
    """

    ITEMS_REGION = (1230, 225, 590, 380)

    def __init__(self):
        super().__init__("Tek Crop Plot", "tek_crop_plot")

    def has_traps(self) -> bool:
        """Checks if the crop plot has traps so we dont waste time
        searching and taking items that dont exist.
        """
        return (
            self.locate_template(
                "templates/ytrap.png", region=self.ITEMS_REGION, confidence=0.8
            )
            is not None
        )

    def take_traps_put_pellets(self, player_inv: PlayerInventory):
        """Opens the crop plots, takes all traps if there are any
        and hits transfer all to put pellets in.
        """
        try:
            # attempt to open, will raise error if not possible
            self.open()

            # check theres traps in the crop plot
            if self.has_traps():
                self.take_all_items("trap")

            # put pellets in and close
            if player_inv.has_item(pellet):
                player_inv.transfer_all(self)
            self.close()

        except InventoryNotAccessibleError:
            print("Skipping crop plot!")


class Gacha(Inventory):
    """Represents the gacha inventory in ark.

    Handles the gacha inventory related actions such as taking pellets
    and transferring pellets and traps into it.

    Inherits from the `Inventory` class.
    """

    def __init__(self):
        super().__init__("Gacha", "gacha")

    def first_run_take_pellets(self, player_inv: PlayerInventory) -> None:
        """Takes all pellets from the gacha and transfers a few rows
        back into it."""
        self.take_all_items("ll")
        player_inv.await_items_added()
        self.sleep(0.5)
        player_inv.transfer_some_pellets(self)

    def can_access(self) -> bool:
        """Checks if the gacha can be accessed"""
        return (
            self.locate_template(
                "templates/ride.png", region=(0, 0, 1920, 1080), confidence=0.75
            )
            is not None
        )


class DedicatedStorage(Inventory):
    """Represents the Dedicated Storage Box in ark.

    Contains dedi specific methods such as depositing.

    TO-DO: Add methods for withdrawing.
    """

    def __init__(self):
        super().__init__("Dedicated Storage Box", "dedi")

    def can_deposit(self) -> bool:
        return (
            self.locate_template(
                "templates/deposit_all.png", region=(0, 0, 1920, 1080), confidence=0.7
            )
            is not None
        )

    def deposited_items(self) -> bool:
        return (
            self.locate_template(
                "templates/items_deposited.png",
                region=(710, 4, 460, 130),
                confidence=0.75,
            )
            is not None
        )

    def attempt_deposit(
        self, items: list[Item], check_amount: bool = True
    ) -> tuple[str, int]:
        """Attempts to deposit into a dedi until the 'x items deposited.'
        green message appears up top where x can be any number.

        Parameters:
        -----------
        items :class:`list`:
            A list of items where each item is a potentionally deposited item


        Returns:
        -----------
        item :class:`str`:
            The name of the item that was being deposited or was last checked

        amount :class:`int`:
            The quantity of items that were deposited, 0 if none.

        Raises:
        -----------
        `NoItemsDepositedError` if the expected text did not appear after 30 seconds.
        """
        # initial deposit attempt
        self.sleep(0.5)
        self.press(self.keybinds.use)
        c = 0

        # wait until we actually attempted a deposit (lag protection)
        while not self.deposited_items():
            self.sleep(0.1)
            c += 1
            # retry every 3 seconds
            if c % 30 == 0:
                self.press(self.keybinds.use)

            if c > 300:
                raise NoItemsDepositedError("Failed to deposit after 30 seconds!")

        if not check_amount:
            return
        print("Deposited into dedi! Checking...")

        # check for each item
        for item in items:
            if not self.item_deposited(item):
                continue

            # 5 attempts to get a better chance for a good result
            for _ in range(5):
                # get the amount of deposited items of the items we are depositing
                amount = self.get_amount_deposited(item)
                # make sure the amount is actually meaningful so we dont get false matches
                if amount and len(str(amount)) >= item.min_len_deposits:
                    break
            break
        # never got to an item that was deposited, no amount can be determined
        else:
            amount = 0

        # wait for the green text to go away so we can try fresh on the next dedi
        while self.deposited_items():
            self.sleep(0.1)

        return item.name, amount

    def item_deposited(self, item: Item) -> tuple:
        """Checks if the given item has been deposited"""
        return self.locate_template(
            item.added_icon, region=(0, 430, 160, 350), confidence=0.7
        )

    def get_amount_deposited(self, item: Item) -> int:
        """Checks how much of the given item was deposited."""

        # check if any was deposited
        if not (dust_pos := self.item_deposited(item)):
            print(f"No {item.name} was deposited.")
            return 0

        print(f"{item.name} deposited! Attempting to determine amount!")

        # get our region of interest
        text_start_x = dust_pos[0] + dust_pos[2]
        text_end = text_start_x + self.convert_width(130), dust_pos[1]
        roi = (*text_end, self.convert_width(290), self.convert_height(25))

        # find the items name to crop out the numbers
        name_text = self.locate_template(
            item.added_text, region=roi, confidence=0.7, convert=False
        )

        # not worth trying to find out the amount without proper roi
        if not name_text:
            return 0

        # get our region of interest (from end of "Removed:" to start of "Element")
        roi = (
            *text_end,
            self.convert_width(int(name_text[0] - text_end[0])),
            self.convert_height(25),
        )

        # grab the region of interest and apply denoising
        img = self.grab_screen(roi, convert=False)
        img = self.denoise_text(img, denoise_rgb=(255, 255, 255), variance=5)

        raw_result = tes.image_to_string(
            img,
            config="-c tessedit_char_whitelist=0123456789liIxObL --psm 7 -l eng",
        )

        # replace all the mistaken "1"s
        for char in ["I", "l", "i", "b", "L"]:
            raw_result = raw_result.replace(char, "1")

        # replace mistaken "0"s, strip off newlines
        filtered = raw_result.replace("O", "0").rstrip()

        # find the x to slice out the actual number
        x = filtered.find("x")
        if x == -1 or not filtered or filtered == "x":
            return 0

        return int(filtered[:x])

    def can_be_opened(self) -> bool:
        """Checks if the dedi can be opened by attempting to do so"""
        c = 0
        max_time = 5

        while not self.is_open():
            c += 1
            # wait for 1s if the dedi opens
            self.press(self.keybinds.target_inventory)
            if self.await_open():
                break

            if c == 2:
                if not self.in_access_range():
                    return False
                print("Timer appears to be popping!")
                max_time = 30

            if c > max_time:
                return False
        return True


class Vault(Inventory):
    """Represents the vault inventory in ark.

    Is able to check if the vault is full or not.
    """

    def __init__(self):
        super().__init__("Vault", "vault")

    def is_full(self) -> bool:
        """Checks if the vault is full"""
        return (
            self.locate_template(
                "templates/vault_capped.png", region=(1074, 500, 60, 23), confidence=0.9
            )
            is not None
        )


class Grinder(Inventory):
    """Represents the grinder inventory in ark.

    Is able to be turned on and off and grind all.
    """

    def __init__(self):
        super().__init__("Grinder", "grinder")

    def can_turn_on(self) -> bool:
        return (
            self.locate_template(
                "templates/turn_on.png",
                region=(740, 570, 444, 140),
                confidence=0.85,
                grayscale=True,
            )
            is not None
        )

    def is_turned_on(self) -> bool:
        return (
            self.locate_template(
                "templates/turn_off.png",
                region=(740, 570, 444, 140),
                confidence=0.85,
                grayscale=True,
            )
            is not None
        )

    def can_grind(self) -> bool:
        return (
            self.locate_template(
                "templates/grind_all_items.png",
                region=(740, 570, 444, 140),
                confidence=0.85,
            )
            is not None
        )

    def turn_on(self) -> None:
        if self.is_turned_on():
            print("Grinder is already on!")
            return

        if not self.can_turn_on():
            raise NoGasolineError

        while self.can_turn_on():
            self.click_at(964, 615, delay=0.3)
            self.sleep(1)

        print("Grinder has been turned on!")

    def turn_off(self) -> None:
        if self.can_turn_on():
            print("Grinder is already off!")
            return

        while self.is_turned_on():
            self.click_at(964, 615, delay=0.3)
            self.sleep(1)

        print("Grinder has been turned off!")

    def grind_all(self) -> bool:
        if not self.can_grind():
            print("There is no items to grind!")
            return False

        self.click_at(969, 663, delay=0.3)
        return True
