import ctypes
import itertools
import json
import os
import time
import traceback
from datetime import datetime, timedelta
from typing import Iterable

from ark import Console, Player, Server, TribeLog, UserSettings, config, exceptions
from discord import Embed  # type:ignore[import]

from . import tools
from .exceptions import ConfigError
from .recovery import Unstucking
from .settings import TowerSettings
from .stations import (
    ARBStation,
    BerryFeedStation,
    CrystalStation,
    GrindingStation,
    HealingStation,
    MeatFeedStation,
    MedbrewStation,
    SmallMeatStation,
    Station,
    YTrapStation,
)
from .webhooks import DiscordSettings, InfoWebhook, TimerWebhook, TribeLogWebhook


class GachaBot:
    """Main gacha bot control class. Loads up the settings and creates
    the stations. The basic concept is to have a list of `Station` objects
    which follow the `Station` Abstract Base Class and thus behave the same
    on a very low level.

    This allows to simply iterate over the stations and foreach check if it
    ready. The order they are arranged in can be seen as a priority order.
    """

    SESSION_START = datetime.now()

    def __init__(self) -> None:
        print("Bot started, initializing gacha bot...")
        self.settings = TowerSettings.load()
        self._set_environment()

        self.ark_settings = UserSettings.load()
        self.validate_game_settings(self.ark_settings)

        self.server = Server(self.ark_settings.last_server)
        self.create_webhooks()

        with open("settings/settings.json") as f:
            self.player = Player(**json.load(f)["player"])

        self.stations = self.create_stations()
        print("Initialization successful.")
        self.hour_start = datetime.now()

    def create_stations(self) -> list[Station | Iterable[YTrapStation]]:
        """Creates a list of the stations the gacha bot will run, the stations
        are ordered by 'priority', e.g the crystal station comes first, the
        ytrap station comes last (if no other station was ready).

        Each of the stations follows the `Station` abstract base class
        and behave similar.
        """
        base_args = (self.player, self.tribelogs, self.info_webhook)
        stations: list[Station | Iterable[YTrapStation]] = [HealingStation(*base_args)]

        grinding = GrindingStation(*base_args)
        arb = ARBStation(*base_args)
        ytrap = YTrapStation.build_stations(*base_args)
        crystal = CrystalStation.build_stations(
            *base_args,
            self.timer_webhook,
            grinding,
            arb,
            gen2=self.settings.map == "Genesis 2",
        )
        meat = MeatFeedStation.build_stations(*base_args)
        small_meat = SmallMeatStation.build_stations(*base_args)
        berry = BerryFeedStation.build_stations(*base_args)
        medbrew = MedbrewStation.build_stations(*base_args)

        for station in [
            crystal,
            grinding,
            arb,
            medbrew,
            meat,
            berry,
            small_meat,
            ytrap,
        ]:
            if not station:
                continue

            if isinstance(station, (Station, itertools.cycle)):
                stations.append(station)

            elif isinstance(station, list):
                stations.extend(station)

        return stations

    def create_webhooks(self) -> None:
        """Creates the webhooks from the discord settings, `None` if no webhook was passed."""
        try:
            settings = DiscordSettings.load()
            self.info_webhook = InfoWebhook(settings.webhook_gacha, settings.user_id)
            log = TribeLog()
            self.tribelogs = TribeLogWebhook(
                log, settings.webhook_alert, settings.webhook_logs
            )
            self.timer_webhook = TimerWebhook(
                settings.webhook_state, self.server, log, settings.timer_pop
            )
        except Exception as e:
            raise ConfigError(f"Failed to create one or more webhooks!\n{e}")

    def do_next_task(self) -> None:
        """Gacha bots main call method, call repeatedly to keep doing the
        next task in line. Iterates over each station in our station list
        and checks for the first one to be ready.
        """
        try:
            task = self._find_next_task()
            print(f"Found next task: '{task.name}'")
            task.complete()

            if (datetime.now() - self.hour_start) > timedelta(hours=1):
                self.post_total_statistics()
                self.hour_start = datetime.now()

        except exceptions.TerminatedError:
            pass

        except LookupError:
            print("No station is currently ready...")

        except ConnectionError as e:
            print(f"Ran into a connection error!\n{e}")

        except Exception as e:
            self.info_webhook.send_error(f"Station '{task}'", e)
            print(traceback.format_exc())
            self._unstuck()

    def post_total_statistics(self) -> None:
        runtime_diff = (datetime.now() - self.SESSION_START).total_seconds()
        total_runtime = tools.format_seconds(round(runtime_diff))

        embed = Embed(
            type="rich",
            title="Hourly statistics update:",
            description=f"Here is your hourly statistics update!",
            color=0x297AD1,
        )

        embed.add_field(name="Total runtime:", value=total_runtime)
        embed.add_field(
            name="Dust per hour:",
            value=f"{self._compute_dust_per_hour():_}".replace("_", " "),
        )
        embed.add_field(name="Laps completed:", value=YTrapStation.lap - 1)

        for statistic, amount in Station.statistics.items():
            if not amount:
                continue
            if "time" in statistic.lower():
                formatted_amount = f"{amount} seconds"
            else:
                formatted_amount = f"{amount:_}".replace("_", " ")

            embed.add_field(name=f"{statistic}:", value=formatted_amount)

        missing = 3 - len(embed.fields) % 3
        for _ in range(missing if missing != 3 else 0):
            embed.add_field(name="\u200b", value="\u200b")

        embed.set_thumbnail(
            url="https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/b/b1/Element_Dust.png/revision/latest/scale-to-width-down/228?cb=20181107161643"
        )
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")
        self.info_webhook.send_embed(embed)

    def _compute_dust_per_hour(self) -> int:
        return round(
            (
                Station.statistics.get("Element Dust", 0)
                / (datetime.now() - self.SESSION_START).total_seconds()
            )
            * 3600
        )

    def _find_next_task(self) -> Station:
        for station in self.stations:
            if isinstance(station, Station):
                if station.is_ready():
                    return station

            elif isinstance(station, itertools.cycle):
                return next(station)

        raise LookupError("Could not find a ready station!")

    def start(self) -> None:
        try:
            console = Console()
            console.set_gamma(5)

            self.player.set_first_person()
            self._inform_started()
        except exceptions.TerminatedError:
            print("Bot terminated!")
            pass

    def _unstuck(self) -> None:
        unstucking = Unstucking(
            self.server, self.player, self.settings.game_launcher, self.info_webhook
        )
        unstucking.unstuck()
        if not unstucking.reconnected:
            return

    def _inform_started(self) -> None:
        """Sends a message to discord that the bot has been started"""
        embed = Embed(
            type="rich",
            title="Ling Ling has been started!",
            description=f"Ling Ling has been started at <t:{round(time.time())}:t>!",
            color=0xF20A0A,
        )
        embed.add_field(name=f"Account:", value=self.settings.account_name)
        embed.add_field(name=f"Server:", value=self.server.name)
        embed.set_thumbnail(
            url="https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/b/b9/Whip_%28Scorched_Earth%29.png/revision/latest/scale-to-width-down/228?cb=20160901213011"
        )
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")

        self.info_webhook.send_embed(embed)

    @staticmethod
    def validate_game_settings(settings: UserSettings) -> None:
        s = settings

        expected_settings = {
            "Hide item names": (True, s.hide_item_names),
            "Show item tooltips": (False, s.show_item_tooltips),
            "Auto chatbox": (False, s.auto_chatbox),
            "Toggle HUD": (False, s.toggle_hud),
            "Disable Menu Transitions": (True, s.disable_menu_transitions),
            "Reverse tribelogs": (True, s.reverse_logs),
            "Local show all items": (True, s.local_show_all_items),
            "Remote show all items": (True, s.remote_show_all_items),
            "Local sort type": (1, s.sort_type),
            "Remote sort type": (1, s.remote_sort_type),
            "Remote show engrams": (False, s.remote_show_engrams),
            "Remote hide unlearned engrams": (True, s.remote_hide_unlearned_engrams),
            "In remote crafting": (False, s.in_remote_inventory),
        }
        incorrect = [
            setting
            for setting, value in expected_settings.items()
            if value[0] != value[1]
        ]
        if not incorrect:
            return
        errors = "\n".join(
            f"{setting}: expected {expected_settings[setting][0]}, got {expected_settings[setting][1]}"
            for setting in incorrect
        )

        ctypes.windll.user32.MessageBoxW(
            None,
            f"Incorrect configurations:\n\n{errors}\n\nPlease fix these mismatches and try again.",
            f"ARK config mismatches!",
            0x1000,
        )
        raise ConfigError("Invalid ark settings.")

    def _set_environment(self) -> None:
        for path in [self.settings.ark_path, self.settings.tesseract_path]:
            if not os.path.exists(path):
                raise ConfigError(f"CONFIG ERROR! Path '{path}' does not exist.")

        config.ARK_PATH = self.settings.ark_path
        config.TESSERACT_PATH = self.settings.tesseract_path
