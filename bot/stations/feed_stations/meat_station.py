import time
from dataclasses import dataclass
from datetime import datetime

from discord import Embed  # type: ignore[import]

from ark.beds import BedMap
from ark.entities import Dinosaur, Player
from ark.exceptions import InventoryNotAccessibleError
from ark.items import PELLET, RAW_MEAT, SPOILED_MEAT, Item
from ark.structures.structure import Structure
from ark.tribelog import TribeLog
from bot.stations.feed_stations import FeedStation
from bot.stations.station import StationData, StationStatistics

RAW_MEAT_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/e/e9/Raw_Meat.png/revision/latest/scale-to-width-down/228?cb=20150704150605"
TRANSFER_PELLETS_BACK = 15


@dataclass
class MeatStatistics:

    time_taken: int
    refill_lap: bool
    profit: dict[Item, int]


class MeatFeedStation(FeedStation):
    """Handles the auto meat station. The purpose of the station is to
    harvest meat plants using direbears to raise dinos in its area or let
    meat pile up for use elsewhere. The plants take 30 minutes to regenerate
    but should not be harvested every 30 minutes due to meat overflow.


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
        self, station_data: StationData, player: Player, tribelog: TribeLog
    ) -> None:
        super().__init__(station_data, player, tribelog)
        self.dire_bear = Dinosaur("Dire Bear", "dire_bear")
        self.bed_map = BedMap()
        self.crop_plot = Structure("Tek Crop Plot", "tek_crop_plot")

    def is_ready(self) -> bool:
        """Checks whether the station is ready by comparing the station
        datas' interval to the last emptied datetime.
        """
        # currently disabled because honestly nobody raises anyways
        return False 
        
    def travel_to_trough_bed(self) -> None:
        """Travels to the stations secondary bed, that has a `b` in front
        of its numeric suffix created by the beds `create_secondary` method.
        """
        new_bed = self.station_data.beds[self.current_bed].create_secondary("b")

        self.bed_map.travel_to(new_bed)
        self.tribelog.check_tribelogs()
        self.player.await_spawned()
        self.player.sleep(1)

    def approach_dire_bear(self) -> None:
        """Approaches the direbear by pressing 'w' until we can see the
        'Ride' text.

        TODO: Add error handling etc when the bear could not be reached.

        """
        counter = 0
        while not self.dire_bear.can_ride():
            self.player.walk("w", 0.1)
            counter += 1
            if counter > 8:
                return

    def get_meat(self) -> None:
        """Mounts the direbear, hits the meatplant 20 times and dismounts."""
        self.approach_dire_bear()
        self.dire_bear.mount()
        self.player.turn_y_by(160)

        for _ in range(20):
            self.dire_bear.attack("left")
            self.dire_bear.sleep(0.7)

        self.player.sleep(5)
        self.dire_bear.dismount()

    def walk_to_spawn(self) -> None:
        """Looks down on the ground and walks into the direction the bed should be
        at."""
        self.player.look_down_hard()
        direction = "a" if self.gacha_is_right() else "d"

        while not self.bed_map.can_be_accessed():
            self.player.walk(direction, 0.2)

    def crop_plots_need_pellets(self) -> bool:
        """Opens the crop plot and checks how many pellets are in it,
        returns a boolean determining if the crop plots need a pellet refill."""
        self.crop_plot.inventory.open()
        pellets_amount = self.crop_plot.inventory.count_item(PELLET)
        self.crop_plot.inventory.close()

        return pellets_amount <= 10

    def refill_crop_plots(self) -> None:
        """Refills the crop plots with pellets."""
        direction = "left" if self.gacha_is_right() else "right"
        self.player.turn_90_degrees(direction)
        self.player.do_precise_crop_plot_stack(refill_pellets=True, max_index=6)
        self.player.empty_inventory()

    def take_meat_from_bear(self) -> int:
        """Takes the raw meat from the dire bear above.
        Returns how much meat was taken from the bear
        """
        direction = "a" if self.gacha_is_right() else "d"
        self.player.walk(direction, 0.5)
        self.player.look_up_hard()
        direction = "right" if self.gacha_is_right() else "left"
        self.player.turn_90_degrees(direction, delay=0.5)

        attempt = 0
        while not self.dire_bear.can_access():
            self.player.turn_y_by(6)
            self.player.sleep(0.5)
            attempt += 1
            if attempt > 20:
                raise InventoryNotAccessibleError

        self.dire_bear.inventory.open()
        self.dire_bear.inventory.take_all_items(RAW_MEAT)
        self.player.inventory.await_items_added()
        self.player.sleep(0.5)
        meat = self.player.inventory.get_amount_transferred(RAW_MEAT, "add")

        self.dire_bear.inventory.click_drop_all()
        self.dire_bear.inventory.close()

        self.player.sleep(1)
        self.player.look_down_hard()
        self.bed_map.lay_down()

        if self.gacha_is_right():
            for _ in range(2):
                self.player.sleep(0.5)
                self.player.turn_90_degrees("left")
        self.player.sleep(1)
        return meat

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
            title=f"Finished meat station {self.station_data.beds[self.current_bed].name}!",
            color=0xFC97E8,
        )

        embed.add_field(name="Time taken:ㅤ", value=f"{statistics.time_taken} seconds")
        embed.add_field(
            name="Meat deposited:ㅤ", value=f"~{statistics.profit[RAW_MEAT]}"
        )
        embed.add_field(name="Pellets refilled", value=statistics.refill_lap)

        embed.set_thumbnail(url=RAW_MEAT_AVATAR)
        embed.set_footer(text="Ling Ling on top!")
        return embed

    def complete(self) -> tuple[Embed, StationStatistics]:
        """Completes the station, returns an embed displaying the
        statistics, and the statistics object itself."""
        self.spawn()
        start = time.time()
        try:
            self.get_meat()
            self.walk_to_spawn()
            self.travel_to_trough_bed()
            need_refill = self.crop_plots_need_pellets()
            if need_refill:
                self.get_pellets(transfer_rows_back=10)
                self.refill_crop_plots()

            meat_harvested = self.take_meat_from_bear()
            self.fill_troughs(RAW_MEAT, popcorn=SPOILED_MEAT)

            stats = MeatStatistics(
                round(time.time() - start),
                need_refill,
                profit={RAW_MEAT: meat_harvested},
            )
            return self.create_embed(stats), stats

        finally:
            self.increment_bed_counter()
