from __future__ import annotations

import time
from datetime import datetime

from ark import Bed, Player, Structure, TekCropPlot, items
from discord import Embed  # type: ignore[import]

from ...webhooks import InfoWebhook, TribeLogWebhook
from ._small_meat_settings import SmallMeatStationSettings
from .feed_station import FeedStation


class SmallMeatStation(FeedStation):

    RAW_MEAT_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/e/e9/Raw_Meat.png/revision/latest/scale-to-width-down/228?cb=20150704150605"

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

        self.trough = Structure(f"Trough {name}", "assets/templates/tek_trough.png")
        self.vault = Structure(f"Vault {name}", "assets/templates/vault.png")
        self.crop_plot = TekCropPlot(name)
        self._load_last_completion("small_meat")

    @staticmethod
    def build_stations(
        player: Player, tribelog: TribeLogWebhook, info_webhook: InfoWebhook
    ) -> list[SmallMeatStation]:
        settings = SmallMeatStationSettings.load()
        if not settings.enabled:
            return []
        return [
            SmallMeatStation(
                f"{settings.meat_prefix}{i:02d}",
                player,
                tribelog,
                info_webhook,
                settings.meat_interval,
            )
            for i in range(settings.meat_beds)
        ]

    def is_ready(self) -> bool:
        return super().is_ready()

    def complete(self) -> None:
        self.spawn()
        start = time.time()
        try:
            self._take_hatchet()
            self._harvest_plant()
            meat_in_trough = self._fill_trough()
            self._put_hatchet_back()
            self._webhook.send_embed(
                self.create_embed(round(time.time() - start), meat_in_trough)
            )
        finally:
            self.last_completed = datetime.now()
            self.set_completed_date("small_meat")

    def _take_hatchet(self) -> None:
        for _ in range(2):
            self._player.turn_90_degrees(delay=1)

        self.vault.open()
        self.vault.inventory.take(items.HATCHET, amount=1)
        self._player.inventory.equip(items.HATCHET, is_armor=False)
        self.vault.close()
        self._player.sleep(2)

    def _harvest_plant(self) -> None:
        for _ in range(2):
            self._player.turn_90_degrees(delay=1)

        while self.crop_plot.plant_is_visible():
            self._player.attack()
            self._player.sleep(0.3)

    def _fill_trough(self) -> int:
        self._player.sleep(1)
        self._player.turn_90_degrees("left")
        self._player.turn_y_by(80)

        self.trough.open()
        if self.trough.inventory.has(items.SPOILED_MEAT):
            self.trough.inventory.transfer_all(items.SPOILED_MEAT)
        self._player.inventory.transfer_all()
        meat = self.trough.inventory.count(items.RAW_MEAT) * 40
        self.trough.close()
        self._player.sleep(2)
        return meat

    def _put_hatchet_back(self) -> None:
        self._player.turn_y_by(-80)
        self._player.turn_90_degrees("left", delay=1)

        self.vault.open()
        self._player.inventory.transfer_all(items.HATCHET)
        self.vault.close()

    def create_embed(self, time_taken: int, meat_in_trough: int) -> Embed:
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
            title=f"Finished small meat station {self._name}!",
            color=0xFC97E8,
        )

        embed.add_field(name="Time taken:ㅤ", value=f"{time_taken} seconds")
        embed.add_field(name="Meat in trough:ㅤ", value=f"{meat_in_trough}")

        embed.set_thumbnail(url=self.RAW_MEAT_AVATAR)
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")
        return embed
