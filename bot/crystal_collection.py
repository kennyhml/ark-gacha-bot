import pyautogui as pg
import pydirectinput as inp

from ark.inventories import DedicatedStorage, Vault
from ark.items import black_pearl, dust, gacha_crystal
from ark.player import Player
from bot.ark_bot import ArkBot
import time

class CrystalCollection(ArkBot):
    """Crystal collection handler
    ------------------------------
    Handles picking up the crystals in the gacha tower, from picking
    them up to opening to depositing them. Deposited amounts will
    be OCR'd using tesseract and the deposited amount will be returned.

    Inherits from `ArkBot` parent class.
    """

    def __init__(self, player: Player) -> None:
        super().__init__()
        self.started = time.time()
        self.player = player
        self.hotbar = [
            self.keybinds.hotbar_2,
            self.keybinds.hotbar_3,
            self.keybinds.hotbar_4,
            self.keybinds.hotbar_5,
            self.keybinds.hotbar_6,
            self.keybinds.hotbar_7,
            self.keybinds.hotbar_8,
            self.keybinds.hotbar_9,
            self.keybinds.hotbar_0,
        ]

    def typewrite(self, message) -> None:
        return super().typewrite(message)

    def walk_into_back(self) -> None:
        """Walks into the back of the pit, essentially does it twice
        to avoid not picking crystals due to lag.
        """
        self.player.walk("s", duration=3)

        self.press(self.keybinds.use)
        if self.player.await_item_added():
            return

        self.sleep(3)
        self.player.walk("s", duration=3)

    def walk_forward_spam_f(self) -> None:
        """Slowly walks foward spaming the pick-up key to pick all the
        crystals while being angled slighty downwards.
        """
        for _ in range(9):
            self.press(self.keybinds.target_inventory)
            self.sleep(0.1)
            self.player.walk("w", duration=0.2)

        self.player.walk("w", 2)

    def walk_to_dedi(self):
        """Walks forward to dedi with various lag protection

        Being at the dedi is determined when we can see the deposit text.
        We then attempt to open the dedi to ensure its not lagging, if it doesnt
        open, the action wheel logic is used to determine if its lag or a bad angle.
        """
        # look up further (so the deposit text 100% appears)
        dedi = DedicatedStorage()
        self.player.turn_y_by(-70)

        # try to access the dedi, if its not possible rewalk
        while not dedi.can_be_opened():
            while not dedi.can_deposit():
                self.player.walk("w", 1)

            self.player.walk("w", 1)
        dedi.close()

    def pick_crystals(self):
        """Picks up the crystals in the collection point

        Walks all the way into the back, slowly picks the crystals
        and walks back to the dedi with lag protection.
        """
        # walk back, crouch and look down
        self.walk_into_back()
        self.press(self.keybinds.crouch)
        self.player.turn_y_by(80)

        self.walk_forward_spam_f()
        self.walk_to_dedi()

    def put_crystals_in_hotbar(self):
        """Puts crystals in hotbar using `shift + slot`.

        This will happen regardless of crystals already being in the hotbar on every
        first run.
        """
        inp.keyDown("shift")
        for _ in range(4):
            for slot in self.hotbar:
                self.press(slot)
                self.sleep(0.5)
        inp.keyUp("shift")

    def hit_keys(self):
        """Typewrites all the hotbar keys with crystals on them to open crystals fast."""
        self.check_status()
        pg.typewrite("".join(c for c in self.hotbar), interval=0.01)

    def open_crystals(self, first_time: bool) -> None:
        """Opens the crystals at the dedis, counting each iteration of the hotbar
        until there are no more crystals in our player inventory.

        Parameters:
        -----------
        first_time :class:`bool`:
            Whether the bot has opened crystals before, this will decide if it will
            put crystals into the hotbar or not.
        """
        # open inv and search for gacha crystals, click first crystal
        self.player.inventory.open()
        self.player.inventory.search_for("gacha")
        self.click_at(163, 281)

        # put crystals into hotbar always on the first run
        if first_time:
            self.put_crystals_in_hotbar()

        # open until no crystals left in inventory, count iterations
        r = 0
        while self.player.inventory.has_item(gacha_crystal):
            self.hit_keys()
            self.press("e")
            r += 1

        # go over the hotbar 5 more times to ensure no crystals left behind
        for _ in range(5):
            self.hit_keys()

        print(f"Opened rougly {r * 7} crystals!")
        self.player.inventory.close()
        self.sleep(3)
        return r * 7

    def deposit_dedis(self) -> tuple[dict, int]:
        """Deposits all the dust / black pearls into the dedis.\n
        Uses `DedicatedStorage.attempt_deposit` method to deposit into each of the dedis.

        Returns:
        -----------
        A dictionary containing the amounts of items deposited for dust and pearls
        """

        gains = {"Element Dust": 0, "Black Pearl": 0}
        dedi = DedicatedStorage()
        
        # prepare turns
        turns = {
            40: self.player.turn_x_by,
            -50: self.player.turn_y_by,
            -80: self.player.turn_x_by,
            50: self.player.turn_y_by,
        }

        # go through each turn depositing into dedi
        for amount in turns:
            turns[amount](amount)

            item, amount = dedi.attempt_deposit([dust, black_pearl])
            if amount:
                print(f'Deposited {amount} "{item}"!')
                gains[item] += amount
            else:
                print(
                    "Nothing was deposited, dedi is either full or we have already deposited all items!"
                )

        # return to original position
        self.player.turn_x_by(40)
        return gains, round(time.time() - self.started)

    def deposit_items(self, drop_items: list) -> None:
        vault = Vault()
        vault_full = False

        # put the grinding items in the left vault
        self.sleep(0.3)
        self.player.turn_90_degrees("left")
        self.sleep(1)
        vault.open()
        
        if not vault.is_full():
            # drop the shitty quality ones
            for item in drop_items:
                self.player.inventory.drop_all_items(item)
                self.sleep(0.3)

            # transfer all the grinding items
            for item in ["riot", "ass", "fab", "miner", "pump"]:
                self.player.inventory.transfer_all(vault, item)
                self.sleep(0.2)
            vault_full = vault.is_full()
        else:
            vault_full = True

        # turn to the upper vault
        vault.close()
        self.player.turn_90_degrees("right")
        self.player.look_up_hard()
        vault.open()

        if vault.is_full():
            self.player.inventory.drop_all()
            vault.close()
            return vault_full

        # put structure stuff in it
        for item in ["gate", "platform"]:
            self.player.inventory.transfer_all(vault, item)
            self.sleep(0.2)
        self.player.inventory.drop_all()
        vault.close()

        return vault_full
