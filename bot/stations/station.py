""""
Abstract base class example that all ling ling stations *need* to follow.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol

import numpy as np
from discord import Embed

from ark.beds import Bed, BedMap
from ark.entities.player import Player
from ark.exceptions import NoBedPassedError
from ark.items import Item
from ark.tribelog import TribeLog


@dataclass
class StationData:
    """Contains the relevant data of a station.

    interval :class:`int`:
        The run frequency of the station in seconds

    last_completed :class:`datetime`:
        The datetime object of the last completion

    bed :class:`Bed`:
        The respective bed to the station

    npy_path [Optional] :class:`str`:
        The path to a .npy file storing the `datetime` object of the
        last completion. Replaces the `last_completed` in `__post_init__`
    """

    interval: int
    beds: list[Bed]
    last_completed: datetime = datetime.now()
    npy_path: Optional[str] = None

    def __post_init__(self) -> None:
        if self.npy_path is not None:
            self.last_completed = datetime(*np.load(self.npy_path))


@dataclass
class StationStatistics(Protocol):
    """The protocol to follow when creating a station statistics dataclass."""

    time_taken: int
    refill_lap: bool
    profit: dict[Item, int]


class Station(ABC):
    """A station base class for any ling-ling station class to follow.

    Parameters:
    -----------
    station_data :class:`StationData`:
        The data of the station, contains the bed to spawn at, the interval
        and the last completion time.

    player :class:`Player`:
        The player object to control our player.

    tribelog :class:`TribeLog`:
        The tribelog object to update the tribelogs.
    """

    station_data: StationData
    player: Player
    tribelog: TribeLog
    current_bed: int = 0

    def is_ready(self) -> bool:
        """Checks whether the station is ready by comparing the station
        datas' interval to the last emptied datetime.
        """
        time_diff = datetime.now() - self.station_data.last_completed
        return time_diff.total_seconds() > self.station_data.interval

    def spawn(self) -> None:
        """Spawns at the station given the station datas bed object.
        Checks tribelogs during whitescreen and awaits to be loaded
        in by checking for the stamina bar.
        """
        if not self.station_data.beds:
            raise NoBedPassedError(
                "You did not define a 'Bed' for the station in 'StationData'."
            )

        bed_map = BedMap()
        bed_map.travel_to(self.station_data.beds[self.current_bed])
        self.tribelog.check_tribelogs()
        self.player.await_spawned()

    @abstractmethod
    def complete(self) -> tuple[Embed, StationStatistics]:
        """Completes the station, returns the statistics as a discord Embed."""
        ...

    @abstractmethod
    def create_embed(self, statistics: StationStatistics) -> Embed:
        """Returns a formatted embed of the station run."""
        ...
