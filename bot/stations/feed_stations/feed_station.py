import json
from datetime import datetime
from typing import Optional

from ark import Bed, Gacha, Player, Structure, TekCropPlot, items

from bot.stations._station import Station

from ...webhooks import InfoWebhook, TribeLogWebhook
from .._station import Station


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
        self,
        name: str,
        player: Player,
        tribelog: TribeLogWebhook,
        webhook: InfoWebhook,
        interval: int,
    ) -> None:

        self._name = name
        self._player = player
        self._tribelog = tribelog
        self._webhook = webhook
        self.interval = interval

        self.bed = Bed(name)
        self.trough = Structure("Tek Trough", "assets/templates/tek_trough.png")
        self.gacha = Gacha(name)

        self._stacks = [
            [TekCropPlot(f"Crop Plot {stack+ 1}:{idx+1}") for idx in range(8)]
            for stack in range(2)
        ]

        self.case_01_05_09 = [
            (self._player.turn_x_by, 80),
            (self._player.turn_y_by, -40),
            self._player.crouch,
            (self._player.turn_x_by, 40),
            self._player.crouch,
            (self._player.turn_y_by, 40),
            (self._player.turn_x_by, 50),
            self._player.crouch,
            (self._player.turn_y_by, -40),
        ]

        self.case_00_02_04 = [
            (self._player.turn_x_by, -80),
            (self._player.turn_y_by, -40),
            self._player.crouch,
            (self._player.turn_x_by, -40),
            self._player.crouch,
            (self._player.turn_y_by, 40),
            (self._player.turn_x_by, -50),
            self._player.crouch,
            (self._player.turn_y_by, -40),
        ]

        self.case_other = [
            (self._player.turn_x_by, 90),
            (self._player.turn_y_by, -40),
            self._player.crouch,
            (self._player.turn_x_by, 40),
            self._player.crouch,
            (self._player.turn_y_by, 40),
            (self._player.turn_x_by, 50),
            self._player.crouch,
            (self._player.turn_y_by, -40),
        ]

    def _load_last_completion(self, key: str) -> None:
        with open("bot/_data/station_data.json") as f:
            data: dict = json.load(f)[key]

        self.last_completed = datetime.strptime(
            data["last_completed"][:-3], "%Y-%m-%d %H:%M:%S.%f"
        )

    def gacha_is_right(self) -> bool:
        """Checks whether the gacha is on the righthand side when the player
        spawns given the beds numeric suffix."""
        return int(self.bed.name[-2:]) % 2 == 0

    def check_get_pellets(self) -> bool:
        """Takes the pellets from the gacha.

        Parameters:
        ----------
        transfer_rows_back :class:`int`:
            The amount of pellet rows we want to transfer back into the gacha,
            to avoid capping due to pellet overflow.
        """
        crop_plot = self._stacks[0][5]
        crop_plot.open()
        if crop_plot.inventory.count(items.PELLET) > 10:
            return False
        crop_plot.close()
        self._player.sleep(0.5)

        self._player.turn_90_degrees(
            "right" if self.gacha_is_right() else "left", delay=1
        )

        # open the gacha, default_key=False because the inventory will not
        # be opened pressing 'F' due to the catwalk, however pressing 'E'
        # works, just need to make sure the gacha does not have a saddle equipped
        self.gacha.inventory.open(default_key=False)
        self.gacha.inventory.transfer_all(items.PELLET)
        self._player.inventory.await_items_added(items.PELLET)
        self._player.inventory.search(items.PELLET)

        for _ in range(6):
            self._player.inventory.transfer_top_row()
        self.gacha.inventory.close()
        self._player.sleep(1)
        return True

    def get_trough_turns(self) -> list:
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
        bed_suffix = self.bed.name[-2:]

        # check for the correct remainder
        if int(bed_suffix) % 4 == 1:
            return self.case_01_05_09

        elif int(bed_suffix) % 2 == 0:
            return self.case_00_02_04

        return self.case_other

    def fill_trough(
        self, item: items.Item | list[items.Item], popcorn: Optional[items.Item] = None
    ) -> None:
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
        self.trough.open()
        if popcorn:
            self.trough.inventory.drop(popcorn)

        self._player.inventory.transfer_all()
        self._player.sleep(0.5)

        # check for berries left in our inventory
        if isinstance(item, items.Item):
            item = [item]

        if not any(self._player.inventory.has(i) for i in item):
            self.trough.inventory.close()
            raise LookupError(f"No {item} left to transfer!")

        self.trough.inventory.close()
        self._player.sleep(0.3)

    def fill_troughs(
        self, item: items.Item | list[items.Item], popcorn: Optional[items.Item] = None
    ) -> None:
        """Fills all the troughs with the passed item. Stops when
        a `NoItemsLeftError` is raised.

        Parameters:
        -----------
        item :class:`Item`:
            The item to put into the troughs
        """
        # prepare to fill troughs
        self._player.look_down_hard()
        self._player.sleep(0.2)
        self._player.turn_y_by(-150)
        self._player.sleep(1)

        for action in self.get_trough_turns():
            if isinstance(action, tuple):
                func, arg = action
                func(arg)
            else:
                action()
            self._player.sleep(0.3)

            try:
                self.fill_trough(item, popcorn)
            except LookupError:
                return
