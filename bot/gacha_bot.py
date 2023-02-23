import itertools
import json
import traceback
from typing import Iterable

from ark import Player, Server, TribeLog, UserSettings, exceptions

from bot.recovery import Unstucking

from .settings import TowerSettings
from .stations import (
    CrystalStation,
    GrindingStation,
    HealingStation,
    Station,
    YTrapStation,
)
from .webhooks import DiscordSettings, InfoWebhook, TimerWebhook


class GachaBot:
    """Main gacha bot control class. Loads up the settings and creates
    the stations. The basic concept is to have a list of `Station` objects
    which follow the `Station` Abstract Base Class and thus behave the same
    on a very low level.

    This allows to simply iterate over the stations and foreach check if it
    ready. The order they are arranged in can be seen as a priority order.
    """

    def __init__(self) -> None:
        print("Bot started, initializing gacha bot...")
        self.settings = TowerSettings.load()
        self.ark_settings = UserSettings.load()
        self.server = Server(self.ark_settings.last_server)
        self.create_webhooks()

        with open("settings/settings.json") as f:
            self.player = Player(**json.load(f)["player"])
        self.stations = self.create_stations()

        print("Initialization successful.")

    def create_stations(self) -> list[Station | Iterable[YTrapStation]]:
        """Creates a list of the stations the gacha bot will run, the stations
        are ordered by 'priority', e.g the crystal station comes first, the
        ytrap station comes last (if no other station was ready).

        Each of the stations follows the `Station` abstract base class
        and behave similar.
        """
        stations: list[Station | Iterable[YTrapStation]] = [
            HealingStation(self.player, self.tribelogs, self.info_webhook)
        ]

        grinding = GrindingStation(self.player, self.tribelogs, self.info_webhook)
        ytraps = self._create_ytrap_stations()
        crystal = self._create_crystal_stations(grinding)

        if self.settings.ytrap_station:
            stations.extend(crystal)

        if self.settings.grinding_station:
            stations.append(grinding)

        if self.settings.arb_station:
            ...

        if self.settings.meat_station:
            ...

        if self.settings.berry_station:
            ...

        if self.settings.ytrap_station:
            stations.append(ytraps)

        return stations

    def _create_ytrap_stations(self) -> itertools.cycle:
        stations = [
            YTrapStation(
                f"{self.settings.ytrap_prefix}{i:02d}",
                self.player,
                self.tribelogs,
                self.info_webhook,
            )
            for i in range(33, self.settings.ytrap_beds)
        ]
        return itertools.cycle(stations)

    def _create_crystal_stations(self, grinding=None, arb=None) -> list[CrystalStation]:
        return [
            CrystalStation(
                f"{self.settings.crystal_prefix}{i:02d}",
                self.player,
                self.tribelogs,
                self.info_webhook,
                self.timer_webhook,
                grinding,
                arb,
                gen2=self.settings.gen2,
            )
            for i in range(self.settings.crystal_beds)
        ]

    def create_webhooks(self) -> None:
        """Creates the webhooks from the discord settings, `None` if no webhook was passed."""
        try:
            settings = DiscordSettings.load()
            self.info_webhook = InfoWebhook(settings.webhook_gacha, settings.user_id)

            self.tribelogs = TribeLog(
                settings.webhook_alert, settings.webhook_logs, settings.user_id
            )
            self.timer_webhook = TimerWebhook(
                settings.webhook_state, self.server, self.tribelogs, settings.timer_pop
            )

        except Exception as e:
            print(f"Failed to create one or more webhooks!\n{e}")
            raise

    def do_next_task(self) -> None:
        """Gacha bots main call method, call repeatedly to keep doing the
        next task in line. Iterates over each station in our station list
        and checks for the first one to be ready.
        """
        try:
            for station in self.stations:
                if isinstance(station, Station):
                    if not station.is_ready():
                        continue
                    task = station

                elif isinstance(station, itertools.cycle):
                    task = next(station)

                task.complete()
                break

        except exceptions.TerminatedError:
            pass

        except exceptions.BedNotFoundError as e:
            # no point trying to unstuck, if we were stuck the bed
            # menu would not be open to begin with.
            self.info_webhook.send_error(f"Travelling to '{task}'", e)

        except Exception as e:
            print(traceback.format_exc())
            Unstucking(self.server, "epic", self.info_webhook).unstuck()
