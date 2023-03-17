from __future__ import annotations

import json
import time
from datetime import datetime, timedelta

from ark import (Bed, ChemistryBench, Dinosaur, Gacha, Player, Structure,
                 TekCropPlot, TekDedicatedStorage, items)
from discord import Embed  # type: ignore[import]

from ...exceptions import MissingPelletsError, StationNotReadyError
from ...webhooks import InfoWebhook, TribeLogWebhook
from .._crop_plot_helper import do_crop_plot_stack
from .._station import Station
from ._settings import MedbrewStationSettings
from ._status import Status


class MedbrewStation(Station):
    """Ling Lings Medbrew Station component.

    Crafts medbrews from berries and spoiled meat plants.
    """

    MEDBREW_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/5/59/Medical_Brew.png/revision/latest/scale-to-width-down/228?cb=20150615103740"
    NARCOTIC_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/5/59/Medical_Brew.png/revision/latest/scale-to-width-down/228?cb=20150615103740"
    COOKER_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/9/91/Industrial_Cooker.png/revision/latest/scale-to-width-down/228?cb=20151202043005"

    def __init__(
        self,
        name: str,
        player: Player,
        tribelog: TribeLogWebhook,
        info_webhook: InfoWebhook,
        settings: MedbrewStationSettings,
    ) -> None:
        self._name = name
        self._player = player
        self._tribelog = tribelog
        self._webhook = info_webhook
        self.forges_emptied = False
        self.settings = settings

        self.turn_factor = -1 if not self.benches_are_right else 1
        self.status = Status.WAITING_FOR_BERRIES

        self._load_last_completion("medbrew")
        self._create_turns()
        self.narc_crop_plots = [
            TekCropPlot(f"{name} - Narcoberry 1:{i}") for i in range(1, 10)
        ]
        self.tinto_crop_plots = [
            [TekCropPlot(f"{name} - Tintoberry {stack}:{i} ") for i in range(1, 10)]
            for stack in range(1, 4)
        ]

        self.dedi = TekDedicatedStorage()
        self.chembench = ChemistryBench()
        self.cooker = Structure(
            f"Cooker {name}", "assets/templates/cooker.png", toggleable=True
        )
        self.gacha = Gacha(name)
        self.bear = Dinosaur("Dire Bear", "assets/templates/dire_bear.png")
        self.trough = Structure("Tek Trough", "assets/templates/tek_trough.png")

        self.chembench_bed = Bed(name + "cb")

        self.pellet_2_bed = Bed(name + "p2")
        self.pellet_1_bed = Bed(name + "p1")

        self.narcoberry_bed = Bed(name + "c1")
        self.spoiled_meat_bed = Bed(name + "c2")
        self.tintoberry_bed = Bed(name + "c3")

    @property
    def benches_are_right(self) -> bool:
        """Returns whether the stations benches are to the righthand side when
        spawning, given the stations numeric suffix."""
        return int(self._name[-2:]) % 2 == 0

    def is_ready(self) -> bool:
        if self.status == Status.WAITING_FOR_BERRIES:
            return self._berries_are_ready()

        elif self.status == Status.CRAFTING_NARCOTICS:
            return self._narcotics_finished_crafting()

        elif self.status == Status.COOKING_MEDBREWS:
            return self._brews_finished_cooking()

        raise ValueError(f"'{self.status}' is not a valid status!")

    def complete(self) -> None:
        if self.status == Status.WAITING_FOR_BERRIES:
            self.craft_narcotics()

        elif self.status == Status.CRAFTING_NARCOTICS:
            self.cook_brews()

        elif self.status == Status.COOKING_MEDBREWS:
            self.pickup_brews()

        else:
            raise ValueError(f"'{self.status}' is not a valid status!")

    @staticmethod
    def build_stations(
        player: Player,
        tribelog: TribeLogWebhook,
        info_webhook: InfoWebhook,
    ) -> list[MedbrewStation]:
        settings = MedbrewStationSettings.load()
        return [
            MedbrewStation(
                f"{settings.prefix}{i:02d}",
                player,
                tribelog,
                info_webhook,
                settings,
            )
            for i in range(settings.beds)
        ]

    def craft_narcotics(self) -> None:
        """Gets the narcoberries and spoiled meat, then queues narcotics."""
        start = time.time()

        self._get_narcoberries()
        self._distribute_narcoberries()

        self._harvest_spoiled_meat()
        self._get_meat_from_bear()

        self._get_gasoline()
        self._queue_narcotics()

        self._put_gas_into_cookers()

        self.status = Status.CRAFTING_NARCOTICS
        self._started_crafting_narcotics = datetime.now()
        self._webhook.send_embed(
            self._create_narcotics_queued_embed(round(time.time() - start))
        )

    def cook_brews(self) -> None:
        """Starts cooking the medbrews by putting the crafted narcotics into
        the cookers, then putting the tintoberries in."""
        start = time.time()

        self._put_narcotics_in_cookers()
        self._spawn_at(self.tintoberry_bed)

        if self.refill:
            self._player.look_down_hard()
            self._player.turn_y_by(-40)
            bag = Structure("Item Cache", "assets/wheels/item_cache.png")
            bag.open()
            bag.inventory.transfer_all()
            bag.close()

        for idx, stack in enumerate(self.tinto_crop_plots):
            self._player.turn_90_degrees("right", delay=1)
            self._player.crouch()
            do_crop_plot_stack(
                self._player,
                stack,
                items.TINTOBERRY,
                [-130, *[-17] * 5, 30, -17, -17],
                [],
                refill=self.refill,
                precise=True,
            )
            self._player.sleep(2)
            self._player.stand_up()
            if idx == 2:
                continue

            self._player.look_down_hard()
            self._player.turn_y_by(-160)

            for _ in range(3 - idx):
                self._player.turn_90_degrees("right", delay=1)

            if not idx:
                self._player.turn_x_by(-40 * self.turn_factor)
            else:
                self._player.turn_x_by(-40 * self.turn_factor)
                self._player.turn_x_by(80 * self.turn_factor)

            self._fill_up_cooker()
            if not idx:
                self._player.turn_x_by(40 * self.turn_factor)
            else:
                self._player.turn_x_by(40 * self.turn_factor)
                self._player.turn_x_by(-80 * self.turn_factor)

            for _ in range(3 - idx):
                self._player.turn_90_degrees("left", delay=1)

        self._player.look_down_hard()
        self._player.turn_y_by(-160, delay=0.5)
        self._player.turn_90_degrees("right", delay=1)

        for idx, (func, arg) in enumerate(self.cooker_turns_2):
            func(arg, delay=0.5)
            if idx < 2:
                continue
            if idx == 2:
                self._fill_up_cooker()
            else:
                self.cooker.open()
                self._player.inventory.transfer_all()
                self.cooker.turn_on()
                self.cooker.close()

        self.status = Status.COOKING_MEDBREWS
        self._started_cooking_brews = datetime.now()
        self._webhook.send_embed(
            self._create_started_cooking_embed(round(time.time() - start))
        )

    def pickup_brews(self) -> None:
        """Takes the cooked brews out of the cookers and puts them into the
        troughs. Counts how many were crafted."""
        self._spawn_at(self.chembench_bed)
        start = time.time()

        for func, arg in self.meat_bench_turns:
            func(arg, delay=0.5)

        for func, arg in self.cooker_turns:
            func(arg, delay=0.5)
            self.cooker.open()
            self.cooker.inventory.transfer_all(items.MEDBREW)
            self.cooker.close()
            self._player.sleep(2)

        for func, arg in reversed(self.cooker_turns):
            func(arg * -1, delay=0.5)

        for func, arg in reversed(self.meat_bench_turns):
            func(arg * -1, delay=0.5)

        self._player.inventory.open()
        brews_made = self._player.inventory.count(items.MEDBREW) * 100
        img = self._player.window.grab_screen(self._player.inventory._ITEM_REGION)
        self._player.inventory.close()

        self._fill_troughs()
        self._webhook.send_embed(
            self._create_final_embed(round(time.time() - start), brews_made), img=img
        )
        self.statistics["Medical Brews"] = (
            self.statistics.get("Medical Brews", 0) + brews_made
        )

        self.status = Status.WAITING_FOR_BERRIES
        self.last_completed = datetime.now()
        self.set_data("medbrew", "last_completed", self.last_completed)

    def _put_narcotics_in_cookers(self) -> None:
        """Puts the narcotics from the chembenches into the cookers."""
        self._spawn_at(self.chembench_bed)
        for func, arg in self.meat_bench_turns:
            func(arg, delay=0.5)

            self.chembench.open()
            self.chembench.inventory.transfer_all(items.NARCOTIC)
            self.chembench.close()
            self._player.sleep(2)

        for idx, (func, arg) in enumerate(self.cooker_turns):
            func(arg, delay=0.5)

            self.cooker.open()
            if idx == 3:
                self._player.inventory.transfer_all()
            else:
                self.cooker.inventory.transfer_all(items.NARCOTIC)
                self._player.inventory.transfer(
                    items.NARCOTIC, 600, self.chembench.inventory
                )
            self.cooker.close()
            self._player.sleep(2)

    def _fill_up_cooker(self) -> None:
        """Puts exactly 60 slots of tintoberries into the cooker, then turns
        it on."""
        self.cooker.open()
        self._player.inventory.transfer_all(items.TINTOBERRY)

        self.cooker.inventory.search(items.TINTOBERRY)
        for _ in range(2):
            self.cooker.inventory.transfer_top_row()

        self._player.sleep(1)
        self.cooker.inventory.scroll("down", rows=4)
        self._player.sleep(1)

        while self.cooker.window.locate_template(
            items.TINTOBERRY.inventory_icon,
            self.cooker.inventory.SLOTS[36],
            confidence=0.7,
        ):
            self.cooker.inventory.press("t")
            self._player.sleep(0.2)

        self.cooker.turn_on()
        self.cooker.close()

    def _berries_are_ready(self) -> bool:
        """Returns whether 5 hours passed since the last completion"""
        assert self.last_completed is not None
        try:
            return (datetime.now() - self.last_completed).total_seconds() > 5 * 3600
        except AttributeError:
            return True

    def _narcotics_finished_crafting(self) -> bool:
        """Returns whether 3 minutes passed since crafting narcotics"""
        try:
            return (
                datetime.now() - self._started_crafting_narcotics
            ).total_seconds() > 180
        except AttributeError:
            return True

    def _brews_finished_cooking(self) -> bool:
        """Returns whether 18 minutes passed since starting to cook medbrews"""
        try:
            return (datetime.now() - self._started_cooking_brews).total_seconds() > 1020
        except AttributeError:
            return True

    def _queue_narcotics(self) -> None:
        """Queues narcotics in the chembenches"""
        for func, arg in self.meat_bench_turns:
            func(arg, delay=0.5)

            self.chembench.open()
            self._player.inventory.take(items.GASOLINE, amount=1)
            self._player.inventory.transfer(
                items.SPOILED_MEAT, 700, self.chembench.inventory
            )

            self.chembench.turn_on()
            self.chembench.inventory.open_tab("crafting")
            self.chembench.inventory.craft(items.NARCOTIC, 200)
            self.chembench.inventory.open_tab("inventory")
            self.chembench.close()

            self._player.sleep(2)

    def _put_gas_into_cookers(self) -> None:
        """Puts 1 gas into each cooker."""
        for func, arg in self.cooker_turns:
            func(arg, delay=0.5)
            self.cooker.open()
            self._player.inventory.take(items.GASOLINE, amount=1)
            self.cooker.close()
            self._player.sleep(2)

        for func, arg in reversed(self.cooker_turns):
            func(arg * -1, delay=0.5)

        for func, arg in reversed(self.meat_bench_turns):
            func(arg * -1, delay=0.5)

        for turn, val in self.gasoline_turns:
            turn(val, delay=0.5)

        self.dedi.deposit([items.GASOLINE], get_amount=False)

    def _get_meat_from_bear(self) -> None:
        """Takes the spoiled meat from the bear"""
        self._spawn_at(self.chembench_bed)
        self.bear.access()
        self.bear.inventory.transfer_all(items.SPOILED_MEAT)
        self.bear.close()
        self._player.sleep(2)

    def _get_narcoberries(self) -> None:
        """Harvests the narcoberry crop plots"""
        try:
            self._take_narcoberries()
        except StationNotReadyError:
            self.last_completed = datetime.now() - timedelta(minutes=4.5 * 60)
            raise
        except MissingPelletsError:
            self.refill = True
            self._drop_down_pellets()
            self._take_narcoberries(refill=True)
        else:
            self.refill = False
        self._player.stand_up()

    def _distribute_narcoberries(self) -> None:
        """Distributes the narcoberries into the chembenches, putting 2700 each."""
        for idx, (turn, val) in enumerate(self.narco_bench_turns):
            turn(val, delay=1)

            self.chembench.open()
            if idx < 2:
                self._player.inventory.transfer(
                    items.NARCOBERRY, 2700, self.chembench.inventory
                )
            else:
                self._player.inventory.transfer_all(items.NARCOBERRY)
            self.chembench.close()
            self._player.sleep(2)

    def _get_gasoline(self) -> None:
        """Takes 10 gasoline from the dedi."""
        for turn, val in self.gasoline_turns:
            turn(val, delay=0.5)

        self.dedi.open()
        self.dedi.inventory.withdraw(5, presses=2)
        self.dedi.close()
        self._player.sleep(2)

        for turn, val in reversed(self.gasoline_turns):
            turn(val * -1, delay=0.5)

    def _fill_troughs(self) -> None:
        """Puts the medbrews into the troughs"""
        for turn in [-160, None, 50, None]:
            if turn is None:
                self._player.crouch()
            else:
                self._player.turn_x_by(turn * self.turn_factor, delay=1)

            self.trough.open()
            self._player.inventory.transfer_all()
            if not self._player.inventory.has(items.MEDBREW):
                self.trough.close()
                return

            self.trough.close()

            if turn is None:
                self._player.stand_up()

    def _spawn_at(self, bed: Bed) -> None:
        """Spawns at a given bed of the station."""
        self._player.prone()
        self._player.look_down_hard()

        bed.spawn()
        self._tribelog.check_tribelogs()
        self._player.spawn_in()

    def _harvest_spoiled_meat(self) -> None:
        """Harvests the spoiled meat plants."""
        self._spawn_at(self.spoiled_meat_bed)

        self._player.prone()
        self._player.look_down_hard()

        self.bear.mount()
        attacks = 0
        while (not self._player.received_item() or attacks < 4) and attacks < 10:
            self.bear.attack("left")
            self._player.sleep(1)
            attacks += 1

        self.bear.dismount()
        self._player.stand_up()
        self._player.look_down_hard()
        self.spoiled_meat_bed.interface.open()

    def _take_narcoberries(self, refill: bool = False) -> None:
        """Takes narcoberries from the crop plots"""
        self._spawn_at(self.narcoberry_bed)

        if refill:
            self._player.look_down_hard()
            for _ in range(2):
                self._player.turn_90_degrees("right", delay=1)
            bag = Structure("Item Cache", "assets/wheels/item_cache.png")
            bag.open()
            bag.inventory.transfer_all()
            bag.close()
            for _ in range(2):
                self._player.turn_90_degrees("left", delay=1)
        else:
            plot = self.narc_crop_plots[6]
            plot.open()

            if plot.inventory.count(items.PELLET) < 13:
                raise MissingPelletsError

            elif plot.inventory.count(items.NARCOBERRY) < 9:
                raise StationNotReadyError

            plot.close()
            self._player.sleep(2)

        self._player.crouch()

        do_crop_plot_stack(
            self._player,
            self.narc_crop_plots,
            items.NARCOBERRY,
            [-130, *[-17] * 5, 30, -17, -17],
            [],
            refill=refill,
            precise=True,
        )
        self._player.look_down_hard()
        self._player.sleep(1)
        self._player.turn_y_by(-160, delay=1)

    def _drop_down_pellets(self) -> None:
        """Drops the pellets down to the berrystations"""
        self._spawn_at(self.pellet_1_bed)
        self.gacha.access()

        for _ in range(20):
            self.gacha.inventory.transfer_top_row()
            if not self.gacha.inventory.has(items.PELLET):
                break

        self.gacha.close()

        self._spawn_at(self.pellet_2_bed)
        self.gacha.access()
        self.gacha.inventory.transfer_all(items.PELLET)
        self.gacha.close()

    def _create_turns(self) -> None:
        self.gasoline_turns = [
            (self._player.turn_x_by, -160 * self.turn_factor),
            (self._player.turn_y_by, -40),
        ]

        self.meat_bench_turns = [
            (self._player.turn_x_by, 80 * self.turn_factor),
            (self._player.turn_x_by, 50 * self.turn_factor),
            (self._player.turn_x_by, 50 * self.turn_factor),
        ]

        self.narco_bench_turns = [
            (self._player.turn_x_by, -65 * self.turn_factor),
            (self._player.turn_x_by, -50 * self.turn_factor),
            (self._player.turn_x_by, -60 * self.turn_factor),
        ]

        self.cooker_turns = [
            (self._player.turn_x_by, 60 * self.turn_factor),
            (self._player.turn_x_by, 60 * self.turn_factor),
            (self._player.turn_y_by, -90),
            (self._player.turn_x_by, -60 * self.turn_factor),
        ]

        self.cooker_turns_2 = [
            (self._player.turn_x_by, 40 * self.turn_factor),
            (self._player.turn_x_by, -80 * self.turn_factor),
            (self._player.turn_y_by, -100),
            (self._player.turn_x_by, 60 * self.turn_factor),
        ]

    def _load_last_completion(self, key: str) -> None:
        with open("bot/_data/station_data.json") as f:
            data: dict = json.load(f)[key]

        if not data["last_completed"]:
            self.last_completed = datetime.now() - timedelta(hours=5)
            self.set_data(key, "last_completed", self.last_completed)
            return

        self.last_completed = datetime.strptime(
            data["last_completed"][:-3], "%Y-%m-%d %H:%M:%S.%f"
        )

    def set_data(self, key: str, key2: str, value) -> None:
        with open("bot/_data/station_data.json") as f:
            data: dict = json.load(f)

        data[key][key2] = value

        with open("bot/_data/station_data.json", "w") as f:
            json.dump(data, f, indent=4, default=str)

    def _create_final_embed(self, time_taken: int, brews_made: int) -> Embed:
        embed = Embed(
            type="rich",
            title=f"Finished medbrew station '{self.name}'!",
            description="The cooked medical brews have been picked up!",
            color=0x5A2825,
        )

        embed.add_field(name="Time taken:", value=f"{time_taken} seconds")
        embed.add_field(name="Brews crafted:", value=brews_made)

        embed.set_thumbnail(url=self.MEDBREW_AVATAR)
        return embed

    def _create_narcotics_queued_embed(self, time_taken: int) -> Embed:
        embed = Embed(
            type="rich",
            title=f"Queued narcotics at medbrew station '{self.name}'!",
            description="The narcotics have been queued and will be ready in 5 minutes!",
            color=0x5A2825,
        )

        embed.add_field(name="Time taken:", value=f"{time_taken} seconds")
        embed.set_thumbnail(url=self.NARCOTIC_AVATAR)
        return embed

    def _create_started_cooking_embed(self, time_taken: int) -> Embed:
        embed = Embed(
            type="rich",
            title=f"Started cooking the medical brews at '{self.name}'!",
            description="The medical brews will be picked up in 18 minutes!",
            color=0x5A2825,
        )

        embed.add_field(name="Time taken:", value=f"{time_taken} seconds")
        embed.set_thumbnail(url=self.COOKER_AVATAR)
        return embed
