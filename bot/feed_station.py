from bot.ark_bot import ArkBot
from ark.inventories import Gacha, CropPlot, Inventory
from ark.player import Player
from ark.beds import Bed, BedMap
from ark.items import mejoberry
from ark.exceptions import NoBerriesLeftError

class BerryFeedStation(ArkBot):
    """Used to fill troughs with berries"""
    def __init__(self, bed: Bed) -> None:
        super().__init__()
        self.gacha = Gacha()
        self.player = Player()
        self.bed = bed
        self.bedmap = BedMap()
        self.trough = Inventory("Tek Trough", "tek_trough")

    def spawn(self) -> None:
        """Spawns and turns towards the gacha"""
        self.bedmap.travel_to(self.bed)
        self.player.await_spawned()
        self.sleep(1)

        # use the beds name to determine what direction to turn
        if int(self.bed.name[-2:]) % 2 == 0:
            self.player.turn_90_degrees("right")
        else:
            self.player.turn_90_degrees("left")

    def do_crop_plots(self) -> None:
        """Does the crop plot stack, finishes facing the last stack"""
        if int(self.bed.name[-2:]) % 2 == 0:
            direction = "left"
        else:
            direction = "right"

        for _ in range(2):
            self.player.turn_90_degrees(direction)
            self.player.do_precise_crop_plot_stack()
    
    def take_pellets(self) -> None:
        """Take the pellets from the gacha"""
        self.sleep(0.5)
        self.gacha.open()
        if self.gacha.has_item(mejoberry):
            self.gacha.close()
            self.gacha.open()

        self.gacha.search_for("ll")
        self.sleep(0.3)

        self.gacha.take_all()
        self.player.inventory.await_items_added()
        self.sleep(0.5)
        self.player.inventory.transfer_some_pellets(self.player.inventory, transfer_back=25)
        self.gacha.close()

    def put_pellets_back(self) -> None:
        if int(self.bed.name[-2:]) % 2 == 0:
            self.player.turn_90_degrees("left")
        else:
            self.player.turn_90_degrees("right")
        self.gacha.open()
        self.player.inventory.transfer_all(self.gacha, "ll")
        self.gacha.close()

    def fill_trough(self) -> None:
        self.sleep(0.3)
        self.trough.open()
        self.player.inventory.transfer_all(self.trough)
        self.sleep(0.5)
        if not self.player.inventory.has_item(mejoberry):
            self.trough.close()
            raise NoBerriesLeftError("No Berries left!")
        self.trough.close()

    def fill_troughs(self) -> None:
        try:
            self.player.crouch()
            self.player.look_down_hard()
            self.sleep(0.2)
            self.player.turn_y_by(-150)
            self.sleep(0.2)

            if self.bed.name[-2:] == "01":
                self.player.turn_y_by(10)
                self.sleep(0.3)
                self.player.turn_x_by(80)
                self.fill_trough()
                self.player.turn_y_by(-40)
                self.fill_trough()

                self.player.crouch()
                self.fill_trough()

                self.player.turn_x_by(40)
                self.fill_trough()

                self.player.crouch()
                self.fill_trough()

                self.player.turn_y_by(40)
                self.fill_trough()
                self.player.turn_x_by(50)
                self.fill_trough()
                self.player.crouch()
                self.fill_trough()
                self.player.turn_y_by(-40)
                self.fill_trough()

            elif self.bed.name[-2:] in ["02", "00"]:
                self.player.turn_y_by(10)
                self.sleep(0.3)
                self.player.turn_x_by(-80)
                self.fill_trough()
                self.player.turn_y_by(-40)
                self.fill_trough()

                self.player.crouch()
                self.fill_trough()

                self.player.turn_x_by(-40)
                self.fill_trough()
                self.player.crouch()
                self.fill_trough()
                self.player.turn_y_by(40)
                self.fill_trough()
                self.player.turn_x_by(-50)
                self.fill_trough()
                self.player.crouch()
                self.fill_trough()
                self.player.turn_y_by(-40)
                self.fill_trough()

            elif self.bed.name[-2:] == "03":
                self.player.turn_y_by(10)
                self.sleep(0.3)
                self.player.turn_x_by(90)
                self.fill_trough()
                self.player.turn_y_by(-40)
                self.fill_trough()
                self.player.crouch()
                self.fill_trough()

                self.player.turn_x_by(40)
                self.fill_trough()
                self.player.crouch()
                self.fill_trough()
                self.player.turn_y_by(40)
                self.fill_trough()
                self.player.turn_x_by(50)
                self.fill_trough()
                self.player.crouch()
                self.fill_trough()
                self.player.turn_y_by(-40)
                self.fill_trough()

        except NoBerriesLeftError:
            pass

    def run(self) -> None:
        """Runs the feed station"""
        self.spawn()
        self.take_pellets()
        self.do_crop_plots()
        self.fill_troughs()