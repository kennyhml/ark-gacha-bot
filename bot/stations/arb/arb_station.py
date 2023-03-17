import json
import time
from datetime import datetime
from typing import Any, Literal, Optional

import pyautogui  # type: ignore[import]
from ark import (Bed, ChemistryBench, Dinosaur, IndustrialForge, Player,
                 TekDedicatedStorage, items)
from discord import Embed  # type: ignore[import]

from ...tools import format_seconds
from ...webhooks import InfoWebhook, TribeLogWebhook
from .._station import Station
from ._settings import ArbStationSettings
from ._status import Status

FORGE_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/c/c5/Industrial_Forge.png/revision/latest/scale-to-width-down/228?cb=20151126023709"
CHEMBENCH_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/9/9d/Chemistry_Bench.png/revision/latest/scale-to-width-down/228?cb=20160428045516"
ARB_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/6/64/Advanced_Rifle_Bullet.png/revision/latest/scale-to-width-down/228?cb=20150615121742"
EXOMEK_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/6/6d/Unassembled_Exo-Mek_%28Genesis_Part_2%29.png/revision/latest/scale-to-width-down/228?cb=20210603184626"


class ARBStation(Station):
    """Represents the ARB Station, follows the `Station` abstract base class.
    Is set ready whenever the wood at the forges hits near 30000, then (just like
    the grinding station) it uses a `Status` enum to determine the next steps
    until fully done, at which points it waits to get set ready again.

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
        self,
        player: Player,
        tribelog: TribeLogWebhook,
        info_webhook: InfoWebhook,
    ) -> None:
        self._name = "ARB Station"
        self._player = player
        self._tribelog = tribelog
        self._webhook = info_webhook
        self.forges_emptied = False

        with open("bot/_data/station_data.json") as f:
            data: dict = json.load(f)["arb"]

        self._wood_in_dedi: int = data["wood"]
        print(f"Loaded ARB wood: {self._wood_in_dedi}")

        self.status = data["status"]
        print(f"Loaded ARB status: {self.status}")

        if self.status == Status.COOKING_WOOD:
            self._started_cooking_wood = datetime.strptime(
                data["cooking_start"][:-3], "%Y-%m-%d %H:%M:%S.%f"
            )
            print(f"Loaded start of cooking: {self._started_cooking_wood}")

        self.ready = self._wood_in_dedi > 29900
        print(f"Station is ready: {self.ready}")
        self.settings = ArbStationSettings.load()

        self.dedi = TekDedicatedStorage()
        self.chembench = ChemistryBench()
        self.forge = IndustrialForge()
        self.exo_mek = Dinosaur("Exo Mek", "assets/templates/exo_mek.png")
        self.bed = Bed("arb_craft")
        self.forge_bed = Bed("arb_cooking")
        self.pickup_bed = Bed("arb_pickup")

        self.bench_turns = [
            (self._player.turn_x_by, -80),
            (self._player.turn_y_by, -70),
            (self._player.turn_x_by, -50),
            (self._player.turn_y_by, 70),
            (self._player.turn_x_by, -50),
            (self._player.turn_y_by, -70),
        ]

        self.bottom_bench_turns = [
            (self._player.turn_x_by, -80),
            (self._player.turn_x_by, -50),
            (self._player.turn_x_by, -50),
        ]

    def is_ready(self) -> bool:
        """Checks if the station is ready for the next step."""
        if not self.settings.enabled:
            return False

        print(f"Checking whether arb station is ready, status: '{self.status}'")
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

        raise ValueError(f"{self.status} is not a valid status!")

    def complete(self) -> None:
        """Completes the stations next step corresponding to its status."""
        if self.status == Status.WAITING_FOR_WOOD:
            self.fill_forges_craft_spark()

        elif self.status == Status.COOKING_WOOD:
            self.craft_gunpowder()

        elif self.status == Status.WAITING_FOR_GUNPOWDER:
            self.craft_arb()

        elif self.status == Status.WAITING_FOR_ARB:
            self.pick_up_arb()

        else:
            raise ValueError(f"{self.status} is not a valid status!")

    @staticmethod
    def _set_data(key: str, value: Any) -> None:
        with open("bot/_data/station_data.json") as f:
            data: dict = json.load(f)

        data["arb"][key] = value

        with open("bot/_data/station_data.json", "w") as f:
            json.dump(data, f, indent=4, default=str)

    def add_wood(self, wood: int) -> None:
        """Called when wood is added to the dedi via the stryder on the
        crystal station. Once more than 29700 wood has been added the
        station is ready to refill the forges."""
        self._wood_in_dedi += wood
        if self._wood_in_dedi >= 29700:
            self.ready = True

        self._set_data("wood", self._wood_in_dedi)

    def gunpowder_ready(self) -> bool:
        """Checks if 5 minutes have passed since queuing gunpowder"""
        try:
            time_diff = round(
                (datetime.now() - self._started_crafting_gunpowder).total_seconds()
            )
            time_left = max(0, (5 * 60) - time_diff)
            if not time_left:
                print("Gunpowder has finished crafting.")
                return True
            print(f"{format_seconds(time_left)} left on gunpowder...")
            return False
        except AttributeError:
            return True

    def arb_ready(self) -> bool:
        """Checks if 15 minutes have passed since queuing arb"""
        try:
            time_diff = round(
                (datetime.now() - self._started_crafting_arb).total_seconds()
            )
            time_left = max(0, (15 * 60) - time_diff)
            if not time_left:
                print("ARB has finished crafting.")
                return True
            print(f"{format_seconds(time_left)} left on ARB...")
            return False
        except AttributeError:
            return True

    def charcoal_ready(self) -> bool:
        """Checks if 2h 45min have passed since filling the forges"""
        time_diff = round((datetime.now() - self._started_cooking_wood).total_seconds())
        time_left = max(0, (170 * 60) - time_diff)
        if not time_left:
            print("Charcoal has finished burning.")
            return True
        print(f"{format_seconds(time_left)} left on charcoal...")
        return False

    def spawn_at_forges(self) -> None:
        """Spawns at the forge bed"""
        self._player.prone()
        self._player.look_down_hard()

        self.forge_bed.spawn()
        self._player.spawn_in()

    def take_gas_from_forge_dedi(self) -> None:
        """Takes the gas from its dedi at the forge bed"""
        self._player.turn_y_by(40, delay=0.5)

        self.dedi.open()
        self.dedi.inventory.withdraw_stacks(1)
        self.dedi.close()
        self._player.sleep(2)
        self._player.turn_y_by(-40)

    def take_fungal_wood(self) -> None:
        """Takes the fungal wood from the dedi above."""
        self._player.look_up_hard()
        self._player.sleep(1)

        self.dedi.open()
        self.dedi.inventory.transfer_all()
        self.dedi.close()

        self._player.sleep(2)
        self._player.turn_y_by(160, delay=0.5)
        self._player.turn_y_by(20, delay=0.5)

    def transfer_gasoline(self, amount: int) -> None:
        """Transfers the given amount of gasoline, useful for
        precise amounts such as 11 per forge, or 1 per gunpowder craft
        """
        self._player.inventory.search(items.GASOLINE)
        self._player.inventory.select_slot(0)
        self._player.sleep(1)

        for _ in range(amount):
            pyautogui.click(clicks=2)
        self._player.inventory.delete_search()

    def forges_put_gas_back(self) -> None:
        """Puts the gas back into its dedi at the cooking bed"""
        self.dedi.deposit([items.GASOLINE], get_amount=False)
        self._player.look_up_hard()
        self._player.sleep(1)
        self.dedi.deposit([items.FUNGAL_WOOD], get_amount=False)

    def empty_forges(self) -> None:
        """Empties the forges, empties each forge and puts the charcoal into the dedi."""
        self.spawn_at_forges()
        right_turns: int = 0
        known_empty: set[int] = set()

        while right_turns < 4:
            # turn to the forge
            self._player.turn_90_degrees("right", delay=1)
            right_turns += 1
            if right_turns in known_empty:
                continue

            self.forge.open()
            if (
                not self.forge.inventory.has(items.CHARCOAL)
                or self.forge.inventory.count(items.FUNGAL_WOOD) > 20
            ):
                known_empty.add(right_turns)
                # forge does not have charcoal so go next
                self.forge.close()
                self._player.sleep(2)
                continue

            # forge has charcoal, take all charcoal and turn back to dedi
            if self.forge.inventory.has(items.GASOLINE):
                self.forge.inventory.transfer_all(items.GASOLINE)

            self.forge.inventory.transfer_all(items.CHARCOAL)
            self.forge.close()
            self._player.sleep(2)

            for _ in range(right_turns):
                self._player.turn_90_degrees("left", delay=1)
            right_turns = 0

            self._player.sleep(1)
            # deposit charcoal
            self.dedi.deposit([items.CHARCOAL], get_amount=False)

        self._player.turn_y_by(60, delay=0.5)
        self.dedi.deposit([items.GASOLINE], get_amount=False)

    def fill_forges_craft_spark(self) -> None:
        """Spawns at the forge bed and fills them with wood.
        Deposits 11 gasoline into each forge, and caps it with wood.

        Finishes with the remaining gasoline and wood deposited back into their
        dedis. Sets the most recent wood cooking timestamp upon finishing.
        """
        start = time.time()
        if not self.forges_emptied:
            self.empty_forges()
            self.forges_emptied = True

        self.spawn_at_forges()

        self.take_gas_from_forge_dedi()
        self.take_fungal_wood()

        # fill each forge
        for _ in range(3):
            self._player.turn_90_degrees("right", delay=1)
            self.forge.open()
            self.transfer_gasoline(7)
            self._player.inventory.transfer_all(items.FUNGAL_WOOD)
            self.forge.turn_on()
            self.forge.close()
            self._player.sleep(2)

        self._player.turn_90_degrees("right", delay=0.5)
        self._player.turn_y_by(40, delay=0.5)
        self.forges_put_gas_back()

        self.craft_sparkpowder()
        embed = self.create_forges_refilled_embed(round(time.time() - start))
        self._webhook.send_embed(embed)

        self._started_cooking_wood = datetime.now()
        self._wood_in_dedi -= 30000
        self.ready = False

        self._set_data("cooking_start", self._started_cooking_wood)
        self._set_data("wood", self._wood_in_dedi)

    def access_gasoline(self, mode: Literal["take", "deposit"]) -> None:
        """Turns to the gasoline dedi from the original spawn position,
        can either take gas or deposit it. Finishes in the original spawn
        position."""
        self._player.turn_x_by(-30, delay=0.5)
        self._player.turn_y_by(40, delay=0.5)
        self._player.sleep(1)

        if mode == "take":
            self.dedi.open()
            self.dedi.inventory.withdraw_stacks(1)
            self.dedi.close()
        else:
            self.dedi.deposit([items.METAL_INGOT], get_amount=False)

        self._player.sleep(2)
        self._player.turn_y_by(-40, delay=0.3)
        self._player.turn_x_by(30, delay=0.3)

    def access_stone(self, mode: Literal["take", "deposit"]) -> None:
        """Turns to the stone dedi from the original spawn position,
        can either take stone or deposit it. Finishes in the original spawn
        position."""
        self._player.turn_x_by(30, delay=1)

        if mode == "take":
            self.dedi.open()
            self.dedi.inventory.transfer_all()
            self.dedi.close()
        else:
            self.dedi.deposit([items.STONE], get_amount=False)

        self._player.sleep(2)
        self._player.turn_x_by(-30, delay=0.5)

    def access_flint(self, mode: Literal["take", "deposit"]) -> None:
        """Turns to the flint dedi from the original spawn position,
        can either take flint or deposit it. Finishes in the original spawn
        position."""
        self._player.turn_x_by(30, delay=0.3)
        self._player.turn_y_by(40, delay=1)

        if mode == "take":
            self.dedi.open()
            self.dedi.inventory.transfer_all()
            self.dedi.close()
        else:
            self.dedi.deposit([items.FLINT], get_amount=False)

        self._player.sleep(2)
        self._player.turn_y_by(-40, delay=0.5)
        self._player.turn_x_by(-30, delay=0.5)

    def access_metal(self, mode: Literal["take", "deposit"]) -> None:
        """Turns to the metal dedi from the original spawn position,
        can either take metal or deposit it. Finishes in the original spawn
        position."""
        self._player.turn_x_by(110, delay=1)

        if mode == "take":
            self.dedi.open()
            self.dedi.inventory.transfer_all()
            self.dedi.close()
        else:
            self.dedi.deposit([items.METAL_INGOT], get_amount=False)

        self._player.sleep(2)
        self._player.turn_x_by(-110, delay=0.3)

    def take_metal_queue_arb(self) -> None:
        """Takes metal and puts it into the exo mek, queues the ARB and
        return the metal to its dedi. Finishes in the original spawn
        position."""
        # take metal and turn to exo mek
        self.access_metal("take")
        for _ in range(2):
            self._player.turn_90_degrees(delay=1)

        # open the exo mek, search for ARB
        self.exo_mek.access()
        self._player.inventory.transfer(items.METAL_INGOT, 5400, self.exo_mek.inventory)
        self.exo_mek.inventory.open_tab("crafting")

        self.exo_mek.inventory.search(items.ARB)

        # craft 1k on each bp
        for slot in [(1292 + (i * 95), 296) for i in range(5)]:
            self._player.click_at(slot)
            for _ in range(10):
                self._player.press("a")
                self._player.sleep(0.2)

        # close the exo mek
        self.exo_mek.inventory.open_tab("inventory")
        self.exo_mek.close()
        self._player.sleep(2)

        # turn back to original position, put metal back
        for _ in range(2):
            self._player.turn_90_degrees("left", delay=1)
        self.access_metal("deposit")

    def fill_bottom_chembenches(
        self,
        gas: bool,
        material: items.Item,
        amount: int,
        craft: Optional[items.Item] = None,
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
        for func, arg in self.bottom_bench_turns:
            func(arg, delay=0.5)

            # open the chembench, go through the actions
            self.chembench.open()
            self.chembench.turn_off()
            if gas:
                while not self.chembench.is_turned_off():
                    self.transfer_gasoline(1)
                    self._player.sleep(1)

            if amount < 4000:
                self._player.inventory.transfer(
                    material, amount, self.chembench.inventory
                )
            else:
                self._player.inventory.transfer_all()

            # craft the given item
            if craft is not None:
                self.chembench.turn_on()
                self.chembench.inventory.open_tab("crafting")
                self.chembench.inventory.craft(craft, 900)
                self.chembench.inventory.open_tab("inventory")

            self.chembench.close()
            self._player.sleep(2)

        # reverse the turns to get back to the original position
        for func, arg in reversed(self.bottom_bench_turns):
            func(arg * -1, delay=0.5)

    def craft_sparkpowder(self) -> None:
        """Spawns at the station and starts crafting sparkpowder"""
        self.spawn()
        self.empty_out_chembenches()

        self.access_gasoline("take")
        self.access_stone("take")

        self.fill_bottom_chembenches(gas=True, material=items.STONE, amount=3300)
        self.access_stone("deposit")
        self.access_gasoline("deposit")

        self.access_flint("take")
        self.fill_bottom_chembenches(
            gas=False, material=items.FLINT, amount=7700, craft=items.SPARKPOWDER
        )
        try:
            self.access_flint("deposit")
        finally:
            self.status = Status.COOKING_WOOD
            self._set_data("status", "Cooking wood")

    def take_spark_out(self) -> None:
        """Scrolls down far enough to have a view on slot 51, so that we can determine
        we there is 50 slots left once slot 51 is free."""
        self.chembench.inventory.select_slot()
        self.chembench.inventory.scroll("down", rows=2)
        self._player.sleep(1)

        i = 0
        while self._slot_51_has_spark():
            self.chembench.inventory.select_slot(0)
            pyautogui.press("t")
            i += 1
            self._player.sleep(i / 200)

    def _slot_51_has_spark(self) -> bool:
        return (
            self.chembench.window.locate_template(
                items.SPARKPOWDER.inventory_icon,
                region=self.chembench.inventory.SLOTS[38],
                confidence=0.7,
                grayscale=True,
            )
            is not None
        )

    def distribute_spark_evenly(self) -> None:
        """Distributes spark evenly over the chembenches, by taking out until 50 slots
        on the bottom chembench and putting the taken spark into the upper chem bench."""
        for func, arg in self.bottom_bench_turns:
            func(arg, delay=0.5)

            # take until 50 slots from the bottom one
            self.chembench.open()
            self.take_spark_out()
            self.chembench.close()
            self._player.sleep(2)

            # turn to top one, put all taken spark into the upper one.
            self._player.turn_y_by(-70, delay=0.5)
            self.chembench.open()
            self._player.inventory.transfer_all(items.SPARKPOWDER)
            self.chembench.close()

            self._player.sleep(2)
            self._player.turn_y_by(70, delay=0.5)

        # reverse the turns to get back to original position
        for func, arg in reversed(self.bottom_bench_turns):
            func(arg * -1, delay=0.5)

    def empty_out_chembenches(self) -> None:

        for func, arg in self.bench_turns:
            func(arg, delay=0.7)

            self.chembench.open()
            self.chembench.inventory.transfer_all()
            self._player.inventory.drop_all()
            self.chembench.close()
            self._player.sleep(2)

        for func, arg in reversed(self.bench_turns):
            func(arg * -1, delay=0.7)

    def queue_gunpowder(self, transfer_mats: bool) -> None:
        """Queues gunpowder in every chembench, if transfer_mats is toggled
        it first takes gasoline and puts one gasoline into each chembench."""
        # get the gasoline if we need it
        if transfer_mats:
            self.access_gasoline("take")
            self._player.sleep(1)

            self.dedi.open()
            self.dedi.inventory.transfer_all()
            self.dedi.close()
            self._player.sleep(2)

        for func, arg in self.bench_turns:
            func(arg, delay=0.5)
            self.chembench.open()

            if transfer_mats:
                self.chembench.turn_off()
                while not self.chembench.is_turned_off():
                    self.transfer_gasoline(1)
                    self._player.sleep(1)

                self.chembench.turn_on()
                self._player.inventory.transfer_all(items.CHARCOAL)

            self.chembench.inventory.open_tab("crafting")
            self.chembench.inventory.craft(items.GUNPOWDER, 1000)
            self.chembench.inventory.open_tab("inventory")
            self._player.sleep(0.5)
            self.chembench.close()
            self._player.sleep(2)

        # reverse turns to get back to original position
        for func, arg in reversed(self.bench_turns):
            func(arg * -1, delay=0.5)

        # put away the remaining charcoal
        if transfer_mats:
            self.dedi.deposit([items.CHARCOAL], get_amount=False)
            self.access_gasoline("deposit")

    def craft_gunpowder(self) -> None:
        """Empties the forges, then spawns at the crafting bed, distributes
        sparkpowder evenly and queues gunpowder after. Returns an embed
        displaying the statistics, and the statistics object itself.
        """
        self.empty_forges()
        self.spawn()
        start = time.time()

        self.distribute_spark_evenly()
        for i in range(2):
            self.queue_gunpowder(transfer_mats=not i)

        embed = self.create_gunpowder_crafted_embed(
            round(time.time() - start), 7500 * 6
        )
        self._webhook.send_embed(embed)

        self.status = Status.WAITING_FOR_GUNPOWDER
        self._started_crafting_gunpowder: datetime = datetime.now()

        self._set_data("status", "Waiting for gunpowder")

    def empty_chembenches(self) -> None:
        """Empties the chembenches, because the player can only hold the
        gunpowder of 2 chembenches at once, we we empty a slice of 2. After
        each 2 forges have been emptied we put the gunpowder into the exo
        mek to later craft into ARB."""

        for i in range(2, 8, 2):
            # slice out the turns of the chembenches we need to access
            for index, (func, arg) in enumerate(self.bench_turns[0:i]):
                func(arg, delay=0.7)

                # check if we already emptied the prior chembenches
                if index >= i - 2:
                    self.chembench.open()
                    self.chembench.inventory.transfer_all()
                    self.chembench.turn_off()
                    self.chembench.close()
                    self._player.sleep(2)

            # reverse the turns to return back, once again sliced
            for func, arg in reversed(self.bench_turns[0:i]):
                func(arg * -1, delay=0.5)

            # turn to the exo mek to put the gunpowder in
            for _ in range(2):
                self._player.turn_90_degrees("right", delay=1)

            self.exo_mek.access()
            self._player.inventory.transfer_all(items.GUNPOWDER)
            self.exo_mek.inventory.close()
            self._player.sleep(2)

            for _ in range(2):
                self._player.turn_90_degrees("left", delay=1)

        self._player.drop_all()
        self._player.sleep(2)

    def craft_arb(self) -> None:
        """Spawns at the crafting bed, empties the chembenches to put the
        gunpowder into the exomek, then crafts ARB inside the exo mek.

        Returns an embed displaying the time taken and the statistics.

        Upon finishing, the the status property is set to `WAITING_FOR_ARB`,
        and the `_started_crafting_arb` datetime is created to check when its
        finished.
        """
        self.spawn()
        start = time.time()

        self.empty_chembenches()
        self.take_metal_queue_arb()

        embed = self.create_arb_queued_embed(round(time.time() - start))
        self._webhook.send_embed(embed)

        self.status = Status.WAITING_FOR_ARB
        self._started_crafting_arb: datetime = datetime.now()
        self._set_data("status", "Waiting for ARB")

    def travel_to_pickup_bed(self) -> None:
        """Travels to the arb pick up bed"""
        self._player.prone()
        self._player.look_down_hard()

        self.pickup_bed.spawn()
        self._player.spawn_in()

    def pick_up_arb(self) -> None:
        """Picks up the ARB from the exo mek and puts it into the dedis.
        Returns an embed displaying the time taken and how much ARB
        was crafted.

        This should be the last step of the station and once finished, the
        status property will be set back to `WAITING_FOR_WOOD`, so that it
        once again needs to be set `ready` by the collection point.
        """
        self.travel_to_pickup_bed()
        start = time.time()

        try:
            self.exo_mek.access()
            self.exo_mek.inventory.transfer_all(items.ARB)
            self.exo_mek.inventory.sleep(5)
            self._player.inventory.transfer_all("blueprint")
            self.exo_mek.inventory.close()
            self._player.sleep(5)

            for i, turn in enumerate([80, 60, 80, -60]):
                if i % 2 == 0:
                    self._player.turn_x_by(turn, delay=0.3)
                else:
                    self._player.turn_y_by(turn, delay=0.3)

                _, amount = self.dedi.deposit([items.ARB], get_amount=True)
                if amount:
                    break

            embed = self.create_embed(round(time.time() - start), amount)
            self._webhook.send_embed(embed)
            self.statistics["ARB"] = self.statistics.get("ARB", 0) + max(amount, 10000)

        finally:
            self.status = Status.WAITING_FOR_WOOD
            self._set_data("status", "Waiting for wood")

    def create_embed(self, time_taken: int, arb_profit: int) -> Embed:
        """Creates the final embed after all steps have been finished, displays
        the ARB made and the time taken."""
        embed = Embed(
            type="rich",
            title=f"Picked up the ARB!",
            color=0xFF5500,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{time_taken} seconds")
        embed.add_field(name="ARB crafted:", value=f"{max(arb_profit, 10000)}")

        embed.set_thumbnail(url=ARB_AVATAR)
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")
        return embed

    def create_arb_queued_embed(self, time_taken: int) -> Embed:
        """Returns an embed displaying that ARB has been queued and how
        long it took."""
        embed = Embed(
            type="rich",
            title=f"Queued Advanced Rifle Bullets at {self._name}!",
            color=0xE4CEB8,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{time_taken} seconds")
        embed.set_thumbnail(url=EXOMEK_AVATAR)
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")
        return embed

    def create_gunpowder_crafted_embed(self, time_taken: int, crafted: int) -> Embed:
        """Creates an embed that gunpowder has been queued, how long it took and
        roughly how much is being crafted."""
        embed = Embed(
            type="rich",
            title=f"Queued gunpowder at {self._name}!",
            color=0xFF5500,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{time_taken} seconds")
        embed.add_field(name="Gunpowder queued:", value=crafted)

        embed.set_thumbnail(url=CHEMBENCH_AVATAR)
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")
        return embed

    def create_forges_refilled_embed(self, time_taken: int) -> Embed:
        """Creates an embed displaying that the forge has been refilled and
        how long it took. Also displays if the forges were emptied."""

        embed = Embed(
            type="rich",
            title=f"Filled forges and crafted sparkpowder!",
            color=0xFF5500,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{time_taken} seconds")
        embed.add_field(name="Forges emptied:", value=True)

        embed.set_thumbnail(url=FORGE_AVATAR)
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")
        return embed
