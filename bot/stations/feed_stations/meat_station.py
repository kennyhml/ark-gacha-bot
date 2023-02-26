import json
import time
from datetime import datetime

from ark import Bed, Dinosaur, Player, TribeLog, exceptions, items
from discord import Embed  # type: ignore[import]

from ...webhooks import InfoWebhook
from .._crop_plot_helper import do_crop_plot_stack
from .feed_station import FeedStation


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

    RAW_MEAT_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/e/e9/Raw_Meat.png/revision/latest/scale-to-width-down/228?cb=20150704150605"

    def __init__(
        self,
        name: str,
        player: Player,
        tribelog: TribeLog,
        webhook: InfoWebhook,
        interval: int,
    ) -> None:
        super().__init__(name, player, tribelog, webhook, interval)
        self.bear = Dinosaur("Dire Bear", "assets/templates/dire_bear.png")
        self._load_last_completion("meat")

    def travel_to_trough_bed(self) -> None:
        """Travels to the stations secondary bed, that has a `b` in front
        of its numeric suffix created by the beds `create_secondary` method.
        """
        name = self.bed.name
        new_bed = Bed(name[:-2] + "b" + name[-2:])

        self._player.prone()
        self._player.look_down_hard()

        new_bed.spawn()
        self._player.spawn_in()

    def approach_dire_bear(self) -> None:
        """Approaches the direbear by pressing 'w' until we can see the
        'Ride' text.
        """
        counter = 0
        while not self.bear.can_ride():
            self._player.walk("w", 0.1)
            counter += 1
            if counter > 8:
                return

    def get_meat(self) -> None:
        """Mounts the direbear, hits the meatplant 20 times and dismounts."""
        self.approach_dire_bear()
        self.bear.mount()
        self._player.turn_y_by(160)

        for _ in range(20):
            self.bear.attack("left")
            self.bear.sleep(0.7)

        self._player.sleep(5)
        self.bear.dismount()

    def walk_to_spawn(self) -> None:
        """Looks down on the ground and walks into the direction the bed should be
        at."""
        self._player.look_down_hard()
        direction = "a" if self.gacha_is_right() else "d"

        while not self.bed.interface.can_be_accessed():
            self._player.walk(direction, 0.2)

    def refill_crop_plots(self) -> None:
        """Refills the crop plots with pellets."""
        self._player.turn_90_degrees("left" if self.gacha_is_right() else "right")
        self._player.crouch()
        
        do_crop_plot_stack(
            self._player,
            self._stacks[0],
            None,
            [-130, *[-17] * 5, 50, -17],
            [],
            precise=True,
            refill=True,
        )
        self._player.drop_all()

    def take_meat_from_bear(self) -> int:
        """Takes the raw meat from the dire bear above.
        Returns how much meat was taken from the bear
        """
        direction = "a" if self.gacha_is_right() else "d"
        self._player.walk(direction, 0.5)
        self._player.look_up_hard()
        self._player.turn_90_degrees(
            "right" if self.gacha_is_right() else "left", delay=0.5
        )

        attempt = 0
        while not self.bear.can_access():
            self._player.turn_y_by(6)
            self._player.sleep(0.5)
            attempt += 1
            if attempt > 20:
                raise exceptions.InventoryNotAccessibleError

        self.bear.access()
        self.bear.inventory.transfer_all(items.RAW_MEAT)
        self._player.inventory.await_items_added(items.RAW_MEAT)
        self._player.sleep(0.5)
        meat = self._player.inventory.get_amount_transferred(items.RAW_MEAT, "add")

        self.bear.inventory.drop_all()
        self.bear.inventory.close()

        self._player.sleep(1)
        self._player.look_down_hard()

        self.bed.lay_down()
        self._player.sleep(1)
        self.bed.get_up()

        if self.gacha_is_right():
            for _ in range(2):
                self._player.sleep(0.5)
                self._player.turn_90_degrees("left")
        self._player.sleep(1)
        return meat

    def create_embed(self, time_taken: int, meat_profit: int, refilled: bool) -> Embed:
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
            title=f"Finished meat station {self._name}!",
            color=0xFC97E8,
        )

        embed.add_field(name="Time taken:ㅤ", value=f"{time_taken} seconds")
        embed.add_field(name="Meat deposited:ㅤ", value=f"~{meat_profit}")
        embed.add_field(name="Pellets refilled", value=refilled)

        embed.set_thumbnail(url=self.RAW_MEAT_AVATAR)
        embed.set_footer(text="Ling Ling on top!")
        return embed

    def complete(self) -> None:
        """Completes the station, returns an embed displaying the
        statistics, and the statistics object itself."""
        try:
            self.spawn()
            start = time.time()
            self.get_meat()
            self.walk_to_spawn()
            self.travel_to_trough_bed()

            need_refill = self.check_get_pellets()
            if need_refill:
                self.refill_crop_plots()

            meat_harvested = self.take_meat_from_bear()
            self.fill_troughs(items.RAW_MEAT, popcorn=items.SPOILED_MEAT)

            self._webhook.send_embed(
                self.create_embed(
                    round(time.time() - start), meat_harvested, need_refill
                )
            )
            self.last_completed = datetime.now()

        finally:
            with open("bot/_data/station_data.json") as f:
                data: dict = json.load(f)

            data["meat"]["last_completed"] = self.last_completed

            with open("bot/_data/station_data.json", "w") as f:
                json.dump(data, f, indent=4, default=str)
