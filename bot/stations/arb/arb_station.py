import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Literal, Optional

import pyautogui  # type: ignore[import]
from discord import Embed  # type: ignore[import]

from ark.beds import Bed, BedMap
from ark.entities.dinosaurs import Dinosaur
from ark.entities.player import Player
from ark.exceptions import InvalidStatusError
from ark.items import (
    ARB,
    CHARCOAL,
    FLINT,
    FUNGAL_WOOD,
    GASOLINE,
    GUNPOWDER,
    METAL_INGOT,
    SPARKPOWDER,
    STONE,
    Item,
)
from ark.structures.chemistry_bench import ChemistryBench
from ark.structures.dedi_storage import TekDedicatedStorage
from ark.structures.industrial_forge import IndustrialForge
from ark.tribelog import TribeLog
from bot.stations.arb.status import Status
from bot.stations.grinding.grinding_station import EXOMEK_AVATAR
from bot.stations.station import Station, StationData, StationStatistics

FORGE_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/c/c5/Industrial_Forge.png/revision/latest/scale-to-width-down/228?cb=20151126023709"
CHEMBENCH_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/9/9d/Chemistry_Bench.png/revision/latest/scale-to-width-down/228?cb=20160428045516"
ARB_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/6/64/Advanced_Rifle_Bullet.png/revision/latest/scale-to-width-down/228?cb=20150615121742"


@dataclass
class ArbStatistics:
    """Represents the stations statistics as dataclass.
    Follows the `StationStatistics` protocol.
    """

    time_taken: int
    refill_lap: bool
    profit: dict[Item, int]


