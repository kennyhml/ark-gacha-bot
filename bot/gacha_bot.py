import json
import time
from datetime import datetime
from threading import Thread

from dacite import from_dict
from discord import Embed, File, RequestsWebhookAdapter, Webhook  # type: ignore[import]

from ark.beds import Bed, TekPod
from ark.entities import Player, stryder
from ark.server import Server
from ark.tribelog import TribeLog
from ark.window import ArkWindow
from bot.ark_bot import ArkBot, TerminatedException
from bot.settings import DiscordSettings, TowerSettings
from bot.stations import (
    BerryFeedStation,
    CrystalStation,
    GrindingStation,
    HealingStation,
    MeatFeedStation,
    Station,
    StationData,
    YTrapStation,
)
from bot.stations.arb.arb_station import ARBStation
from bot.unstucking import UnstuckHandler

DISCORD_AVATAR = "https://i.kym-cdn.com/entries/icons/facebook/000/022/293/Bloodyshadow_rolled_user_shutupandsleepwith_i_m_bisexual_let_s_work_from__a48265eae6a474904cdc2cae9f184aad.jpg"
WHIP_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/b/b9/Whip_%28Scorched_Earth%29.png/revision/latest/scale-to-width-down/228?cb=20160901213011"


class GachaBot:
    def __init__(self) -> None:
        super().__init__()
        self.load_settings()
        self.create_webhooks()
        self.server = self.create_server()
        self.screen = ArkWindow()
        self.tribelogs = TribeLog(self.alert_webhook, self.logs_webhook)
        self.player = Player()
        self.stations = self.create_stations()

        return

    def create_stations(self) -> list[Station]:
        """Creates a list of the stations the gacha bot will run, the stations
        are ordered by 'priority', e.g the crystal station comes first, the
        ytrap station comes last (if no other station was ready).

        Each of the stations follows the `Station` abstract base class
        and behave very similar.
        """
        # create all the station data, seperately to the station itself to
        # allow for more readability and easier adjustments.
        healing_data = StationData(interval=0, beds=self.create_healing_bed())
        ytrap_data = StationData(interval=0, beds=self.create_seed_beds())
        crystal_data = StationData(
            interval=self.tower_settings.crystal_interval,
            beds=self.create_crystal_bed(),
        )
        meat_data = StationData(
            interval=3 * 3600,
            beds=self.create_meat_beds(),
            npy_path="temp/last_meat_harvest.npy",
        )
        berry_data = StationData(
            interval=10 * 3600,
            beds=self.create_berry_beds(),
            npy_path="temp/last_berry_harvest.npy",
        )

        arb_data = StationData(
            interval=0,
            beds=self.create_arb_bed(),
        )

        # create grinding station first so we can pass it to YTrapStation,
        # so it can set it to ready when the vaults are full.
        grinding_station = GrindingStation(
            StationData(interval=0, beds=self.create_grinder_bed()),
            self.player,
            self.tribelogs,
        )
        ytrap_station = YTrapStation(ytrap_data, self.player, self.tribelogs)
        arb_station = ARBStation(arb_data, self.player, self.tribelogs)

        # create the list of stations in desired priority order
        return [
            HealingStation(healing_data, self.player, self.tribelogs),
            CrystalStation(
                crystal_data,
                self.player,
                self.tribelogs,
                grinding_station,
                ytrap_station,
                arb_station,
                self.tower_settings.stryder_depositing,
            ),
            grinding_station,
            MeatFeedStation(meat_data, self.player, self.tribelogs),
            BerryFeedStation(berry_data, self.player, self.tribelogs),
            ytrap_station,
        ]

    def unstuck(self, task: Station, error: Exception) -> None:
        """Attempts to unstuck when the bot has failed to proceed from the current task.
        Terminates the bot entirely on failure.

        Parameters:
        ------------
        task :class:`str`:
            The task the bot got stuck at [for discord information]

        error :class:`str`:
            The error the bot got stuck with [for discord information]
        """
        self.inform_error(task, error)
        unstucking = UnstuckHandler(self.server)
        if not unstucking.attempt_fix():
            print("Failed to unstuck...")
            ArkBot.running = False

        print("Unstucking successful!")
        if unstucking.reconnected:
            self.last_emptied = time.time()

    def inform_started(self) -> None:
        """Sends a message to discord that the bot has been started"""
        now = datetime.now()
        now_time = now.strftime("%H:%M")

        embed = Embed(
            type="rich",
            title="Ling Ling has been started!",
            description=f"Ling Ling has been started at {now_time}!",
            color=0xF20A0A,
        )
        embed.add_field(name=f"Account:", value=self.tower_settings.account_name)
        embed.add_field(name=f"Server:", value=self.tower_settings.server_name)
        embed.set_thumbnail(url=WHIP_AVATAR)
        embed.set_footer(text="Ling Ling on top!")

        self.info_webhook.send(
            avatar_url=DISCORD_AVATAR,
            embed=embed,
            username="Ling Ling",
        )

    def create_webhooks(self) -> None:
        """Creates the webhooks from the discord settings, `None` if no webhook was passed."""
        try:
            self.info_webhook: Webhook = Webhook.from_url(
                self.discord_settings.webhook_gacha,
                adapter=RequestsWebhookAdapter(),
            )

            self.alert_webhook: Webhook = Webhook.from_url(
                self.discord_settings.webhook_alert,
                adapter=RequestsWebhookAdapter(),
            )

            self.logs_webhook: Webhook = Webhook.from_url(
                self.discord_settings.webhook_logs,
                adapter=RequestsWebhookAdapter(),
            )
        except Exception as e:
            print(f"Failed to create one or more webhooks!\n{e}")
            raise TerminatedException

    def create_seed_beds(self) -> list[Bed]:
        """Creates the seed bed names using the given prefix and the defined
        amount of beds, using leading nulls.

        Returns a list of `Bed` objects.
        """
        return [
            Bed(
                f"{self.tower_settings.seed_prefix}{i:02d}",
                tuple(self.tower_settings.bed_position),
            )
            for i in range(self.tower_settings.seed_beds)
        ]

    def create_crystal_bed(self) -> list[Bed]:
        """Creates the crystal bed using the given prefix, using leading nulls.

        Returns a `Bed` object.
        """
        return [
            Bed(
                f"{self.tower_settings.crystal_prefix}",
                tuple(self.tower_settings.bed_position),
            )
        ]

    def create_healing_bed(self) -> list[Bed]:
        """Creates a tek pod using the given prefix in the settings.

        Returns a `TekPod` object.
        """
        return [
            Bed(
                self.tower_settings.pod_name,
                tuple(self.tower_settings.bed_position),
            )
        ]

    def create_grinder_bed(self) -> list[Bed]:
        """Creates the grinder bed using a fix prefix.

        Returns a `Bed` object.
        """
        return [Bed("grinding", tuple(self.tower_settings.bed_position))]

    def create_arb_bed(self) -> list[Bed]:
        """Creates the arb bed objects using the given prefix and the defined
        amount of beds, using leading nulls.

        Returns a list of `Bed` objects.
        """
        return [
            Bed(
                f"arb_craft",
                tuple(self.tower_settings.bed_position),
            )
        ]

    def create_berry_beds(self) -> list[Bed]:
        """Creates the berry bed objects using the given prefix and the defined
        amount of beds, using leading nulls.

        Returns a list of `Bed` objects.
        """
        return [
            Bed(
                f"{self.tower_settings.berry_prefix}{i:02d}",
                tuple(self.tower_settings.bed_position),
            )
            for i in range(self.tower_settings.berry_beds)
        ]

    def create_meat_beds(self) -> list[Bed]:
        """Creates the berry bed objects using the given prefix and the defined
        amount of beds, using leading nulls.

        Returns a list of `Bed` objects.
        """
        return [
            Bed(
                f"{self.tower_settings.meat_prefix}{i:02d}",
                tuple(self.tower_settings.bed_position),
            )
            for i in range(self.tower_settings.meat_beds)
        ]

    def create_server(self) -> Server:
        """Creates the server given the information in the settings. Relevant
        for reconnecting to the server during unstucking.

        Returns a `Server` object.
        """
        return Server(
            self.tower_settings.server_name, self.tower_settings.server_search
        )

    def load_settings(self) -> None:
        """Loads the configuration for the selected tower.
        Uses dactite.from_dict to load the dictionary into corresponding dataclasses.

        Raises:
        -----------
        `TerminatedException` if the configs could not be loaded.

        """
        try:
            with open("settings/settings.json", "r") as f:
                self.tower_settings = from_dict(TowerSettings, json.load(f))

            with open("settings/settings.json", "r") as f:
                self.discord_settings = from_dict(DiscordSettings, json.load(f))

        except Exception as e:
            print(f"CRITICAL! Error loading settings!\n{e}")
            ArkBot.running = False

    def get_dust_per_hour(self) -> int:
        return 0
        # total_minutes = round(time.time() - self._session_start) / 60
        # return f"{round((self._total_dust_made / total_minutes) * 60):_}".replace(
        #     "_", " "
        # )

    def inform_error(self, task: Station, exception: Exception) -> None:
        """Posts an image of the current screenshot alongside current
        bed and the exception to discord for debugging purposes.

        Parameters:
        ------------
        bed :class:`Bed`:
            The bed (station) the exception occured at

        exception: :class:`Exception`:
            The description of the occured exception
        """
        embed = Embed(
            type="rich",
            title="Ran into a problem!",
            description="Something went wrong! Attempting to unstuck..",
            color=0xF20A0A,
        )

        embed.add_field(name=f"Task:", value=type(task).__name__)
        embed.add_field(name=f"Error:", value=exception)

        file = File(
            self.screen.grab_screen((0, 0, 1920, 1080), "temp/unknown_error.png"),
            filename="image.png",
        )
        embed.set_image(url="attachment://image.png"),

        Thread(
            target=self.info_webhook.send,
            name="Posting to discord",
            kwargs={
                "username": "Ling Ling",
                "embed": embed,
                "file": file,
                "avatar_url": DISCORD_AVATAR,
            },
        ).start()

    #    def inform_lap_finished(self) -> None:
    #
    #        station_avg = round(sum(self._station_times) / len(self._station_times))
    #
    #        dust = f"{self._total_dust_made:_}".replace("_", " ")
    #        pearls = f"{self._total_bps_made:_}".replace("_", " ")
    #
    #        embed = discord.Embed(
    #            type="rich",
    #            title=f"Finished Lap {self._current_lap}!",
    #            color=0x4285D7,
    #        )
    #        embed.add_field(
    #            name="Time taken:ㅤㅤㅤ", value=self.format_time_taken(self.lap_started)
    #        )
    #
    #        embed.add_field(
    #            name="Total runtime:ㅤㅤㅤ",
    #            value=self.format_time_taken(self._session_start),
    #        )
    #        embed.add_field(name="\u200b", value="\u200b")
    #
    #        embed.add_field(
    #            name="Average station time:ㅤㅤㅤ",
    #            value=f"{station_avg} seconds",
    #        )
    #
    #        embed.add_field(
    #            name="Dust per hour:ㅤㅤㅤ",
    #            value=f"{self.get_dust_per_hour()}",
    #        )
    #        embed.add_field(name="\u200b", value="\u200b")
    #
    #        embed.add_field(name="Total Element Dust:", value=f"{dust}")
    #        embed.add_field(name="Total Black Pearls:", value=f"{pearls}")
    #        embed.add_field(name="\u200b", value="\u200b")
    #
    #        embed.set_thumbnail(url=self.dust_avatar)
    #        embed.set_footer(text="Ling Ling on top!")
    #
    #        self.info_webhook.send(
    #            avatar_url=self.discord_avatar,
    #            embed=embed,
    #            username="Ling Ling",
    #        )

    def do_next_task(self) -> None:
        """Gacha bot main call method, runs the next task in line.

        Current tasks are: Healing, crafting electronics, picking crystals,
        gacha feeding and grinding gear where healing wont block the next task.
        """

        try:
            for station in self.stations:
                if station.is_ready():
                    embed, stats = station.complete()
                    self.info_webhook.send(embed=embed)
                    print(stats)
                    return

        except TerminatedException:
            pass

        except Exception as e:
            self.unstuck(station, e)
