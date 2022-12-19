import json
import time
from threading import Thread
from datetime import datetime

import discord
from dacite import from_dict

from ark.beds import Bed, BedMap, TekPod
from ark.console import Console
from ark.exceptions import (
    InventoryNotAccessibleError,
    TekPodNotAccessibleError,
    InventoryNotClosableError,
)
from ark.inventories import Inventory
from ark.entities import Player
from ark.server import Server
from ark.tribelog import TribeLog
from bot.ark_bot import ArkBot, TerminatedException
from bot.stations.crystal_collection import CrystalCollection
from bot.grind_bot import GrindBot
from bot.settings import DiscordSettings, TowerSettings
from bot.unstucking import UnstuckHandler
from bot.feed_station import BerryFeedStation, MeatFeedStation
import numpy as np


class GachaBot:

    discord_avatar = "https://i.kym-cdn.com/entries/icons/facebook/000/022/293/Bloodyshadow_rolled_user_shutupandsleepwith_i_m_bisexual_let_s_work_from__a48265eae6a474904cdc2cae9f184aad.jpg"

    whip_avatar = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/b/b9/Whip_%28Scorched_Earth%29.png/revision/latest/scale-to-width-down/228?cb=20160901213011"

    def __init__(self) -> None:
        super().__init__()
        self.load_settings()
        self.create_webhooks()
        return

        self.seed_beds = self.create_seed_beds()
        self.crystal_bed = self.create_crystal_bed()
        self.berry_beds = self.create_berry_beds()
        self.meat_beds = self.create_meat_beds()
        self.tek_pod = self.create_tek_pod()
        self.server = self.create_server()
        self.tribelogs = TribeLog(self.alert_webhook, self.logs_webhook)
        self.grinding = GrindBot(
            self.create_grinder_bed(), self.info_webhook, self.server
        )

        self._ytraps_deposited = 0
        self._total_dust_made = 0
        self._total_bps_made = 0
        self._total_pickups = 0
        self._laps_completed = 0
        self._current_bed = 0
        self._current_lap = 1
        self._station_times = []
        self._session_start = time.time()
        self.current_task = None
        self._first_pickup = True
        self._least_healed = time.time()
        self.last_emptied = time.time()
        self.lap_started = time.time()
        self.player = Player()
        self.beds = BedMap()
        self.inform_started()

    @property
    def current_bed(self) -> int:
        return self._current_bed

    @current_bed.setter
    def current_bed(self, value: int) -> None:
        self._current_bed = value

    def unstuck(self, task: str, error: str) -> None:
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

    def travel_to_station(self, station: Bed) -> None:
        """Wrapper for `BedMap` travel method. Travels to the given station
        and checks tribelogs during spawn animation.

        Parameters:
        -----------
        station :class:`Bed`
            The bed object to travel to
        """
        self.check_status()
        self.beds.travel_to(station)
        self.tribelogs.check_tribelogs()
        self.player.await_spawned()

    def inform_started(self) -> None:
        """Sends a message to discord that the bot has been started"""
        now = datetime.now()
        now = now.strftime("%H:%M")

        embed = discord.Embed(
            type="rich",
            title="Ling Ling has been started!",
            description=f"Ling Ling has been started at {now}!",
            color=0xF20A0A,
        )
        embed.add_field(name=f"Account:", value=self.tower_settings.account_name)
        embed.add_field(name=f"Server:", value=self.tower_settings.server_name)
        embed.set_thumbnail(url=self.whip_avatar)
        embed.set_footer(text="Ling Ling on top!")

        self.info_webhook.send(
            avatar_url=self.discord_avatar,
            embed=embed,
            username="Ling Ling",
        )

    def create_webhooks(self) -> None:
        """Creates the webhooks from the discord settings, `None` if no webhook was passed."""
        try:
            self.info_webhook = discord.Webhook.from_url(
                self.discord_settings.webhook_gacha,
                adapter=discord.RequestsWebhookAdapter(),
            )
        except Exception as e:
            print(f"Failed to create info webhook!\n{e}")

        try:
            self.alert_webhook = discord.Webhook.from_url(
                self.discord_settings.webhook_alert,
                adapter=discord.RequestsWebhookAdapter(),
            )
        except Exception as e:
            print(f"Failed to create alert webhook!\n{e}")

        try:
            self.logs_webhook = discord.Webhook.from_url(
                self.discord_settings.webhook_logs,
                adapter=discord.RequestsWebhookAdapter(),
            )
        except Exception as e:
            print(f"Failed to create tribelogs webhook!\n{e}")

    def create_seed_beds(self) -> list[Bed]:
        """Creates the seed bed names using the given prefix and the defined
        amount of beds, using leading nulls.

        Returns a list of `Bed` objects.
        """
        return [
            Bed(
                f"{self.tower_settings.seed_prefix}{i:02d}",
                self.tower_settings.bed_position,
            )
            for i in range(self.tower_settings.seed_beds)
        ]

    def create_crystal_bed(self) -> Bed:
        """Creates the crystal bed using the given prefix, using leading nulls.

        Returns a `Bed` object.
        """
        return Bed(
            f"{self.tower_settings.crystal_prefix}00",
            self.tower_settings.bed_position,
        )

    def create_tek_pod(self) -> TekPod:
        """Creates a tek pod using the given prefix in the settings.

        Returns a `TekPod` object.
        """
        return TekPod(
            self.tower_settings.pod_name,
            self.tower_settings.bed_position,
        )

    def create_grinder_bed(self) -> Bed:
        """Creates the grinder bed using a fix prefix.

        Returns a `Bed` object.
        """
        return Bed("grinding", (self.tower_settings.bed_position))

    def create_berry_beds(self) -> list[Bed]:
        """Creates the berry bed objects using the given prefix and the defined
        amount of beds, using leading nulls.

        Returns a list of `Bed` objects.
        """
        return [
            Bed(
                f"{self.tower_settings.berry_prefix}{i:02d}",
                self.tower_settings.bed_position,
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
                self.tower_settings.bed_position,
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

    def validate_dust_amount(self, amount: int) -> int:
        """Checks if the given amount of dust is valid compared to the usual average.

        Parameters:
        -----------
        amount :class:`int`:
            The amount of dust we think we got

        Returns:
        ----------
        The given amount if its within a valid range, else the average amount
        """
        # likely small amounts
        if self._ytraps_deposited < 15000:
            return amount

        try:
            average_amount = round(self._total_dust_made / self._total_pickups)
        except ZeroDivisionError:
            # assume 6000 dust / minute, or 100 / second
            average_amount = round(100 * self.tower_settings.crystal_interval)

        if average_amount - 5000 < amount < average_amount + 10000:
            return amount
        return average_amount

    def do_crystal_station(self, bed: Bed) -> bool:
        """Completes the crystal collection station of the given bed.

        Travels to the crystal station, picks, opens and deposits crystals and
        puts away the items into the vault as configured by the user.

        Keeps track of the amounts it has deposited into dedis and returns them.

        Parameters:
        -----------
        bed :class:`Bed`:
            The crystal bed to spawn at
        """
        self.current_task = "Crystal Collection"
        try:
            # spawn at crystal bed and pick up the crystals
            crystals = CrystalCollection(self.player)
            self.travel_to_station(bed)
            crystals.pick_crystals()

            # open the crystals and deposit the items into dedis
            crystals_opened = crystals.open_crystals(self._first_pickup)
            resources_deposited, time_taken = crystals.deposit_dedis()
            resources_deposited["Element Dust"] = self.validate_dust_amount(
                resources_deposited["Element Dust"]
            )
            self._first_pickup = False

            # put items into vault
            vault_full = crystals.deposit_items(self.tower_settings.drop_items)

            self.inform_resources_deposited(
                time_taken, crystals_opened, resources_deposited, bed
            )
            self._total_pickups += 1
            self._total_dust_made += resources_deposited["Element Dust"]
            self._total_bps_made += resources_deposited["Black Pearl"]

            return vault_full

        except TerminatedException:
            pass

        except Exception as e:
            self.unstuck(self.current_task, e)

        finally:
            self.last_emptied = time.time()

    def do_berry_station(self) -> None:
        try:
            for bed in self.berry_beds:
                station = BerryFeedStation(bed)
                station.run()

        finally:
            time = datetime.now()  # save this timestamp for later comparison
            np_format = np.array(
                [time.year, time.month, time.day, time.hour, time.minute]
            )  # all numeric values
            np.save("temp/last_berry_harvest.npy", np_format)

    def do_meat_station(self) -> None:
        try:
            for bed in self.meat_beds:
                station = MeatFeedStation(bed)
                station.run()

        finally:
            time = datetime.now()  # save this timestamp for later comparison
            np_format = np.array(
                [time.year, time.month, time.day, time.hour, time.minute]
            )  # all numeric values
            np.save("temp/last_meat_harvest.npy", np_format)

    def do_gacha_station(self, bed: Bed) -> None:
        """Completes the gacha station of the given bed.

        Travels to the gacha station and fills up the gacha. On the first lap it will
        take pellets from the gacha to deposit into crop plots. After finishing it will
        post the stations time taken and the amount of y-traps deposited.

        Parameters:
        -----------
        bed :class:`Bed`:
            The bed of the station to travel to

        Handles:
        -----------
            `InventoryNotAccessible` Exception if the gacha could not be opened
        """
        # set times and tasks, travel to station
        self.travel_to_station(bed)
        start = time.time()
        self.current_task = f"Gacha Station {self.current_bed + 1}"

        # do the crop plots and load the gacha, post records
        try:
            gacha = Gacha()
            self.take_pellets_from_gacha(gacha)
            self.player.do_precise_crop_plots(
                item=y_trap, refill_pellets=self._current_lap == 1
            )
            added_traps = self.player.load_gacha(gacha)
            self._ytraps_deposited += added_traps * 10
            self.inform_station_finished(bed, round(time.time() - start), added_traps)
            self._station_times.append(round(time.time() - start))

        except (InventoryNotAccessibleError, InventoryNotAccessibleError) as e:
            self.unstuck(f"Seeding Gacha {self.current_bed + 1}", e)

        finally:
            self.increment_counter()

    def format_time_taken(self, time_taken: time.time) -> str:
        """Returns the given time.time object in a formatted string"""
        # get time diff
        time_diff = time.time() - time_taken

        # get hours and minutes, round for clean number
        h = round(time_diff // 3600)
        m, s = divmod(time_diff % 3600, 60)
        m, s = round(m), round(s)

        # format
        return f"{h} hour{'s' if h > 1 or not h else ''} {m} minutes"

    def get_dust_per_hour(self) -> int:
        total_minutes = round(time.time() - self._session_start) / 60
        return f"{round((self._total_dust_made / total_minutes) * 60):_}".replace(
            "_", " "
        )

    def inform_error(self, task: str, exception: Exception) -> None:
        """Posts an image of the current screenshot alongside current
        bed and the exception to discord for debugging purposes.

        Parameters:
        ------------
        bed :class:`Bed`:
            The bed (station) the exception occured at

        exception: :class:`Exception`:
            The description of the occured exception
        """
        embed = discord.Embed(
            type="rich",
            title="Ran into an unhandled exception!",
            description="Something went wrong! Attempting to unstuck..",
            color=0xF20A0A,
        )

        embed.add_field(name=f"Task:", value=task if task else "?")
        embed.add_field(name=f"Error:", value=exception if exception else "?")

        file = discord.File(
            self.grab_screen((0, 0, 1920, 1080), "temp/unknown_error.png"),
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
                "avatar_url": self.discord_avatar,
            },
        ).start()

    def inform_station_finished(self, bed: Bed, time: int, traps: int) -> None:
        """Sends the statistics of a gachaseed station after finishing it.

        Parameters:
        -----------
        bed :class:`Bed`:
            The bed (station) that was finished.

        time :class:`int`:
            The time taken to finish the station.

        traps :class:`int`:
            The amount of traps that have been put into the gacha.
        """

        embed = discord.Embed(
            type="rich",
            title=f"Finished gacha station {bed.name}!",
            description=(self.validate_station_stats(traps, time)),
            color=0xFC97E8,
        )

        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{time} seconds")
        embed.add_field(name="Y-Traps deposited:", value=f"{traps * 10}")

        # embed.add_field(name="\u200b", value="\u200b")

        embed.set_thumbnail(url=self.y_trap_avatar)

        embed.set_footer(text="Ling Ling on top!")

        self.info_webhook.send(
            avatar_url=self.discord_avatar,
            embed=embed,
            username="Ling Ling",
        )

    def inform_inventory_not_accessible(self, bed: Bed, inventory: Inventory) -> None:
        """Inform the user that the gacha cannot be accessed"""

        if inventory == "Gacha":
            formatted_text = (
                f"Gacha at `{bed.name}` could not be accessed.\n"
                f"Please move the gacha closer, or improve the bed placement.\n"
                f"Server: {self.tower_settings.server_name}, Account: {self.tower_settings.account_name}"
            )
        else:
            formatted_text = (
                f"{inventory} at `{bed.name}` could not be accessed.\n"
                f"This may have been caused by lag, otherwise please improve your placement.\n"
                f"Server: {self.tower_settings.server_name}, Account: {self.tower_settings.account_name}"
            )

        Thread(
            target=self.send_to_discord,
            name="Posting to discord",
            args=(
                self.info_webhook,
                formatted_text,
                self.grab_screen((0, 0, 1920, 1080), "temp/access_error.png"),
                "Ling Ling",
                self.discord_avatar,
            ),
        ).start()

    def inform_resources_deposited(
        self, time: int, crystals: int, resources: dict, bed: Bed
    ) -> None:

        dust = f"{resources['Element Dust']:_}".replace("_", " ")
        pearls = f"{resources['Black Pearl']:_}".replace("_", " ")

        embed = discord.Embed(
            type="rich",
            title=f"Collected crystals at {bed.name}!",
            color=0x07F2EE,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{time} seconds")
        embed.add_field(name="Crystals opened:", value=f"{crystals} crystals")

        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="Dust made:", value=f"{dust}")
        embed.add_field(name="Black Pearls made:", value=f"{pearls}")
        embed.add_field(name="\u200b", value="\u200b")

        embed.set_thumbnail(url=self.crystal_avatar)
        embed.set_footer(text="Ling Ling on top!")

        self.info_webhook.send(
            avatar_url=self.discord_avatar,
            embed=embed,
            username="Ling Ling",
        )

    def inform_healed_up(self, time_spent, last_healed) -> None:
        """Sends a msg to discord that we healed"""
        embed = discord.Embed(
            type="rich",
            title=f"Recovered player at '{self.tek_pod.name}'!",
            color=0x4F4F4F,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{time_spent} seconds")
        embed.add_field(name="Last healed:", value=self.format_time_taken(last_healed))
        embed.set_thumbnail(url=self.tek_pod.discord_image)
        embed.set_footer(text="Ling Ling on top!")

        self.info_webhook.send(
            avatar_url=self.discord_avatar,
            embed=embed,
            username="Ling Ling",
        )

    def inform_lap_finished(self) -> None:

        station_avg = round(sum(self._station_times) / len(self._station_times))

        dust = f"{self._total_dust_made:_}".replace("_", " ")
        pearls = f"{self._total_bps_made:_}".replace("_", " ")

        embed = discord.Embed(
            type="rich",
            title=f"Finished Lap {self._current_lap}!",
            color=0x4285D7,
        )
        embed.add_field(
            name="Time taken:ㅤㅤㅤ", value=self.format_time_taken(self.lap_started)
        )

        embed.add_field(
            name="Total runtime:ㅤㅤㅤ",
            value=self.format_time_taken(self._session_start),
        )
        embed.add_field(name="\u200b", value="\u200b")

        embed.add_field(
            name="Average station time:ㅤㅤㅤ",
            value=f"{station_avg} seconds",
        )

        embed.add_field(
            name="Dust per hour:ㅤㅤㅤ",
            value=f"{self.get_dust_per_hour()}",
        )
        embed.add_field(name="\u200b", value="\u200b")

        embed.add_field(name="Total Element Dust:", value=f"{dust}")
        embed.add_field(name="Total Black Pearls:", value=f"{pearls}")
        embed.add_field(name="\u200b", value="\u200b")

        embed.set_thumbnail(url=self.dust_avatar)
        embed.set_footer(text="Ling Ling on top!")

        self.info_webhook.send(
            avatar_url=self.discord_avatar,
            embed=embed,
            username="Ling Ling",
        )

    def validate_station_stats(self, traps_amount, time_taken) -> str:
        """Checks on the amount of traps deposited given the current runtime.
        Returns a string verifying if the amount is valid or not.
        """

        result = ""

        # different expectations for first lap (more tasks, dead crop plots)
        if not self._laps_completed:
            if time_taken > 150:
                return "Time taken was unusually long, even for the first lap!"
            return f"Station works as expected for the first lap!"

        # check trap amount, 300 traps might be set a little low
        if traps_amount < 30:
            result += f"The amount of Y-Traps deposited is too low.\n"

        # check time taken for station, might increase
        if time_taken > 140:
            result += f"The time taken was unsually long!"

        return result if result else "Station works as expected."

    def crystals_need_pickup(self) -> bool:
        """True if more than the set interval passed since last picking the
        crystals and either more than 2000 ytraps have been collected or
        we are already on our second lap.
        """
        time_diff = time.time() - self.last_emptied

        return time_diff > self.tower_settings.crystal_interval and (
            self._ytraps_deposited > 2000 or self._laps_completed
        )

    def berries_are_ready(self) -> bool:
        """Checks if berries are ready for harvest by checking
        wether more than 5 hours have passed since the last harvest.
        
        The last harvest is stored as datetime object.
        """
        saved = np.load("temp/last_berry_harvest.npy")
        loaded_time = datetime(*saved)
        now = datetime.now()

        # comparison in minutes
        diff = (now - loaded_time).total_seconds()/3600.
        print(f"{diff} hours passed since last berry session")
        return diff >= 5

    def meat_is_ready(self) -> bool:
        """Checks if berries are ready for harvest by checking
        wether more than 5 hours have passed since the last harvest.
        
        The last harvest is stored as datetime object.
        """
        saved = np.load("temp/last_meat_harvest.npy")
        loaded_time = datetime(*saved)
        now = datetime.now()

        # comparison in minutes
        diff = (now - loaded_time).total_seconds()/3600.
        print(f"{diff} hours passed since last meat session")
        return diff >= 1

    def electronics_finished(self) -> bool:
        """Returns true if there is an ongoing grinding session and more than
        3 minutes have passed since the last electronics craft."""
        try:
            return (
                self.grinding.session_cost
                and (time.time() - self.grinding.last_crafted) > 180
            )
        except TypeError:
            return False

    def do_next_task(self) -> None:
        """Gacha bot main call method, runs the next task in line.

        Current tasks are: Healing, crafting electronics, picking crystals,
        gacha feeding and grinding gear where healing wont block the next task.
        """

        try:
            self.check_status()
            # check if we need to go heal
            if self.player.needs_recovery():
                self.go_heal()

            # check if any electronics are crafting and if they need to be requeued
            if self.electronics_finished():
                self.current_task = "Grinding Station"
                if not self.grinding.need_to_craft_electronics():
                    self.grinding.craft_turrets()
                
            # check if its time to pick crystals
            elif self.crystals_need_pickup():
                # returns true if the vault is filled and we need to start grinding
                if self.do_crystal_station(self.crystal_bed):
                    self.grinding.run()
                return

            elif self.berries_are_ready():
                self.do_berry_station()

            elif self.meat_is_ready():
                self.do_meat_station()

            else:
                # do regular gacha seeding task
                self.do_gacha_station(self.seed_beds[self.current_bed])

        except TerminatedException:
            pass

        except Exception as e:
            self.unstuck(self.current_task, e)

    def increment_counter(self) -> None:
        # increment bed counter, make sure its not out of range!
        if self.current_bed < self.tower_settings.seed_beds - 1:
            self.current_bed += 1
            return

        # reset bed counter, increment laps
        self.lap_finished()

    def lap_finished(self) -> None:
        self.current_bed = 0
        self._laps_completed += 1
        self.inform_lap_finished()
        self._current_lap += 1
        self.lap_started = time.time()

    def go_heal(self) -> None:
        """Goes to heal by travelling to the tek pod, trying to enter it up to
        3 times. If it can not enter the tek pod, a `TekPodNotAccessible` Error
        is raised.
        """
        start = time.time()
        self.current_task = "Healing"
        # travel to the pod
        self.travel_to_station(self.tek_pod)

        # try to enter the pod 3 times
        for _ in range(3):
            if not self.tek_pod.enter():
                self.sleep(1)
                continue

            self.tek_pod.heal(60)
            self.tek_pod.leave()
            self.inform_healed_up(round(time.time() - start), self._least_healed)
            self._least_healed = time.time()
            return

        # we cant heal, raise an error so we can try to unstuck
        raise TekPodNotAccessibleError("Failed to access the tek pod!")