class ARBStation(Station):
    """Represents a plant Y-Trap station. Follows the `Station` protocol.

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
        self.station_data = station_data
        self.player = player
        self.tribelog = tribelog
        self.current_bed: int = 0

        self._wood_in_dedi: int = 0
        self._first_cooking: bool = True

        self.status = Status.WAITING_FOR_WOOD
        self.ready: property = False
        self.dedi = TekDedicatedStorage()
        self.exo_mek = Dinosaur("Exo Mek", "exo_mek")
        self.forge = IndustrialForge()
        self.forge_bed = Bed("arb_cooking", self.station_data.beds[0].coords)
        self.pickup_bed = Bed("arb_pickup", self.station_data.beds[0].coords)
        self.chembench = ChemistryBench()

    @property
    def ready(self) -> bool:
        return self._ready

    @ready.setter
    def ready(self, state: bool) -> None:
        self._ready = state

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, status: Status) -> None:
        self._status = status

    def spawn(self) -> None:
        bed_map = BedMap()
        bed_map.travel_to(self.station_data.beds[0])
        self.tribelog.check_tribelogs()
        self.player.await_spawned()
        self.player.sleep(10)

    def add_wood(self, wood: int) -> None:
        """Called when wood is added to the dedi via the stryder on the
        crystal station. Once more than 29700 wood has been added the
        station is ready to refill the forges."""
        self._wood_in_dedi += wood
        if self._wood_in_dedi >= 29700:
            self.ready = True

    def is_ready(self) -> bool:
        """Checks if the station is ready for the next step."""
        if self.status == Status.WAITING_FOR_WOOD:
            # set ready by 'add_wood' method, called from crystal station
            # when wood gets teleported
            return self.ready

        if self.status == Status.COOKING_WOOD:
            # currently cooking the wood, checks if 2.75 hours have passed.
            return self.charcoal_ready()

        if self.status == Status.WAITING_FOR_GUNPOWDER:
            # currently waiting for the gunpoweder to be crafted
            # so it can queue the ARB
            return self.gunpowder_ready()

        if self.status == Status.WAITING_FOR_ARB:
            # waiting for the ARB to finish crafting (approx 5k crafts)
            return self.arb_ready()

        raise InvalidStatusError(f"{self.status} is not a valid status!")

    def complete(self) -> tuple[Embed, StationStatistics]:
        """Completes the stations next step corresponding to its status."""
        if self.status == Status.WAITING_FOR_WOOD:
            return self.fill_forges_craft_spark()

        if self.status == Status.COOKING_WOOD:
            return self.craft_gunpowder()

        if self.status == Status.WAITING_FOR_GUNPOWDER:
            return self.craft_arb()

        if self.status == Status.WAITING_FOR_ARB:
            return self.pick_up_arb()

        raise InvalidStatusError(f"{self.status} is not a valid status!")

    def create_embed(self, statistics: StationStatistics) -> Embed:
        """Creates the final embed after all steps have been finished, displays
        the ARB made and the time taken."""
        embed = Embed(
            type="rich",
            title=f"Filled forges and crafted sparkpowder!",
            color=0xFF5500,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{statistics.time_taken} seconds")
        embed.add_field(name="ARB crafted:", value=f"{statistics.profit[ARB]}")

        embed.set_thumbnail(url=ARB_AVATAR)
        embed.set_footer(text="Ling Ling on top!")
        return embed

    def create_arb_queued_embed(self, statistics: ArbStatistics) -> Embed:
        """Returns an embed displaying that ARB has been queued and how
        long it took."""
        embed = Embed(
            type="rich",
            title=f"Queued Advanced Rifle Bullets at {self.station_data.beds[0].name}!",
            color=0xE4CEB8,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{statistics.time_taken} seconds")
        embed.set_thumbnail(url=EXOMEK_AVATAR)
        embed.set_footer(text="Ling Ling on top!")
        return embed

    def create_gunpowder_crafted_embed(self, statistics: ArbStatistics) -> Embed:
        """Creates an embed that gunpowder has been queued, how long it took and
        roughly how much is being crafted."""
        embed = Embed(
            type="rich",
            title=f"Queued gunpowder at {self.station_data.beds[0].name}!",
            color=0xFF5500,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{statistics.time_taken} seconds")
        embed.add_field(
            name="Gunpowder queued:", value=f"{statistics.profit[GUNPOWDER]}"
        )

        embed.set_thumbnail(url=CHEMBENCH_AVATAR)
        embed.set_footer(text="Ling Ling on top!")
        return embed

    def create_forges_refilled_embed(self, statistics: ArbStatistics) -> Embed:
        """Creates an embed displaying that the forge has been refilled and
        how long it took. Also displays if the forges were emptied."""

        embed = Embed(
            type="rich",
            title=f"Filled forges and crafted sparkpowder!",
            color=0xFF5500,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{statistics.time_taken} seconds")
        embed.add_field(name="Forges emptied:", value=f"{not self._first_cooking}")

        embed.set_thumbnail(url=FORGE_AVATAR)
        embed.set_footer(text="Ling Ling on top!")
        return embed

    def gunpowder_ready(self) -> bool:
        """Checks if 5 minutes have passed since queuing gunpowder"""
        time_diff = datetime.now() - self._started_crafting_gunpowder
        print((5 * 60) - time_diff.total_seconds(), "seconds left on gunpowder...")
        return time_diff.total_seconds() > (5 * 60)

    def arb_ready(self) -> bool:
        """Checks if 15 minutes have passed since queuing arb"""
        time_diff = datetime.now() - self._started_crafting_arb
        print((15 * 60) - time_diff.total_seconds(), "seconds left on arb...")
        return time_diff.total_seconds() > (15 * 60)

    def charcoal_ready(self) -> bool:
        """Checks if 2h 45min have passed since filling the forges"""
        time_diff = datetime.now() - self._started_cooking_wood
        print((170 * 60) - time_diff.total_seconds(), "seconds left on wood cooking...")
        return time_diff.total_seconds() > (170 * 60)

    def go_over_chembenches(self) -> list[tuple[Callable, int]]:
        """Returns a list of actions to go over the chembenches"""
        return [
            (self.player.turn_x_by, -80),
            (self.player.turn_y_by, -70),
            (self.player.turn_x_by, -50),
            (self.player.turn_y_by, 70),
            (self.player.turn_x_by, -50),
            (self.player.turn_y_by, -70),
        ]

    def go_over_bottom_chembenches(self) -> list[tuple[Callable, int]]:
        """Returns a list of actions to go over the bottom chembenches"""
        return [
            (self.player.turn_x_by, -80),
            (self.player.turn_x_by, -50),
            (self.player.turn_x_by, -50),
        ]

    def spawn_at_forges(self) -> None:
        """Spawns at the forge bed"""
        bed_map = BedMap()
        bed_map.travel_to(self.forge_bed)
        self.tribelog.check_tribelogs()
        self.player.await_spawned()
        self.player.sleep(1)

    def take_gas_from_forge_dedi(self) -> None:
        """Takes the gas from its dedi at the forge bed"""
        self.player.turn_y_by(40)
        self.player.sleep(0.5)

        self.dedi.inventory.open()
        self.dedi.inventory.withdraw_stacks(1)
        self.dedi.inventory.close()
        self.player.sleep(0.5)
        self.player.turn_y_by(-40)

    def take_fungal_wood(self) -> None:
        """Takes the fungal wood from the dedi above."""
        self.player.look_up_hard()
        self.dedi.inventory.open()
        self.dedi.inventory.click_transfer_all()
        self.dedi.inventory.close()

        self.player.sleep(0.3)
        self.player.turn_y_by(160)
        self.player.sleep(0.3)
        self.player.turn_y_by(20)

    def transfer_gasoline(self, amount: int) -> None:
        """Transfers the given amount of gasoline, useful for
        precise amounts such as 11 per forge, or 1 per gunpowder craft
        """
        self.player.inventory.search_for(GASOLINE)
        self.player.inventory.select_first_slot()
        self.player.sleep(1)

        for _ in range(amount):
            pyautogui.click(clicks=2)
        self.player.inventory.delete_search()

    def forges_put_gas_back(self) -> None:
        """Puts the gas back into its dedi at the cooking bed"""
        self.dedi.attempt_deposit(GASOLINE, False)
        self.player.look_up_hard()
        self.player.sleep(1)
        self.dedi.attempt_deposit(FUNGAL_WOOD, False)

    def empty_forges(self) -> None:
        """Empties the forges, empties each forge and puts the charcoal into the dedi."""
        self.spawn_at_forges()
        right_turns: int = 0
        known_empty: set[int] = set()

        while right_turns < 4:
            # turn to the forge
            self.player.turn_90_degrees("right", delay=1)
            right_turns += 1
            if right_turns in known_empty:
                continue

            self.forge.inventory.open()
            if not self.forge.inventory.has_item(CHARCOAL):
                known_empty.add(right_turns)
                # forge does not have charcoal so go next
                self.forge.inventory.close()
                continue

            # forge has charcoal, take all charcoal and turn back to dedi
            self.forge.inventory.take_all_items(CHARCOAL)
            self.forge.inventory.close()

            for _ in range(right_turns):
                self.player.turn_90_degrees("left", delay=1)
            right_turns = 0

            self.player.sleep(1)
            # deposit charcoal
            self.dedi.attempt_deposit(CHARCOAL, False)

    def fill_forges_craft_spark(self) -> tuple[Embed, ArbStatistics]:
        """Spawns at the forge bed and fills them with wood.
        Deposits 11 gasoline into each forge, and caps it with wood.

        Finishes with the remaining gasoline and wood deposited back into their
        dedis. Sets the most recent wood cooking timestamp upon finishing.
        """
        start = time.time()
        try:
            # first cooking we empty the forges in case any charcoal
            # was left from prior runs
            if self._first_cooking:
                self.empty_forges()

            self.spawn_at_forges()
            self.take_gas_from_forge_dedi()
            self.take_fungal_wood()

            # fill each forge
            for _ in range(3):
                self.player.turn_90_degrees("right", delay=1)
                self.forge.inventory.open()
                self.transfer_gasoline(9)
                self.player.inventory.transfer_all(self.forge.inventory, FUNGAL_WOOD)
                self.forge.turn_on()
                self.forge.inventory.close()

            # put the gas and wood back
            self.player.turn_90_degrees("right")
            self.player.turn_y_by(40)
            self.forges_put_gas_back()

            # queue sparkpowder
            self.craft_sparkpowder()
            stats = ArbStatistics(round(time.time() - start), False, {})
            return self.create_forges_refilled_embed(stats), stats

        finally:
            self._started_cooking_wood: datetime = datetime.now()
            self._first_cooking = False
            self._wood_in_dedi = 0
            self.ready = False

    def access_gasoline(self, mode: Literal["take", "deposit"]) -> None:
        """Turns to the gasoline dedi from the original spawn position,
        can either take gas or deposit it. Finishes in the original spawn
        position."""
        self.player.turn_x_by(-30)
        self.player.turn_y_by(40)
        self.player.sleep(1)

        if mode == "take":
            self.dedi.inventory.open()
            self.dedi.inventory.withdraw_stacks(1)
            self.dedi.inventory.close()
        else:
            self.dedi.attempt_deposit(METAL_INGOT, False)

        self.player.sleep(0.5)
        self.player.turn_y_by(-40)
        self.player.turn_x_by(30)

    def access_stone(self, mode: Literal["take", "deposit"]) -> None:
        """Turns to the stone dedi from the original spawn position,
        can either take stone or deposit it. Finishes in the original spawn
        position."""
        self.player.turn_x_by(30)
        self.player.sleep(1)

        if mode == "take":
            self.dedi.inventory.open()
            self.dedi.inventory.click_transfer_all()
            self.dedi.inventory.close()
        else:
            self.dedi.attempt_deposit(METAL_INGOT, False)

        self.player.sleep(0.5)
        self.player.turn_x_by(-30)

    def access_flint(self, mode: Literal["take", "deposit"]) -> None:
        """Turns to the flint dedi from the original spawn position,
        can either take flint or deposit it. Finishes in the original spawn
        position."""
        self.player.turn_x_by(30)
        self.player.turn_y_by(40)
        self.player.sleep(1)

        if mode == "take":
            self.dedi.inventory.open()
            self.dedi.inventory.click_transfer_all()
            self.dedi.inventory.close()
        else:
            self.dedi.attempt_deposit(METAL_INGOT, False)

        self.player.sleep(0.5)
        self.player.turn_y_by(-40)
        self.player.turn_x_by(-30)

    def access_metal(self, mode: Literal["take", "deposit"]) -> None:
        """Turns to the metal dedi from the original spawn position,
        can either take metal or deposit it. Finishes in the original spawn
        position."""
        self.player.turn_x_by(110)
        self.player.sleep(1)

        if mode == "take":
            self.dedi.inventory.open()
            self.dedi.inventory.click_transfer_all()
            self.dedi.inventory.close()
        else:
            self.dedi.attempt_deposit(METAL_INGOT, False)

        self.player.sleep(0.5)
        self.player.turn_x_by(-110)

    def take_metal_queue_arb(self) -> None:
        """Takes metal and puts it into the exo mek, queues the ARB and
        return the metal to its dedi. Finishes in the original spawn
        position."""
        # take metal and turn to exo mek
        self.access_metal("take")
        for _ in range(2):
            self.player.turn_90_degrees()
        self.player.sleep(1)

        # open the exo mek, search for ARB
        self.exo_mek.inventory.open()
        self.player.inventory.transfer_amount(METAL_INGOT, 5400, self.exo_mek.inventory)
        self.exo_mek.inventory.open_craft()
        self.exo_mek.inventory.search_for("advanced rifle")

        # craft 1k on each bp
        for slot in [(1292 + (i * 95), 296) for i in range(5)]:
            self.player.click_at(slot)
            for _ in range(10):
                self.player.press("a")
                self.player.sleep(0.2)

        # close the exo mek
        self.exo_mek.inventory.close_craft()
        self.exo_mek.inventory.close()
        self.player.sleep(0.5)

        # turn back to original position, put metal back
        for _ in range(2):
            self.player.turn_90_degrees("left")
        self.player.sleep(1)
        self.access_metal("deposit")

    def fill_bottom_chembenches(
        self, gas: bool, material: Item, amount: int, craft: Optional[Item] = None
    ) -> None:
        """Fills the bottom chem benches to the given amount with the given material.
        Fills it with 1 gas if passed, and crafts the given item

        Parameters:
        -----------
        gas :class:`bool`:
            Whether to put 1 gas into the chembench

        material :class:`Item`:
            The item to put into the chembench

        amount :class:`int`:
            The amount of the item to put into the chembench

        craft :class: [Optional]:
            The item to craft
        """
        for func, arg in self.go_over_bottom_chembenches():
            func(arg)
            self.player.sleep(0.3)

            # open the chembench, go through the actions
            self.chembench.inventory.open()
            if gas:
                while not self.chembench.can_turn_on():
                    self.transfer_gasoline(1)
                    self.player.sleep(1)

            if amount < 4000:
                self.player.inventory.transfer_amount(
                    material, amount, self.chembench.inventory
                )
            else:
                self.player.inventory.transfer_all(self.chembench.inventory)

            # craft the given item
            if craft is not None:
                self.chembench.turn_on()
                self.chembench.inventory.open_craft()
                self.chembench.inventory.craft(craft, 900)
                self.chembench.inventory.close_craft()

            self.chembench.inventory.close()
            self.player.sleep(0.3)

        # reverse the turns to get back to the original position
        for func, arg in reversed(self.go_over_bottom_chembenches()):
            func(arg * -1)
            self.player.sleep(0.3)

    def craft_sparkpowder(self) -> None:
        """Spawns at the station and starts crafting sparkpowder"""
        self.spawn()
        self.access_gasoline("take")
        self.access_stone("take")
        self.fill_bottom_chembenches(gas=True, material=STONE, amount=3300)
        self.access_stone("deposit")
        self.access_gasoline("deposit")

        self.access_flint("take")
        self.fill_bottom_chembenches(
            gas=False, material=FLINT, amount=7700, craft=SPARKPOWDER
        )
        self.access_flint("deposit")
        self.status = Status.COOKING_WOOD

    def take_spark_out(self) -> None:
        """Scrolls down far enough to have a view on slot 51, so that we can determine
        we there is 50 slots left once slot 51 is free."""
        self.chembench.inventory.select_first_slot()
        pyautogui.scroll(-700)
        self.player.sleep(1)

        i = 0
        while self.chembench.inventory.locate_template(
            SPARKPOWDER.inventory_icon, region=(1420, 783, 110, 110), confidence=0.8
        ):
            self.chembench.inventory.select_first_slot()
            pyautogui.press("t")
            i += 1
            self.player.sleep(i / 200)

    def distribute_spark_evenly(self) -> None:
        """Distributes spark evenly over the chembenches, by taking out until 50 slots
        on the bottom chembench and putting the taken spark into the upper chem bench."""
        for func, arg in self.go_over_bottom_chembenches():
            func(arg)
            self.player.sleep(0.3)

            # take until 50 slots from the bottom one
            self.chembench.inventory.open()
            self.take_spark_out()
            self.chembench.inventory.close()
            self.player.sleep(0.3)

            # turn to top one, put all taken spark into the upper one.
            self.player.turn_y_by(-70)
            self.player.sleep(0.3)
            self.chembench.inventory.open()
            self.player.inventory.transfer_all(self.chembench.inventory, SPARKPOWDER)
            self.chembench.inventory.close()
            self.player.sleep(0.3)
            self.player.turn_y_by(70)

        # reverse the turns to get back to original position
        for func, arg in reversed(self.go_over_bottom_chembenches()):
            func(arg * -1)
            self.player.sleep(0.3)

    def queue_gunpowder(self, transfer_mats: bool) -> None:
        """Queues gunpowder in every chembench, if transfer_mats is toggled
        it first takes gasoline and puts one gasoline into each chembench."""
        # get the gasoline if we need it
        if transfer_mats:
            self.access_gasoline("take")
            self.player.sleep(1)

            self.dedi.inventory.open()
            self.dedi.inventory.click_transfer_all()
            self.dedi.inventory.close()

        for func, arg in self.go_over_chembenches():
            func(arg)
            self.player.sleep(0.3)

            self.chembench.inventory.open()
            # transfer the materials
            if transfer_mats:
                while not self.chembench.can_turn_on():
                    self.transfer_gasoline(1)
                    self.player.sleep(1)
                self.chembench.turn_on()
                self.player.inventory.transfer_all(self.chembench.inventory, CHARCOAL)

            # queu gunpowder
            self.chembench.inventory.open_craft()
            self.chembench.inventory.craft(GUNPOWDER, 1000)
            self.chembench.inventory.close_craft()
            self.chembench.inventory.close()
            self.player.sleep(0.5)

        # reverse turns to get back to original position
        for func, arg in reversed(self.go_over_chembenches()):
            func(arg * -1)
            self.player.sleep(0.3)

        # put away the remaining charcoal
        if transfer_mats:
            self.dedi.attempt_deposit(CHARCOAL, False)
            self.access_gasoline("deposit")

    def craft_gunpowder(self) -> tuple[Embed, ArbStatistics]:
        """Empties the forges, then spawns at the crafting bed, distributes
        sparkpowder evenly and queues gunpowder after. Returns an embed
        displaying the statistics, and the statistics object itself.
        """
        self.empty_forges()
        self.spawn()
        start = time.time()
        try:
            self.distribute_spark_evenly()
            for i in range(2):
                self.queue_gunpowder(transfer_mats=not i)

            stats = ArbStatistics(
                round(time.time() - start), False, {GUNPOWDER: 7500 * 6}
            )
            return self.create_gunpowder_crafted_embed(stats), stats

        finally:
            self.status = Status.WAITING_FOR_GUNPOWDER
            self._started_crafting_gunpowder: datetime = datetime.now()

    def empty_chembenches(self) -> None:
        """Empties the chembenches, because the player can only hold the
        gunpowder of 2 chembenches at once, we we empty a slice of 2. After
        each 2 forges have been emptied we put the gunpowder into the exo
        mek to later craft into ARB."""

        for i in range(2, 8, 2):
            # slice out the turns of the chembenches we need to access
            for index, (func, arg) in enumerate(self.go_over_chembenches()[0:i]):
                func(arg)
                self.player.sleep(0.3)

                # check if we already emptied the prior chembenches
                if index >= i - 2:
                    self.chembench.inventory.open()
                    self.chembench.inventory.click_transfer_all()
                    self.chembench.inventory.close()
                    self.player.sleep(0.3)

            # reverse the turns to return back, once again sliced
            for func, arg in reversed(self.go_over_chembenches()[0:i]):
                func(arg * -1)
                self.player.sleep(0.3)

            # turn to the exo mek to put the gunpowder in
            for _ in range(2):
                self.player.turn_90_degrees("right")
            self.player.sleep(1)
            self.exo_mek.inventory.open()
            self.player.inventory.transfer_all(self.exo_mek.inventory, GUNPOWDER)
            self.exo_mek.inventory.close()
            self.player.sleep(0.5)

            # return to the start
            for _ in range(2):
                self.player.turn_90_degrees("left")

        # drop all the items aside from charcoal (stone, flint, spark leftovers...)
        self.player.empty_inventory()

    def craft_arb(self) -> tuple[Embed, ArbStatistics]:
        """Spawns at the crafting bed, empties the chembenches to put the
        gunpowder into the exomek, then crafts ARB inside the exo mek.
        
        Returns an embed displaying the time taken and the statistics.
        
        Upon finishing, the the status property is set to `WAITING_FOR_ARB`,
        and the `_started_crafting_arb` datetime is created to check when its
        finished.
        """
        self.spawn()
        start = time.time()
        try:
            self.empty_chembenches()
            self.take_metal_queue_arb()

            stats = ArbStatistics(round(time.time() - start), False, {})
            return self.create_arb_queued_embed(stats), stats

        finally:
            self.status = Status.WAITING_FOR_ARB
            self._started_crafting_arb: datetime = datetime.now()

    def travel_to_pickup_bed(self) -> None:
        """Travels to the arb pick up bed"""
        bedmap = BedMap()
        bedmap.travel_to(self.pickup_bed)
        self.tribelog.check_tribelogs()
        self.player.await_spawned()
        self.player.sleep(1)

    def pick_up_arb(self) -> tuple[Embed, ArbStatistics]:
        """Picks up the ARB from the exo mek and puts it into the dedis.
        Returns an embed displaying the time taken and how much ARB
        was crafted.

        This should be the last step of the station and once finished, the
        status property will be set back to `WAITING_FOR_WOOD`, so that it
        once again needs to be set `ready` by the collection point.
        """
        self.travel_to_pickup_bed()
        start = time.time()
        profit: dict[Item, int] = {ARB: 0}

        try:
            self.exo_mek.inventory.open()
            self.exo_mek.inventory.take_all_items(ARB)
            self.exo_mek.inventory.close()
            self.player.sleep(5)

            for i, turn in enumerate([80, 60, 80, -60]):
                if i % 2 == 0:
                    self.player.turn_x_by(turn)
                else:
                    self.player.turn_y_by(turn)

                amount = self.dedi.attempt_deposit(ARB, determine_amount=True)
                if amount:
                    profit[ARB] += amount[1]

            stats = ArbStatistics(round(time.time() - start), False, profit)
            return self.create_embed(stats), stats

        finally:
            self.status = Status.WAITING_FOR_WOOD
