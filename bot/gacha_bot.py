import json
import time
from threading import Thread

import discord
from dacite import from_dict

from ark.beds import Bed, BedMap, TekPod
from ark.exceptions import InventoryNotAccessibleError, TekPodNotAccessibleError
from ark.inventories import Gacha, Inventory
from ark.items import pellet
from ark.player import Player
from bot.ark_bot import ArkBot, TerminatedException
from bot.crystal_collection import CrystalCollection
from ark.console import Console
from bot.settings import DiscordSettings, TowerSettings
from ark.tribelog import TribeLog

class GachaBot(ArkBot):

    discord_avatar = "https://i.kym-cdn.com/entries/icons/facebook/000/022/293/Bloodyshadow_rolled_user_shutupandsleepwith_i_m_bisexual_let_s_work_from__a48265eae6a474904cdc2cae9f184aad.jpg"
    y_trap_avatar = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/c/cb/Plant_Species_Y_Trap_%28Scorched_Earth%29.png/revision/latest?cb=20160901233007"
    crystal_avatar = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/c/c3/Gacha_Crystal_%28Extinction%29.png/revision/latest?cb=20181108100408"
    dust_avatar = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/b/b1/Element_Dust.png/revision/latest/scale-to-width-down/228?cb=20181107161643"

    def __init__(self) -> None:
        super().__init__()
        self.load_settings()
        self.create_webhooks()
        self.tribelogs = TribeLog(self.alert_webhook, self.logs_webhook)
        self.seed_beds = self.create_seed_beds()
        self.crystal_beds = self.create_crystal_beds()
        self.tek_pod = self.create_tek_pod()

        self._ytraps_deposited = 0
        self._total_dust_made = 0
        self._total_bps_made = 0
        self._total_pickups = 0
        self._laps_completed = 0
        self._current_bed = 0
        self._current_lap = 0
        self._station_times = []
        self._session_start = time.time()

        self._first_pickup = True
        self._at_pod = False
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


    def inform_started(self) -> None:
        """Sends a message to discord that the bot has been started"""
        self.send_to_discord(
            self.info_webhook,
            "Ling Ling is starting!",
            name="Ling Ling",
            avatar=self.discord_avatar,
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
                name=f"{self.tower_settings.seed_prefix}{i:02d}",
                coords=(self.tower_settings.bed_x, self.tower_settings.bed_y),
            )
            for i in range(self.tower_settings.seed_beds)
        ]

    def create_crystal_beds(self) -> list[Bed]:
        """Creates the crystal bed names using the given prefix and the defined
        amount of beds, using leading nulls.

        Returns a list of `Bed` objects.
        """
        return [
            Bed(
                name=f"{self.tower_settings.crystal_prefix}{i:02d}",
                coords=(self.tower_settings.bed_x, self.tower_settings.bed_y),
            )
            for i in range(self.tower_settings.crystal_beds)
        ]

    def create_tek_pod(self) -> TekPod:
        """Creates a tek pod using the given prefix in the settings

        Returns a `TekPod` object
        """
        return TekPod(
            self.tower_settings.pod_name,
            (self.tower_settings.bed_x, self.tower_settings.bed_y),
        )

    def load_settings(self) -> None:
        """Loads the configuration for the selected tower.
        Uses dactite.from_dict to load the dictionary into corresponding dataclasses.

        Parameters:
        -----------
        selected_tower :class:`int`:
            The index of the selected tower in the configs

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
            self._running = False

    def do_crystal_station(self, bed: Bed) -> None:
        """Completes the crystal collection station of the given bed.

        Travels to the crystal station, picks, opens and deposits crystals and
        puts away the items into the vault as configured by the user.

        Keeps track of the amounts it has deposited into dedis and returns them.

        Parameters:
        -----------
        bed :class:`Bed`:
            The crystal bed to spawn at
        """
        try:
            # spawn at crystal bed and pick up the crystals
            crystals = CrystalCollection(self.player)
            self.beds.travel_to(bed, self._at_pod)
            self.tribelogs.check_tribelogs()
            self.player.await_spawned()
            crystals.pick_crystals()

            # open the crystals and deposit the items into dedis
            crystals_opened = crystals.open_crystals(self._first_pickup)
            resources_deposited, time_taken = crystals.deposit_dedis()
            self._first_pickup = False

            # put items into vault
            crystals.deposit_items(
                self.tower_settings.drop_items,
                self.tower_settings.keep_items,
            )

            self.inform_resources_deposited(
                time_taken, crystals_opened, resources_deposited, bed
            )
            self._total_pickups += 1
            self._total_dust_made += resources_deposited["Element Dust"]
            self._total_bps_made += resources_deposited["Black Pearl"]

        except TerminatedException:
            pass

        except InventoryNotAccessibleError as err:
            self.inform_inventory_not_accessible(bed, err.args[0])

        except Exception as e:
            self.inform_unknown_exception(bed, e)

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
        gacha = Gacha()
        self.beds.travel_to(bed, self._at_pod)
        self.tribelogs.check_tribelogs()
        self.player.await_spawned()
        start = time.time()

        try:
            # check if we need to take pellets first
            if not self._laps_completed:
                if self.current_bed == 0:
                    Console().set_gamma()

                gacha.open()
                gacha.search_for("ll")
                self.sleep(0.3)
                if gacha.has_item(pellet):
                    gacha.take_all()
                    self.player.inventory.await_items_added()
                    self.sleep(0.5)
                    self.player.inventory.transfer_some_pellets(self.player.inventory)
                gacha.close()

            # do the crop plots and load the gacha, post records
            self.sleep(0.5)
            self.player.do_crop_plots()
            added_traps = self.player.load_gacha(gacha)
            self._ytraps_deposited += added_traps * 10
            self.inform_station_finished(bed, round(time.time() - start), added_traps)
            self._station_times.append(round(time.time() - start))

        except TerminatedException:
            pass

        except InventoryNotAccessibleError:
            self.inform_inventory_not_accessible(bed, gacha._name)

        except Exception as e:
            self.inform_unknown_exception(bed, e)

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

    def inform_unknown_exception(self, bed: Bed, exception: Exception) -> None:
        """Posts an image of the current screenshot alongside current
        bed and the exception to discord for debugging purposes.

        Parameters:
        ------------
        bed :class:`Bed`:
            The bed (station) the exception occured at

        exception: :class:`Exception`:
            The description of the occured exception
        """
        formatted_text = (
            f"Ran into an unhandled exception at task `{bed.name}`!\n" f"{exception}"
        )
        Thread(
            target=self.send_to_discord,
            name="Posting to discord",
            args=(
                self.info_webhook,
                formatted_text,
                self.grab_screen((0, 0, 1920, 1080), "temp/unknown_error.png"),
                "Ling Ling",
                self.discord_avatar,
            ),
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
        """Checks if more time than set passed since we last emptied the crystal collection"""
        return (time.time() - self.last_emptied) > self.tower_settings.crystal_interval

    def do_next_task(self) -> None:
        """Gacha bot main call method, runs the next task in line. First checks
        if the player needs to go into the tek pod, but it is not actually considered
        a task. A task will either be gacha seeding or crystal collection.
        """
        # check if we need to go heal
        if healed := self.player.needs_recovery():
            self.go_heal()

        self._at_pod = healed

        # check if its time to pick crystals
        if self.crystals_need_pickup() and self._ytraps_deposited > 2000:
            for bed in self.crystal_beds:
                self.do_crystal_station(bed)
            self.last_emptied = time.time()
            return

        # do regular gacha seeding task
        self.do_gacha_station(self.seed_beds[self.current_bed])

        # increment bed counter, make sure its not out of range!
        if self.current_bed < self.tower_settings.seed_beds - 1:
            self.current_bed += 1
            return

        # reset bed counter, increment laps
        print("Completed a lap!")
        self.current_bed = 0
        self._laps_completed += 1
        self._current_lap += 1

        self.inform_lap_finished()
        self.lap_started = time.time()

    def go_heal(self) -> None:
        """Goes to heal by travelling to the tek pod, trying to enter it up to
        3 times. If it can not enter the tek pod, a `TekPodNotAccessible` Error
        is raised.
        """
        start = time.time()

        # travel to the pod
        self.beds.travel_to(self.tek_pod)
        self.tribelogs.check_tribelogs()
        self.player.await_spawned()

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
        raise TekPodNotAccessibleError
