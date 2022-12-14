import pydirectinput as input
import pyautogui as pg

from ark.inventories import CropPlot, Gacha, PlayerInventory, Inventory
from ark.buffs import Buff, thirsty, hungry, pod_xp, broken_bones
from ark.items import y_trap, Item
from bot.ark_bot import ArkBot

from ark.exceptions import InventoryNotAccessibleError, PlayerDidntTravelError


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
        counter = 0
        while not self.is_spawned():
            self.sleep(0.5)
            counter += 1

            if counter > 100:
                raise PlayerDidntTravelError("Failed to spawn in!")
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

    def do_crop_plots(self, refill_pellets: bool = False) -> None:
        """Empties all stacks of crop plots
        Starts facing the gacha, ends facing the gacha
        """
        self.sleep(0.5)
        self.press(self.keybinds.crouch)

        for _ in range(3):
            self.turn_90_degrees()
            self.do_crop_plot_stack(refill_pellets)
        self.turn_90_degrees()
        self.sleep(0.2)

    def adjust_for_crop_plot(self, crop_plot: CropPlot, expected_index: int) -> None:
        """Checks if the expected crop plot was opened, adjusts if it was not.
        
        Parameters:
        -----------
        crop_plot :class:`CropPlot`:
            The crop plot we are trying to open

        expected_index :class:`int`:
            The expected index of the crop plot (in the stack)

        TODO: Raise an error when the correct crop plot could not be opened whatsoever
        """
        index = crop_plot.get_stack_index()
        while index != expected_index:
            # no index at all was found, try to reopen the crop plot
            if not index:
                crop_plot.close()
                crop_plot.open()
                index = crop_plot.get_stack_index()
                continue
            crop_plot.close()

            # check if we need to correct higher or lower
            if index > expected_index:
                self.turn_y_by(5)
            else:
                self.turn_y_by(-5)
            
            # recheck the index
            crop_plot.open()
            index = crop_plot.get_stack_index()

    def do_crop_plot_stack(self, refill_pellets: bool = False) -> None:
        """Empties the current stack of crop plots.

        Takes all traps from the crop plots using the searchbar, then transfers
        all to put pellets in. If no traps are in the crop plot, taking traps
        will be skipped.

        Parameters:
        -----------
        refill_pellets :class:`bool`:
            Whether pellets need to be refilled or not
        """
        crop_plot = CropPlot()

        # look down to sync
        self.look_down_hard()
        self.sleep(0.1)

        for val in [-130, *[-17] * 5]:
            self.turn_y_by(val)
            self.sleep(0.3)
            crop_plot.take_traps_put_pellets(self.inventory, refill_pellets)

        # stand up and take the current one
        self.press(self.keybinds.crouch)
        for val in [50, -17, -17]:
            self.turn_y_by(val)
            crop_plot.take_traps_put_pellets(self.inventory, refill_pellets)

        # back to crouching
        self.press(self.keybinds.crouch)

    def do_precise_crop_plot_stack(
        self,
        item: Item = None,
        refill_pellets: bool = False,
        take_all: bool = False,
        max_index: int = 8,
    ) -> None:
        """Empties the current stack of crop plot, but aims for a 100% access rate.

        This is achieved by adding a folder to each crop plot from bottom to top,
        AAA to HHH, so the bot can see the folder and know which crop plot
        it accessed thus being able to adjust itself higher or lower.

        Parameters:
        -----------

        item :class:`Item`:
            The item to take out of the crop plot, as `Item` object.

        take_all :class:`bool`:
            Whether the bot should take all from the crop plot

        max_index :class:`int`:
            The highest crop plot to be accessed, default 8
        """
        crop_plot = CropPlot()
        self.crouch()

        turns = [-130, -20, -20, -17, -15, 35, -17, -20]
        self.look_down_hard()
        self.sleep(0.1)

        # go through each turn attempting to access the respective
        for expected_index, turn in enumerate(turns, start=1):
            if expected_index - 1 == max_index:
                return

            if expected_index == 6:
                self.crouch()

            self.turn_y_by(turn)
            self.sleep(0.3)
            crop_plot.open()

            # check for the correct crop plot
            self.adjust_for_crop_plot()

            if take_all:
                crop_plot.take_all()
            elif item:
                crop_plot.take_all_items(item)

            if refill_pellets:
                self.inventory.transfer_all(crop_plot)
            crop_plot.close()

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

    def do_drop_script(self, item: Item, target_inventory: Inventory, slot=2):

        self.crouch()
        self.sleep(0.5)
        target_inventory.open()

        self.inventory.take_one_item(item, slot=slot, inventory=target_inventory)
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
