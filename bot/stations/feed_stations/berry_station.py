import json
import time
from datetime import datetime

from ark import Bed, Dinosaur, Player, TribeLog, exceptions, items
from discord import Embed  # type: ignore[import]

from ...webhooks import InfoWebhook
from .._crop_plot_helper import do_crop_plot_stack
from .feed_station import FeedStation


class BerryFeedStation(FeedStation):
    """Handles the auto berry station. The purpose of the station is to
    take mejoberries from crop plots to raise dinos in its area, or to
    pile up on berries for use elsewhere. on 500% greenhouse effect it
    takes 5 hours to fully regenerate.
    """

    MEJOBERRY_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/0/00/Mejoberry.png/revision/latest/scale-to-width-down/228?cb=20160219215159"

    def __init__(
        self,
        name: str,
        player: Player,
        tribelog: TribeLog,
        webhook: InfoWebhook,
        interval: int,
    ) -> None:
        super().__init__(name, player, tribelog, webhook, interval)
        self._load_last_completion("mejoberry")

    def do_crop_plots(self, got_pellets: bool) -> None:
        """Does the crop plot stack, finishes facing the last stack"""

        for turn in range(2):
            if turn or got_pellets:
                self._player.turn_90_degrees(
                    "left" if self.gacha_is_right() else "right"
                )

            do_crop_plot_stack(
                self._player,
                self._stacks[turn],
                items.MEJOBERRY,
                [-130, *[-17] * 5, 50, -17],
                [],
                precise=True,
                refill=got_pellets,
            )

    def create_embed(self, time_taken: int) -> Embed:
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
            title=f"Finished berry station {self.name}!",
            color=0xFC97E8,
        )

        embed.add_field(name="Time taken:ㅤ", value=f"{time_taken} seconds")

        embed.set_thumbnail(url=self.MEJOBERRY_AVATAR)
        embed.set_footer(text="Ling Ling on top!")
        return embed

    def complete(self) -> None:
        """Runs the feed station."""
        self.spawn()
        start = time.time()

        try:
            self._player.crouch()
            took_pellets = self.check_get_pellets()
            self.do_crop_plots(took_pellets)
            self.fill_troughs(items.MEJOBERRY)

            self._webhook.send_embed(self.create_embed(round(time.time() - start)))

        finally:
            self.last_completed = datetime.now()

            with open("bot/_data/station_data.json") as f:
                data: dict = json.load(f)

            data["mejoberry"]["last_completed"] = self.last_completed

            with open("bot/_data/station_data.json", "w") as f:
                json.dump(data, f, indent=4, default=str)
