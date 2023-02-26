from typing import Optional
from ark import Player, TekCropPlot, exceptions, items

from ..tools import threaded


def do_crop_plot_stack(
    player: Player,
    stack: list[TekCropPlot],
    item: Optional[items.Item],
    turns: list[int],
    dead: list[TekCropPlot],
    *,
    refill: bool,
    precise: bool
) -> None:
    """Empties a stack of crop plots."""

    @threaded("Standing up")
    def stand_up() -> None:
        player.stand_up()

    player.look_down_hard()
    fails = 0
    for idx, (turn_value, crop_plot) in enumerate(zip(turns, stack)):
        if idx == 6:
            stand_up()

        player.turn_y_by(turn_value, delay=0.3)
        if not take_and_refill(player, crop_plot, item, dead, refill=refill, precise=precise):
            fails += 1
            if fails >= 2:
                raise exceptions.InventoryNotAccessibleError
    player.crouch()


def take_and_refill(
    player: Player,
    crop_plot: TekCropPlot,
    item: Optional[items.Item],
    dead: list[TekCropPlot],
    *,
    refill: bool,
    precise: bool
) -> bool:
    """Takes ytraps out of a crop plot, then puts pellets in if
    we need to refill them. Skips taking or transferring if there
    is no items available.

    If the crop plot could not be opened it will simply be skipped."""
    try:
        crop_plot.open()
        if precise:
            _adjust_for_crop_plot(player, crop_plot)
    except (exceptions.WheelError):
        crop_plot.action_wheel.deactivate()
        return False

    if not crop_plot.inventory.has(items.YTRAP_SEED):
        dead.append(crop_plot)

    if item and crop_plot.inventory.has(item):
        crop_plot.inventory.search(item, delete_prior=False)
        crop_plot.inventory.transfer_all()

    if refill:
        player.inventory.transfer_all()

    crop_plot.inventory.set_content(items.PELLET)
    crop_plot.close()
    return True

def _adjust_for_crop_plot(
    player: Player, crop_plot: TekCropPlot
) -> None:
    try:
        expected_idx = int(crop_plot.name.split(":")[1])
        crop_plot_idx = crop_plot.inventory.get_folder_index()
    except exceptions.UnknownFolderIndexError:
        return

    while crop_plot_idx != expected_idx:
        crop_plot.close()

        player.turn_y_by(7 if crop_plot_idx > expected_idx else -7, delay=0.3)

        crop_plot.open()
        crop_plot_idx = crop_plot.inventory.get_folder_index()


def set_stack_folders(player: Player, stack: list[TekCropPlot]) -> None:
    player.turn_y_by(-60)
    folders = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH", "III", "JJJ", "KKK"]
    player.look_down_hard()
    player.turn_y_by(-110)

    stack_has_up_to = 0

    for idx, (crop_plot, folder) in enumerate(zip(stack, folders), start=1):
        if idx == 7:
            player.stand_up()
            player.turn_y_by(60, delay=0.5)

        if idx <= stack_has_up_to:
            continue
        
        while True:
            player.turn_y_by(-5)
            try:
                crop_plot.open()
            except exceptions.WheelError:
                pass
            try:
                curr_idx = crop_plot.inventory.get_folder_index()
            except exceptions.UnknownFolderIndexError:
                crop_plot.inventory.create_folder(folder)
                crop_plot.close()
                break

            crop_plot.close()
            stack_has_up_to = curr_idx
            if stack_has_up_to >= idx:
                break

