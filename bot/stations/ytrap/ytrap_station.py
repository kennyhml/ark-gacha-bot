import itertools  # type:ignore[import]
import time
from typing import Literal, final

from ark import Bed, Gacha, Player, TekCropPlot, TribeLog, exceptions, items
from discord import Embed  # type:ignore[import]
from ...tools import threaded
from ...webhooks import InfoWebhook
from .._station import Station


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

    turn_direction :class:`Literal["left", "right"]`:
        The turn direction for the crop plots, default right.

    stacks :class:`int`:
        The amount of crop plot stacks the station has.

    per_stack :class:`int`:
        The amount of crop plot stacks per station.

    Properties
    ----------
    stacks :class:`str`:
        A nice overview of all the stacks and their crop plots

    pellet_coverage :class:`str`:
        The pellet coverage of the station, for example 40%
    """

    Y_TRAP_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/c/cb/Plant_Species_Y_Trap_%28Scorched_Earth%29.png/revision/latest?cb=20160901233007"

    def __init__(
        self,
        name: str,
        player: Player,
        tribelog: TribeLog,
        info_webhook: InfoWebhook,
        *,
        turn_direction: Literal["left", "right"] = "right",
        stacks: int = 3,
        per_stack: int = 8,
        expected_pellet_coverage: float = 0.8,
    ) -> None:
        self._name = name
        self._player = player
        self._tribelog = tribelog
        self._webhook = info_webhook
        self._turn_direction = turn_direction
        self.bed = Bed(name)
        self.gacha = Gacha(name)
        self.expected_pellet_coverage = expected_pellet_coverage
        self.total_completions = 0
        self.total_ytraps_deposited = 0
        self._stacks = [
            [
                TekCropPlot(f"Crop Plot {stack+ 1}:{idx+1} at {name}")
                for idx in range(per_stack)
            ]
            for stack in range(stacks)
        ]
        
    def is_ready(self) -> bool:
        return True

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
        max_pellets = len(plots) * 20
        total_pellets = sum(
            [plot.inventory.contents.get(items.PELLET.name, 0) for plot in plots]
        )
        return min(total_pellets / max_pellets, 1.0)

    def complete(self) -> None:
        """Completes the Y-Trap station. Travels to the gacha station,
        empties the crop plots and fills the gacha.
        """
        self.spawn()
        start = time.time()

        self.refill = (
            self.pellet_coverage < self.expected_pellet_coverage
            and self.total_completions > 0
        )

        if self.refill:
            self._take_pellets_from_gacha()

        self._player.crouch()
        turns = len(self._stacks)

        for stack in range(turns):
            self._player.turn_90_degrees(self._turn_direction, delay=0.5)
            self._do_crop_plot_stack(self._stacks[stack])

        for _ in range(4 - turns):
            self._player.turn_90_degrees(delay=1)

        added_traps = self._load_gacha()

        self.total_ytraps_deposited += added_traps
        self.total_completions += 1

        embed = self._create_embed(round(time.time() - start), added_traps)
        self._webhook.send_embed(embed)

    def _do_crop_plot_stack(self, stack: list[TekCropPlot]) -> None:
        """Empties a stack of crop plots."""

        @threaded("Standing up")
        def stand_up() -> None:
            self._player.stand_up()

        self._player.look_down_hard()
        turns = [-130, *[-17] * 5, 50, -17, -17, -17]

        for idx, (turn_value, crop_plot) in enumerate(zip(turns, stack)):
            if idx == 6:
                stand_up()

            self._player.turn_y_by(turn_value, delay=0.3)
            self._take_ytraps_put_pellets(crop_plot)

        self._player.crouch()

    def _take_ytraps_put_pellets(self, crop_plot: TekCropPlot) -> None:
        """Takes ytraps out of a crop plot, then puts pellets in if
        we need to refill them. Skips taking or transferring if there
        is no items available.

        If the crop plot could not be opened it will simply be skipped."""
        try:
            crop_plot.open()
        except (exceptions.WheelError):
            crop_plot.action_wheel.deactivate()
            return

        if crop_plot.inventory.has(items.Y_TRAP):
            crop_plot.inventory.search(items.Y_TRAP, delete_prior=False)
            crop_plot.inventory.transfer_all()

        if self.refill:
            self._player.inventory.transfer_all()

        crop_plot.inventory.set_content(items.PELLET)
        crop_plot.close()

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

        # take all the pellets (to avoid losing out on traps because of cap)
        self.gacha.access()
        ytraps = self._player.inventory.count(items.Y_TRAP) * 10

        if ytraps:
            self.gacha.inventory.transfer_all(items.PELLET)
            self._player.inventory.transfer_all(items.Y_TRAP)

        if ytraps >= 400:
            self._player.sleep(0.3)
            ytraps_removed = self._player.inventory.get_amount_transferred(items.Y_TRAP)

        self._player.inventory.transfer_all()

        if self._player.inventory.has(items.Y_TRAP):
            self._player.inventory.drop(items.Y_TRAP)

        self._player.inventory.drop_all()
        self._player.inventory.close()

        if ytraps < 420 or not 0 < ytraps_removed < 800:
            return ytraps
        return ytraps_removed

    def _validate_stats(self, time_taken: int, ytraps: int) -> str:
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
        if self.refill:
            if time_taken > 170:
                return "Time taken was unusually long, even for the first lap!"
            return f"Station works as expected for the first lap!"

        # check trap amount, below 400 is not normal
        if ytraps < 400:
            result += f"The amount of Y-Traps deposited is too low.\n"

        # check time taken for station
        if time_taken > 100:
            result += f"The time taken was unsually long!"

        return result if result else "Station works as expected."

    def _create_embed(self, time_taken: int, ytraps: int) -> Embed:
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
            description=(self._validate_stats(time_taken, ytraps)),
            color=0xFC97E8,
        )

        embed.add_field(name="Time taken:", value=f"{time_taken} seconds")
        embed.add_field(name="Y-Traps:", value=ytraps)
        embed.add_field(name="Pellets:", value=f"{round(self.pellet_coverage * 100)}%")

        embed.set_thumbnail(url=self.Y_TRAP_AVATAR)
        embed.set_footer(text="Ling Ling on top!")
        return embed
