from ark.beds import Bed, BedMap
from ark.entities import Dinosaur
from ark.exceptions import DinoNotMountedError, NoItemsLeftError, BedNotAccessibleError
from ark.items import Item, MEJOBERRY, RAW_MEAT, PELLET
from ark.entities import Player
from bot.ark_bot import ArkBot

from copy import deepcopy

class FeedStation(ArkBot):
    """A class representing the generic feedstation.

    Parameters:
    -----------
    bed :class:`Bed`:
        The stations bed object to travel to
    """

    def __init__(self, bed: Bed) -> None:
        super().__init__()
        self.gacha = Gacha()
        self.player = Player()
        self.bed = bed
        self.bedmap = BedMap()
        self.trough = Inventory("Tek Trough", "tek_trough")

    def gacha_is_right(self) -> bool:
        return int(self.bed.name[-2:]) % 2 == 0

    def spawn(self) -> None:
        """Spawns and turns towards the gacha"""
        self.bedmap.travel_to(self.bed)
        self.player.await_spawned()
        self.sleep(1)

    def take_pellets(self, transfer_rows_back: int = 6) -> None:
        """Takes the pellets from the gacha.

        Parameters:
        ----------
        transfer_rows_back :class:`int`:
            The amount of pellet rows we want to transfer back into the gacha,
            to avoid capping due to pellet overflow.
        """

        if self.gacha_is_right():
            self.player.turn_90_degrees("right")
        else:
            self.player.turn_90_degrees("left")

        self.sleep(1)

        # open gacha, take pellets and wait for them to be added
        self.sleep(0.5)
        self.gacha.open(default_key=False)
        self.gacha.take_all_items("ll")
        self.player.inventory.await_items_added()
        self.sleep(0.5)

        # transfer some pellets back in
        self.player.inventory.transfer_some_pellets(
            self.player.inventory, transfer_back=transfer_rows_back
        )
        self.gacha.close()
        self.sleep(1)

    def get_trough_turns(self) -> list[tuple]:
        """Gets the optimized trough turns given the stations bed for the
        respective bed.

        Returns:
        ---------
        A list of actions (turns and crouches) either as a tuple (func, arg) or
        just the crouch function.

        e.g:
        >>> [(turn_x, 80), (turn_y, -40), crouch]
        """
        # alias to make it more readable
        turn_x = self.player.turn_x_by
        turn_y = self.player.turn_y_by
        crouch = self.player.crouch

        # check for beds such as 01, 05, 09...
        if self.bed.name[-2:] in [f"{i:02d}" for i in range(1, 16, 4)]:
            return [
                (turn_x, 80),
                (turn_y, -40),
                crouch,
                (turn_x, 40),
                crouch,
                (turn_y, 40),
                (turn_x, 50),
                crouch,
                (turn_y, -40),
            ]

        # two beds sharing the same turns, such as 00, 02, 04, 06...
        if self.bed.name[-2:] in [f"{i:02d}" for i in range(0, 16, 2)]:
            return [
                (turn_x, -80),
                (turn_y, -40),
                crouch,
                (turn_x, -40),
                crouch,
                (turn_y, 40),
                (turn_x, -50),
                crouch,
                (turn_y, -40),
            ]

        # only one variant left at this point
        return [
            (turn_x, 90),
            (turn_y, -40),
            crouch,
            (turn_x, 40),
            crouch,
            (turn_y, 40),
            (turn_x, 50),
            crouch,
            (turn_y, -40),
        ]

    def fill_trough(self, item: Item) -> None:
        """Opens the trough the player is looking at and deposits the given
        item. If no items are left after depositing, an Exception is raised.

        Parameters:
        -----------
        item :class:`Item`:
            The item to deposit, an `Item` object is required!

        Raises:
        ---------
        `NoItemsLeftError` when there is no items left in the inventory after
        depositing.
        """
        # open trough and transfer berries, add delays to make sure we only check
        # for berries in the inventory once they actually transferred.
        self.sleep(0.3)
        self.trough.open()
        self.player.inventory.transfer_all(self.trough)
        self.sleep(0.5)

        # check for berries left in our inventory
        if not self.player.inventory.has_item(item):
            self.trough.close()
            raise NoItemsLeftError(f"No {item} left to transfer!")
        self.trough.close()
        self.sleep(0.3)

    def fill_troughs(self, item: Item) -> None:
        """Fills all the troughs with the passed item. Stops when
        a `NoItemsLeftError` is raised.

        Parameters:
        -----------
        item :class:`Item`:
            The item to put into the troughs
        """
        # prepare to fill troughs
        self.player.crouch()
        self.player.look_down_hard()
        self.sleep(0.2)
        self.player.turn_y_by(-150)
        self.sleep(1)

        for action in self.get_trough_turns():
            if isinstance(action, tuple):
                func, arg = action
                print(f"{func.__name__}({arg})")
                func(arg)
            else:
                action()

            try:
                self.fill_trough(item)
            except NoItemsLeftError:
                return


