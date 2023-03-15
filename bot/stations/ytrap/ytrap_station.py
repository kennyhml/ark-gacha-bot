from __future__ import annotations

import itertools  # type:ignore[import]
import time
from typing import final

from ark import Bed, DinoExport, Gacha, Player, TekCropPlot, exceptions, items
from discord import Embed  # type:ignore[import]

from ...webhooks import InfoWebhook, TribeLogWebhook
from .._crop_plot_helper import do_crop_plot_stack, set_stack_folders
from .._station import Station
from ._settings import YTrapStationSettings


@final
class YTrapStation(Station):
    """Represents a plant Y-Trap station, the most commonly executed station.
    Like all other stations, it follows the `Station` abstract base class.

    Each station on the tower is represented by a different YTrapStation, which
    allows it to focus on it's own status only. Each station has has it's own
    bed, turning and stack attributes, and its own crop plots that are aware
    of which station they belong to.

    Each `TekCropPlot` represents a singular tek crop plot in the stacks, it is
    not a single reused instance. This allows to keep track of the contents of
    each crop plot and then calculate the total pellet coverage of the station
    at a later point, to decide whether a refill should be initiated.

    Parameters
    -----------
    name :class:`str`:
        The name of the station, or the name of the bed to travel to.

    player :class:`Player`:
        The player instance to handle movements.

    tribelog :class:`Tribelog`:
        The tribelog instance to check tribelogs when spawning.

    info_webhook :class:`InfoWebhook`:
        The info webhook instance to post station statistics to.

    Properties
    ----------
    stacks :class:`str`:
        A nice overview of all the stacks and their crop plots

    pellet_coverage :class:`str`:
        The pellet coverage of the station, for example 40%
    """

    Y_TRAP_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/c/cb/Plant_Species_Y_Trap_%28Scorched_Earth%29.png/revision/latest?cb=20160901233007"
    total_ytraps_collected = 0
    lap = 0
    station_times: list[int] = []

    def __init__(
        self,
        name: str,
        player: Player,
        tribelog: TribeLogWebhook,
        info_webhook: InfoWebhook,
        settings: YTrapStationSettings,
    ) -> None:
        self._name = name
        self._player = player
        self._tribelog = tribelog
        self._webhook = info_webhook
        self.settings = settings

        if (l2 := settings.plots_per_stack) != (l1 := len(settings.crop_plot_turns)):
            raise ValueError(
                f"Turns do not match crop plots, got {l2} crop plots, and {l1} turns."
            )

        self.bed = Bed(name)
        self.gacha = Gacha(name)
        self.total_completions = 0
        self._stacks = [
            [
                TekCropPlot(f"Crop Plot {stack+ 1}:{idx+1}")
                for idx in range(self.settings.plots_per_stack)
            ]
            for stack in range(self.settings.plot_stacks)
        ]

    @property
    def stacks(self) -> str:
        backslash = "\n"
        return "\n".join(
            f"Stack {idx + 1}\n{f'{backslash}'.join(str(crop_plot) for crop_plot in self._stacks[idx])}"
            for idx in range(len(self._stacks))
        )

    @property
    def pellet_coverage(self) -> float:
        """Gets the fill level of the station, i.e if every crop splot has
        10/20 pellets, the fill level is 0.5 or 50%"""
        plots = list(itertools.chain(*self._stacks))
        max_pellets = len(plots) * 19
        total_pellets = sum(
            [plot.inventory.contents.get(items.PELLET.name, 0) for plot in plots]
        )
        return min(total_pellets / max_pellets, 1.0)

    @staticmethod
    def build_stations(
        player: Player, tribelog: TribeLogWebhook, info_webhook: InfoWebhook
    ) -> itertools.cycle | list:
        settings = YTrapStationSettings.load()
        if not settings.enabled:
            return []

        return itertools.cycle(
            [
                YTrapStation(
                    f"{settings.ytrap_prefix}{i:02d}",
                    player,
                    tribelog,
                    info_webhook,
                    settings,
                )
                for i in range(settings.ytrap_beds)
            ]
        )

    def is_ready(self) -> bool:
        return True

    def complete(self) -> None:
        """Completes the Y-Trap station.

        Spawns at the station, empties the crop plots and loads the gacha.
        Whether the crop plots need to be refilled with pellets is determined
        by the pellet coverage of the station, which will only be available
        once the station has been completed at least once.
        """
        self.spawn()
        start = time.time()
        refill = (
            self.pellet_coverage < self.settings.min_pellet_coverage
        ) and self.total_completions > 0

        if refill:
            self._take_pellets_from_gacha()

        dead_crop_plots = self._do_crop_plot_stacks(refill)

        for _ in range(4 - len(self._stacks)):
            self._player.turn_90_degrees(delay=1)

        self._player.look_down_hard()
        self._player.turn_y_by(self.settings.gacha_turn, delay=0.5)

        added_traps = self._load_gacha()

        time_taken = round(time.time() - start)
        self._add_statistics(time_taken, added_traps)
        embed = self._create_embed(time_taken, added_traps, dead_crop_plots, refill)
        self._webhook.send_embed(embed)

    def _add_statistics(self, time_taken: int, traps_collected: int) -> None:
        """Adds the completion to the statistics to keep track of."""
        self.station_times.append(time_taken)
        self.statistics["YTrap Station Time"] = round(
            sum(self.station_times) / len(self.station_times)
        )
        self.total_completions += 1
        if self.total_completions > self.lap:
            YTrapStation.lap = self.total_completions
        YTrapStation.total_ytraps_collected += traps_collected

    def _do_crop_plot_stacks(self, refill: bool) -> list[TekCropPlot]:
        """Empties the crop plots using the crop plot helpers."""
        dead_crop_plots: list[TekCropPlot] = []
        self._player.crouch()

        precise = self.settings.mode == "precise" or (
            self.settings.mode == "precise refill" and refill
        )

        for stack in self._stacks:
            self._player.turn_90_degrees(self.settings.turn_direction, delay=0.5)
            if self.settings.mode == "set folders":
                set_stack_folders(self._player, stack)
                continue

            do_crop_plot_stack(
                self._player,
                stack,
                items.Y_TRAP,
                self.settings.crop_plot_turns,
                dead_crop_plots,
                refill=refill,
                precise=precise,
                delay=self.settings.plot_delay,
            )
        return dead_crop_plots

    def _take_pellets_from_gacha(self) -> None:
        """Takes the pellets from the gacha (on a refill lap only).

        Expects the gacha in a closed state, leaves the gacha in a closed state.
        Raises a `NoItemsAddedError` if no pellets could be taken from the gacha.
        """
        self.gacha.access()
        self.gacha.inventory.search(items.PELLET)

        if not self.gacha.inventory.has(items.PELLET):
            self.gacha.inventory.close()
            return

        # take the pellets and transfer some rows back
        self.gacha.inventory.transfer_all()
        self._player.inventory.await_items_added(items.PELLET)
        self._player.inventory.search(items.PELLET)

        for _ in range(7):
            self._player.inventory.transfer_top_row(0.2)
            if self._player.inventory.count(items.PELLET) <= 30:
                break

        self.gacha.inventory.close()

    def _load_gacha(self) -> int:
        """Fills the gacha after emptying crop plots. It does so by first
        taking all the pellets to make space for ytraps, then putting the
        ytraps in and then filling it up with pellets again.

        Returns the amount of ytraps that were deposited into the gacha.
        """
        try:
            self.gacha.access()
        except exceptions.InventoryNotAccessibleError:
            print("Could not access gacha, standing up...")
            self._player.stand_up()
            self.gacha.access()

        self._ensure_looking_at_gacha()
        if self.settings.auto_level_gachas:
            self._check_level_gacha()

        ytraps = self._player.inventory.count(items.Y_TRAP) * 10
        if ytraps:
            self.gacha.inventory.transfer_all(items.PELLET)
            self._player.inventory.transfer_all(items.Y_TRAP)

        self._player.inventory.transfer_all()
        self._player.sleep(0.3)

        if not self._player.inventory.has(items.Y_TRAP):
            self._player.inventory.drop_all()
            self._player.inventory.close()
            return ytraps

        self._player.inventory.drop_all([items.PELLET])
        self._player.inventory.drop(items.Y_TRAP)
        self._player.inventory.close()
        return ytraps

    def _ensure_looking_at_gacha(self) -> None:
        """Makes sure we are looking at the gacha. If there is a ytrap seed inside
        inventory its safe to say we ended up inside a crop plot instead.

        If we turn more than 3 times and are still finding a ytrap seed, a
        `InventoryNotAccessibleError` is raised.
        """
        times_turned = 0
        while self.gacha.inventory.has(items.YTRAP_SEED):
            times_turned += 1
            if times_turned > 3:
                raise exceptions.InventoryNotAccessibleError(self.gacha.inventory)

            self.gacha.close()
            self._player.sleep(2)
            self._player.turn_90_degrees(self.settings.turn_direction)
            self.gacha.access()

    def _check_level_gacha(self) -> None:
        if not self.gacha.inventory.has_level_up():
            return

        print("Gacha has a level up available! Checking stats...")
        self.gacha.inventory.close()
        self._player.sleep(0.5)

        self.gacha.action_wheel.export_data()
        self.gacha.access()

        data = DinoExport.load_most_recent()
        crafting_to_level = round((0.100000 - data.crafting) / 0.01)
        if crafting_to_level:
            print(f"Need to level crafting {crafting_to_level} times.")
            self.gacha.inventory.level_skill("crafting", crafting_to_level)

        print("Leveling weight...")
        while self.gacha.inventory.has_level_up():
            self.gacha.inventory.level_skill("weight", 5)
        self._player.sleep(3)

    def _validate_stats(self, time_taken: int, ytraps: int, refill: bool) -> str:
        """Checks on the amount of traps deposited given the current runtime.

        Parameters:
        ----------
        statistics :class:`StationStatistics`:
            The statistics object of the station to take the data from.

        Returns:
        ---------
        A string displaying if the time taken and the Y-Traps deposited
        are within a valid range.
        """
        result = ""

        # different expectations for first lap (more tasks, dead crop plots)
        if refill:
            if time_taken > 170:
                return "Time taken was unusually long, even for the first lap!"
            return f"Station works as expected for the first lap!"

        # check trap amount, below 400 is not normal
        if ytraps < 360:
            result += f"The amount of Y-Traps deposited is too low.\n"

        # check time taken for station
        if time_taken > 120:
            result += f"The time taken was unsually long!"

        return result if result else "Station works as expected."

    def _create_embed(
        self, time_taken: int, ytraps: int, dead: list[TekCropPlot], refilled: bool
    ) -> Embed:
        """Creates a `discord.Embed` from the stations statistics.

        The embed contains info about what station was finished, if the time
        was within a normal range, how long it took and how many Y-Traps
        were deposited into the gacha.

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
            title=f"Finished gacha station '{self._name}'!",
            description=(self._validate_stats(time_taken, ytraps, refilled)),
            color=0xFC97E8,
        )

        embed.add_field(name="Time taken:", value=f"{time_taken} seconds")
        embed.add_field(name="Y-Traps:", value=ytraps)
        embed.add_field(name="Pellets:", value=f"{round(self.pellet_coverage * 100)}%")

        if dead:
            embed.add_field(
                name="Dead crop plots:",
                value="\n".join(
                    f"Stack {plot.name.split(':')[0][-1]}, index {plot.name.split(':')[1]}"
                    for plot in dead
                ),
            )

        if self.pellet_coverage < self.settings.min_pellet_coverage:
            embed.description = "Station will be refilled next lap."
        embed.set_thumbnail(url=self.Y_TRAP_AVATAR)

        return embed
