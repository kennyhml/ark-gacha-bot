import time
from dataclasses import dataclass

from discord import Embed  # type: ignore[import]

from ark.tribelog import TribeLog
from ark.beds import BedMap
from ark.entities import Player
from ark.items import MEJOBERRY, Item
from ark.structures.structure import Structure
from bot.stations.feed_stations import FeedStation
from bot.stations.station import StationStatistics, StationData

MEJOBERRY_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/0/00/Mejoberry.png/revision/latest/scale-to-width-down/228?cb=20160219215159"


@dataclass
class BerryStatistics:

    time_taken: int
    refill_lap: bool
    profit: dict[Item, int]

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

    def __init__(
        self, station_data: StationData, player: Player, tribelog: TribeLog
    ) -> None:
        super().__init__(station_data, player, tribelog)
        self.bed_map = BedMap()
        self.crop_plot = Structure("Tek Crop Plot", "tek_crop_plot")

    def is_ready(self) -> bool:
        return False


    def do_crop_plots(self) -> None:
        """Does the crop plot stack, finishes facing the last stack"""
        direction = "left" if self.gacha_is_right() else "right"

        for _ in range(2):
            self.player.turn_90_degrees(direction)
            self.player.do_precise_crop_plot_stack(MEJOBERRY, refill_pellets=True)

    def create_embed(self, statistics: StationStatistics) -> Embed:
        """Creates a `discord.Embed` from the stations statistics.

        The embed contains info about what station was finished and how
        long it took.

        Parameters:
        ----------
        statistics :class:`StationStatistics`:
            The statistics object of the station to take the data from.

        Returns:
        ---------
        A formatted `discord.Embed` displaying the station statistics
        """
        embed = Embed(
            type="rich",
            title=f"Finished berry station {self.station_data.beds[self.current_bed].name}!",
            color=0xFC97E8,
        )

        embed.add_field(name="Time taken:ㅤ", value=f"{statistics.time_taken} seconds")

        embed.set_thumbnail(url=MEJOBERRY_AVATAR)
        embed.set_footer(text="Ling Ling on top!")
        return embed

    def complete(self) -> tuple[Embed, StationStatistics]:
        """Runs the feed station."""
        self.spawn()
        start = time.time()

        try:
            self.get_pellets(25)
            self.do_crop_plots()
            self.fill_troughs(MEJOBERRY)
            stats = BerryStatistics(round(time.time() - start), False, {})
            return self.create_embed(stats), stats

        finally:
            self.increment_bed_counter()


