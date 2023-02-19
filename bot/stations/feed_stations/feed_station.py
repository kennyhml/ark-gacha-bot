
from datetime import datetime
from typing import Callable, Optional, Sequence

import numpy as np
from ark import TribeLog
from ark.entities import Dinosaur, Player
from ark.items import PELLET, Item

from bot.stations._station import Station


class FeedStation(Station):
    """A class representing the generic feedstation.

    Parameters:
    -----------
    station_data :class:`StationData`:
        A dataclass containing data about the station

    player :class:`Player`:
        The player controller handle responsible for movement

    tribelog :class:`Tribelog`:
        The tribelog object to check tribelogs when spawning
    """

    def __init__(
        self, station_data, player: Player, tribelog: TribeLog
    ) -> None:

        self.station_data = station_data
        self.player = player
        self.tribelog = tribelog

        self.trough = Structure("Tek Trough", "tek_trough")
        self.gacha = Dinosaur("Gacha", "gacha")
        self.current_bed = 0
        self.check_npy_path()

    def check_npy_path(self) -> None:
        if not self.station_data.npy_path:
            raise InvalidNpyPathError(f"A feed Station needs a '.npy' file path!")

    def gacha_is_right(self) -> bool:
        """Checks whether the gacha is on the righthand side when the player
        spawns given the beds numeric suffix."""
        return int(self.station_data.beds[self.current_bed].name[-2:]) % 2 == 0

    def get_pellets(self, transfer_rows_back: int = 6) -> None:
        """Takes the pellets from the gacha.

        Parameters:
        ----------
        transfer_rows_back :class:`int`:
            The amount of pellet rows we want to transfer back into the gacha,
            to avoid capping due to pellet overflow.
        """

        direction = "right" if self.gacha_is_right() else "left"
        self.player.turn_90_degrees(direction, delay=1)

        # open the gacha, default_key=False because the inventory will not
        # be opened pressing 'F' due to the catwalk, however pressing 'E'
        # works, just need to make sure the gacha does not have a saddle equipped
        self.gacha.inventory.open(default_key=False)
        self.gacha.inventory.take_all_items(PELLET)
        self.player.inventory.await_items_added()

        # transfer some pellets back in
        self.player.inventory.take_pellets(transfer_back=transfer_rows_back)
        self.gacha.inventory.close()
        self.player.sleep(1)

    def case_01_05_09(self) -> Sequence[tuple[Callable, int] | Callable]:
        return [
            (self.player.turn_x_by, 80),
            (self.player.turn_y_by, -40),
            self.player.crouch,
            (self.player.turn_x_by, 40),
            self.player.crouch,
            (self.player.turn_y_by, 40),
            (self.player.turn_x_by, 50),
            self.player.crouch,
            (self.player.turn_y_by, -40),
        ]

    def case_00_02_04(self) -> Sequence[tuple[Callable, int] | Callable]:
        return [
            (self.player.turn_x_by, -80),
            (self.player.turn_y_by, -40),
            self.player.crouch,
            (self.player.turn_x_by, -40),
            self.player.crouch,
            (self.player.turn_y_by, 40),
            (self.player.turn_x_by, -50),
            self.player.crouch,
            (self.player.turn_y_by, -40),
        ]

    def case_other(self) -> Sequence[tuple[Callable, int] | Callable]:
        return [
            (self.player.turn_x_by, 90),
            (self.player.turn_y_by, -40),
            self.player.crouch,
            (self.player.turn_x_by, 40),
            self.player.crouch,
            (self.player.turn_y_by, 40),
            (self.player.turn_x_by, 50),
            self.player.crouch,
            (self.player.turn_y_by, -40),
        ]

    def get_trough_turns(self) -> Sequence[tuple[Callable, int] | Callable]:
        """Gets the optimized trough turns given the stations bed for the
        respective bed.

        Returns:
        ---------
        A list of actions (turns and crouches) either as a tuple (func, arg) or
        just the crouch function.

        e.g:
        >>> [(turn_x, 80), (turn_y, -40), crouch]
        """
        # get the beds suffix
        bed_suffix = self.station_data.beds[self.current_bed].name[-2:]

        # check for the correct remainder
        if int(bed_suffix) % 4 == 1:
            return self.case_01_05_09()

        elif int(bed_suffix) % 2 == 0:
            return self.case_00_02_04()

        return self.case_other()

    def fill_trough(self, item: Item, popcorn: Optional[Item] = None) -> None:
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
        self.trough.inventory.open()
        if popcorn:
            self.trough.inventory.popcorn(popcorn)

        self.player.inventory.transfer_all(self.trough.inventory)
        self.player.sleep(0.5)

        # check for berries left in our inventory
        if not self.player.inventory.has_item(item):
            self.trough.inventory.close()
            raise NoItemsLeftError(f"No {item} left to transfer!")

        self.trough.inventory.close()
        self.player.sleep(0.3)

    def fill_troughs(self, item: Item, popcorn: Optional[Item] = None) -> None:
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
        self.player.sleep(0.2)
        self.player.turn_y_by(-150)
        self.player.sleep(1)

        for action in self.get_trough_turns():
            if isinstance(action, tuple):
                func, arg = action
                func(arg)
            else:
                action()
            self.player.sleep(0.3)

            try:
                self.fill_trough(item, popcorn)
            except NoItemsLeftError:
                return

    def increment_bed_counter(self) -> None:
        if self.current_bed < len(self.station_data.beds) - 1:
            self.current_bed += 1
            return

        # all station beds completed
        self.current_bed = 0
        time = datetime.now()
        self.station_data.last_completed = time
        if self.station_data.npy_path:
            np_format = np.array(
                [time.year, time.month, time.day, time.hour, time.minute]
            )
            np.save(self.station_data.npy_path, np_format)