class BerryFeedStation(FeedStation):
    """Handles the auto berry station. The purpose of the station is to
    take mejoberries from crop plots to raise dinos in its area, or to
    pile up on berries for use elsewhere. on 500% greenhouse effect it
    takes 5 hours to fully regenerate.

    Parameters:
    -----------
    bed :class:`Bed`:
        The bed object of the station to travel to
    """

    def do_crop_plots(self) -> None:
        """Does the crop plot stack, finishes facing the last stack"""
        direction = "left" if self.gacha_is_right() else "right"

        for _ in range(2):
            self.player.turn_90_degrees(direction)
            self.player.do_precise_crop_plot_stack(mejoberry, refill_pellets=True)

    def run(self) -> None:
        """Runs the feed station."""
        self.spawn()
        self.take_pellets(25)
        self.do_crop_plots()
        self.fill_troughs(mejoberry)


class MeatFeedStation(FeedStation):
    """Handles the auto meat station. The purpose of the station is to
    harvest meat plants using direbears to raise dinos in its area or let
    meat pile up for use elsewhere. The plants take 30 minutes to regenerate
    but should not be harvested every 30 minutes due to meat overflow.


    Parameters:
    -----------
    bed :class:`Bed`:
        The bed object of the station to travel to

    """

    def __init__(self, bed: Bed) -> None:
        super().__init__(bed)
        self.dire_bear = Dinosaur("Dire Bear", "dire_bear")

    def spawn(self) -> None:
        """Override spawn method because we do not need to look at the
        gacha first."""
        self.bedmap.travel_to(self.bed)
        self.player.await_spawned()
        self.sleep(1)
 
    def travel_to_trough_bed(self) -> None:
        new_bed = deepcopy(self.bed)
        new_bed.name = new_bed.name[:-2] + "b" + new_bed.name[-2:]
        self.bedmap.travel_to(new_bed)
        self.player.await_spawned()
        self.sleep(1)

    def approach_dire_bear(self) -> None:
        counter = 0
        while not self.dire_bear.can_ride():
            self.player.walk("w", 0.1)
            counter += 1
            if counter > 8:
                return

    def get_meat(self) -> None:
        """Approaches the dire bear from the spawn point until it can ride it.
        Proceeds to hit the meatplants 20 times each second and then walks back to the bed"""
        self.approach_dire_bear()
        self.dire_bear.mount()
        self.player.turn_y_by(160)

        for _ in range(20):
            self.dire_bear.attack("left")
            self.sleep(0.7)
        self.sleep(5)

        self.dire_bear.dismount()
        print("Finished getting meat!")

    def walk_to_spawn(self) -> None:
        self.player.look_down_hard()
        key = "a" if self.gacha_is_right() else "d"

        while not self.bedmap.can_be_accessed():
            self.player.walk(key, 0.2)

    def crop_plots_need_pellets(self) -> bool:
        crop_plot = CropPlot()
        crop_plot.open()
        pellets_amount = crop_plot.count_item(pellet)
        crop_plot.close()

        return pellets_amount <= 10

    def refill_crop_plots(self) -> None:

        if self.gacha_is_right():
            self.player.turn_90_degrees("left")
        else:
            self.player.turn_90_degrees("right")

        self.player.do_precise_crop_plot_stack(refill_pellets=True, max_index=6)
        self.player.drop_all()

    def take_meat_from_bear(self) -> None:
        if self.gacha_is_right():
            self.player.walk("a", 0.5)
        else:
            self.player.walk("d", 0.5)

        self.player.look_up_hard()
        while not self.dire_bear.can_access():
            self.player.turn_y_by(10)
            self.sleep(0.5)

        if self.gacha_is_right():
            self.player.turn_90_degrees("right")
        else:
            self.player.turn_90_degrees("left")
        self.sleep(0.5)

        self.dire_bear.inventory.open()
        self.dire_bear.inventory.take_all_items(raw_meat)
        self.dire_bear.inventory.drop_all()
        self.dire_bear.inventory.close()
        self.sleep(1)
        self.player.look_down_hard()
        self.bedmap.lay_down()

        if self.gacha_is_right():
            for _ in range(2):
                self.sleep(0.5)
                self.player.turn_90_degrees("left")

        self.sleep(1)

    def run(self) -> None:
        self.spawn()
        self.get_meat()
        self.walk_to_spawn()
        self.travel_to_trough_bed()

        if self.crop_plots_need_pellets():
            self.take_pellets(10)
            self.refill_crop_plots()

        self.take_meat_from_bear()
        self.fill_troughs(raw_meat)
