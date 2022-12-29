import time
from dataclasses import dataclass

from discord import Embed  # type: ignore[import]

from ark.beds import TekPod
from ark.entities.player import Player
from ark.exceptions import TekPodNotAccessibleError
from ark.items import Item
from ark.tribelog import TribeLog
from bot.stations.station import (
    Station,
    StationData,
    StationStatistics,
    format_time_taken,
)


@dataclass
class HealingStatistics:
    """The protocol to follow when creating a station statistics dataclass."""

    time_taken: int
    refill_lap: bool
    profit: dict[Item, int]


class HealingStation(Station):
    def __init__(
        self, station_data: StationData, player: Player, tribelog: TribeLog
    ) -> None:
        self.station_data = station_data
        self.player = player
        self.tribelog = tribelog
        self.current_bed = 0
        self._least_healed = time.time()
        self.tek_pod = TekPod(station_data.beds[0].name, station_data.beds[0].coords)

    def is_ready(self) -> bool:
        return self.player.needs_recovery()

    def create_embed(self, statistics: StationStatistics) -> Embed:
        """Sends a msg to discord that we healed"""
        embed = Embed(
            type="rich",
            title=f"Recovered player at '{self.tek_pod.name}'!",
            color=0x4F4F4F,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{statistics.time_taken} seconds")
        embed.add_field(
            name="Last healed:", value=format_time_taken(self._least_healed)
        )
        embed.set_thumbnail(url=self.tek_pod.discord_image)
        embed.set_footer(text="Ling Ling on top!")

        return embed

    def complete(self) -> tuple[Embed, HealingStatistics]:
        """Goes to heal by travelling to the tek pod, trying to enter it up to
        3 times. If it can not enter the tek pod, a `TekPodNotAccessible` Error
        is raised.
        """
        self.spawn()
        start = time.time()

        # try to enter the pod 3 times
        for _ in range(3):
            if not self.tek_pod.enter():
                self.player.sleep(1)
                continue

            self.tek_pod.heal(60)
            self.tek_pod.leave()

            stats = HealingStatistics(round(time.time() - start), False, {})

            return self.create_embed(stats), stats

        # we cant heal, raise an error so we can try to unstuck
        raise TekPodNotAccessibleError("Failed to access the tek pod!")
