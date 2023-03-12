from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from ark import Bed, Player

from ..webhooks import InfoWebhook, TribeLogWebhook


class Station(ABC):
    """A station base class for any station intended to be included by ling-ling
    to follow. It provides the default spawn and interval check behavior as well
    as giving an idea of what arguments should be taken and how the station should
    be completed.

    Parameters
    -----------
    name :class:`str`:
        The name of the station

    player :class:`Player`:
        The player instance to use to complete the station

    tribelog :class:`TribeLog`:
        The tribelogs to post to while spawning at the station

    interval :class:`Optional[int]`:
        The station interval in minutes, to check whether its ready

    last_completed :class:`Optional[datetime]`:
        The timestamp of the last completion, to check whether its ready
    """

    def __init__(
        self,
        name: str,
        player: Player,
        tribelog: TribeLogWebhook,
        webhook: InfoWebhook,
        interval: Optional[int] = None,
        last_completed: Optional[datetime] = None,
    ) -> None:
        self._name = name
        self._player = player
        self._tribelog = tribelog
        self.bed = Bed(name)
        self.interval = interval
        self.last_completed = last_completed

    def __str__(self) -> str:
        return f"{type(self).__name__} {self._name}"

    @property
    def name(self) -> str:
        return self._name

    def is_ready(self) -> bool:
        """Checks whether the station is ready by comparing the station
        datas' interval to the last emptied datetime.
        """
        if self.interval is None or self.last_completed is None:
            return True

        time_diff = datetime.now() - self.last_completed
        print(f"Time left for {self._name}: {(self.interval * 60) - time_diff.total_seconds()}")
        return time_diff.total_seconds() > (self.interval * 60)

    def spawn(self) -> None:
        """Spawns at the station given the station datas bed object.
        Checks tribelogs during whitescreen and awaits to be loaded
        in by checking for the stamina bar.
        """
        self._player.stand_up()
        self._player.prone()
        self._player.look_down_hard()
        
        self.bed.spawn()
        self._tribelog.check_tribelogs()
        self._player.spawn_in()

    @abstractmethod
    def complete(self) -> None:
        """Completes the station, returns the statistics as a discord Embed."""
        ...
