from pytesseract import pytesseract as tes

from ark.exceptions import NoItemsDepositedError
from ark.inventories.dedi_inventory import DedicatedStorageInventory
from ark.items import Item
from ark.structures.structure import Structure


class TekDedicatedStorage(Structure):
    """Represents the grinder inventory in ark.

    Is able to be turned on and off and grind all.
    """
    def __init__(self) -> None:
        super().__init__("Tek Dedicated Storage", "dedi")
        self.inventory = DedicatedStorageInventory()
        
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

    def item_deposited(self, item: Item) -> tuple:
        """Checks if the given item has been deposited"""
        if not item.added_icon:
            raise Exception(f"You did not define an 'added_icon' for {item}!")

        return self.locate_template(
            item.added_icon, region=(0, 430, 160, 350), confidence=0.7
        )

    def attempt_deposit(
        self, items: list[Item], determine_amount: bool = True
    ) -> tuple[Item, int] | None:
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

        if not determine_amount:
            return None

        # check for each item
        for item in items:
            if not self.item_deposited(item):
                continue

            # 5 attempts to get a better chance for a good result
            for _ in range(5):
                # get the amount of deposited items of the items we are depositing
                amount = self.get_amount_deposited(item)
            break
        else:
            # never got to an item that was deposited, no amount can be determined
            amount = 0

        # wait for the green text to go away so we can try fresh on the next dedi
        while self.deposited_items():
            self.sleep(0.1)
        return item, amount

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

        if not item.added_text:
            raise Exception(f"You did not define an 'added_text' for {item}!")

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
