import pydirectinput as input
import pyautogui as pg

from ark.inventories import CropPlot, Gacha, PlayerInventory, Inventory
from ark.buffs import Buff, thirsty, hungry, pod_xp, broken_bones
from ark.items import y_trap, Item
from bot.ark_bot import ArkBot

from ark.exceptions import InventoryNotAccessibleError


class Player(ArkBot):

    DEBUFF_REGION = (1270, 950, 610, 130)
    HP_BAR = (1882, 1022, 15, 50)

    def __init__(self) -> None:
        super().__init__()
        self.inventory = PlayerInventory()

    def drop_all(self) -> None:
        self.inventory.open()
        self.inventory.drop_all()
        self.inventory.close()

    def drop_all_items(self, item) -> None:
        self.inventory.open()
        self.inventory.drop_all_items(item)
        self.inventory.close()

    def is_spawned(self) -> bool:
        """Checks if the player is spawned"""
        return (
            self.locate_template(
                "templates/stamina.png", region=(1850, 955, 70, 65), confidence=0.7
            )
            is not None
        )

    def needs_recovery(self) -> bool:
        for buff in [thirsty, hungry, broken_bones]:
            if self.has_effect(buff):
                print(f"Bad effect located: {buff.name}! Going to heal...")
                return True
        return False

    def has_effect(self, buff: Buff) -> bool:
        """Checks if the player has the given buff"""
        return (
            self.locate_template(buff.image, region=self.DEBUFF_REGION, confidence=0.8)
            is not None
        )

    def await_spawned(self) -> None:
        while not self.is_spawned():
            self.sleep(0.5)
        print("Now spawned!")

    def turn_90_degrees(self, direction: str = "right") -> None:
        """Turns by 90 degrees in given direction"""
        val = 130 if direction == "right" else -130
        self.turn_x_by(val)

    def look_down_hard(self) -> None:
        """Looks down all the way to the ground"""
        for _ in range(7):
            self.turn_y_by(50)
            self.sleep(0.05)
        self.sleep(0.3)

    def look_up_hard(self) -> None:
        """Looks up all the way to the ceiling"""
        for _ in range(7):
            self.turn_y_by(-50)
            self.sleep(0.05)
        self.sleep(0.3)

    def turn_y_by(self, amount) -> None:
        """Turns the players' y-axis by the given amount"""
        self.check_status()
        input.moveRel(0, amount, 0, None, False, False, True)

    def turn_x_by(self, amount) -> None:
        """Turns the players' x-axis by the given amount"""
        self.check_status()
        input.moveRel(amount, 0, 0, None, False, False, True)

    def do_crop_plots(self) -> None:
        """Empties all stacks of crop plots
        Starts facing the gacha, ends facing the gacha
        """
        self.press(self.keybinds.crouch)

        for _ in range(3):
            self.turn_90_degrees()
            self.do_crop_plot_stack()
        self.turn_90_degrees()
        self.sleep(0.2)

    def do_crop_plot_stack(self) -> None:
        """Empties the current stack of crop plots.

        Takes all traps from the crop plots using the searchbar, then transfers
        all to put pellets in. If no traps are in the crop plot, taking traps
        will be skipped.

        Transfer all from the inventory will always be pressed because pellets
        can end up at the very bottom of the inventory depending on the amount
        of traps.
        """
        crop_plot = CropPlot()

        # look down to sync
        self.look_down_hard()
        self.sleep(0.1)

        # take the bottom most crop plot
        self.turn_y_by(-130)
        self.sleep(0.5)
        crop_plot.take_traps_put_pellets(self.inventory)

        # look up slightly emptying the next 5
        for _ in range(5):
            self.turn_y_by(-17)
            crop_plot.take_traps_put_pellets(self.inventory)

        # stand up and take the current one
        self.press(self.keybinds.crouch)
        self.turn_y_by(50)
        crop_plot.take_traps_put_pellets(self.inventory)

        # take next two
        for _ in range(2):
            self.turn_y_by(-17)
            crop_plot.take_traps_put_pellets(self.inventory)

        # back to crouching
        self.press(self.keybinds.crouch)

    def look_for_gacha(self, gacha: Gacha) -> None:
        """Locates the gacha using vertical and horizontal
        movements after each it attempts to locate the `Ride`
        template.

        Parameters:
        -----------
        gacha :class:`Gacha`:
            The instance of the gacha to locate

        Returns:
        -----------
        `True` if the gacha could be found else `None`
        """
        # check if we need to move at all
        if gacha.can_access():
            return True

        # look down then straight forward to sync
        self.look_down_hard()
        self.sleep(0.1)
        self.turn_y_by(-180)
        if gacha.can_access():
            return True

        # look further up 6 times, every 3 times check left & right
        for i in range(6):
            self.turn_y_by(-10)
            if gacha.can_access():
                return True

            # look at the sides every 3 steps
            if (i + 1) % 3 == 0:

                # look at left
                for _ in range(4):
                    self.turn_x_by(-20)
                    if gacha.can_access():
                        return True
                # look at right
                for _ in range(8):
                    self.turn_x_by(20)
                    if gacha.can_access():
                        return True
                # back to middle
                for _ in range(4):
                    self.turn_x_by(-20)
                    if gacha.can_access():
                        return True

    def load_gacha(self, gacha: Gacha) -> None:
        """Fills the gacha after emptying crop plots.

        Will first attempt to look at the gacha using vertical
        and horizontal movements, then takes all the pellets,
        puts traps in and then fills with remaining pellets.

        Parameters:
        -----------
        gacha :class:`Gacha`:
            The gacha instance of the gacha to transfer items to

        Raises:
        -----------
        `InventoryNotAccessible` if the gacha cant be accessed
        """

        # open the gacha and take all pellets
        gacha.open()
        amount_of_traps = self.inventory.count_item(y_trap)
        gacha.take_all_items("ll")

        # put traps back in then remaining pellets
        self.inventory.transfer_all(gacha, "trap")
        self.sleep(0.5)
        self.inventory.transfer_all(gacha)
        self.sleep(0.5)
        self.inventory.drop_all()
        self.inventory.close()
        return amount_of_traps

    def walk(self, key, duration):
        input.keyDown(key)
        self.sleep(duration=duration)
        input.keyUp(key)

    def crouch(self) -> None:
        self.press(self.keybinds.crouch)

    def prone(self) -> None:
        self.press(self.keybinds.prone)

    def disable_hud(self) -> None:
        self.press("backspace")

    def pick_up_bag(self):
        self.look_down_hard()
        self.press(self.keybinds.target_inventory)
        self.sleep(0.5)
        bag = Inventory("Bag", "bag")
        bag.open()
        self.move_to(1287, 289)
        self.press("o")
        self.sleep(1)

    def do_drop_script(self, item: Item, target_inventory: Inventory):

        self.crouch()
        self.sleep(0.5)
        target_inventory.open()

        self.inventory.take_one_item(item, slot=2, inventory=target_inventory)
        self.inventory.await_items_added()
        self.sleep(0.3)
        self.inventory.drop_all_items(item.name)

        self.inventory.search_for(item.name)

        while True:
            target_inventory.search_for(item.name)
            self.sleep(0.5)
            if not target_inventory.has_item(item):
                break

            target_inventory.take_all()
            self.sleep(0.3)
            for _ in range(3):
                for slot in [(168, 280), (258, 280), (348, 277)]:
                    pg.moveTo(slot)
                    pg.press(self.keybinds.drop)

        self.inventory.close()
        self.pick_up_bag()
        self.crouch()
        self.sleep(0.5)

    def item_added(self) -> bool:
        return (
            self.locate_template(
                "templates/added.png", region=(0, 450, 314, 240), confidence=0.75
            )
            is not None
        )

    def await_item_added(self) -> None:
        c = 0
        while not self.item_added():
            self.sleep(0.1)
            c += 1
            if c > 10:
                return False
        return True
