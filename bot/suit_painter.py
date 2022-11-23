import random

from bot.ark_bot import ArkBot
from ark.player import Player
from ark.inventories import Vault
import pyautogui as pg
import time

REGION_1 = 240, 266
REGION_2 = 240, 327
REGION_3 = 240, 387
REGION_4 = 530, 266
REGION_5 = 530, 327
REGION_6 = 530, 387


PAINTABLE = {
    "tek_boots": [REGION_1, REGION_2, REGION_3, REGION_5, REGION_6],
    "tek_chest": [REGION_1, REGION_2, REGION_3, REGION_4, REGION_5, REGION_6],
    "tek_gauntlets": [REGION_1, REGION_2, REGION_3, REGION_5, REGION_6],
    "tek_leggings": [REGION_1, REGION_3, REGION_4, REGION_5, REGION_6],
    "tek_helmet": [REGION_1, REGION_2, REGION_3, REGION_5, REGION_6],
}


COLOR_LOCATIONS = [(x, y) for x in range(163, 614, 89) for y in range(537, 624, 86)]


class TekSuitPainter(ArkBot):
    """Main Suit Painter handle"""

    player = Player()
    vault = Vault()

    def __init__(self) -> None:
        super().__init__()
        self.suit_pieces = [
            "tek_boots",
            "tek_chest",
            "tek_gauntlets",
            "tek_leggings",
            "tek_helmet",
        ]

    def take_pieces(self, piece):
        """Takes as many pieces of a certain armor type as configurated by the user,
        comparing the previous amount in inventory to the new amount to avoid lag problems.
        """
        start = time.time()

        while not self.player.inventory.count_item(f"templates/{piece}.png") == 5:

            # set previous amount
            amount = self.player.inventory.count_item(f"templates/{piece}.png")
            pg.moveTo(1296, 278)
            pg.click(button="left")
            self.press("t")

            # wait for the new amount to not match the previous amount
            while self.player.inventory.count_item(f"templates/{piece}.png") == amount:
                pass

            if time.time() - start > 45:
                return

    def take_suit_pieces(self):
        """Turns to the fresh suit vault, opens it and takes x pieces of each
        suit piece where x is defined by the user.
        """
        self.vault.open()

        # repeat for every piece
        for piece in self.suit_pieces:
            self.vault.search_for(piece.split("_")[1])
            self.take_pieces(piece)

        self.vault.close()

    def take_fresh_suits(self):
        """Takes fresh suits and opens the painted vault"""
        self.take_suit_pieces()
        self.player.turn_90_degrees()
        self.vault.open()

    def get_all_targets(self):
        """Locates all armor pieces in the inventory and stores them in a hashmap"""
        return {
            piece: self.player.inventory.find_items(f"templates/{piece}.png")
            for piece in self.suit_pieces
        }

    def enter_paint_menu(self, piece_position):
        """Opens the paint menu by moving random color to the piece to be painted.
        This is achieved by matching for a grayscale image of the color.
        """
        random_paint = self.player.inventory.find_item(f"templates/color.png")
        pg.moveTo(random_paint)
        self.sleep(0.1)
        pg.dragTo(piece_position, button="left", duration=0.2)
        self.sleep(1)

    def paint_random(self, piece):
        """Paints a piece randomly, for each region the piece owns it will
        randomly choose a color field to select and apply.
        """
        # repeat for each region the piece supports
        for region in PAINTABLE[piece]:
            color = random.choice(COLOR_LOCATIONS)  # get a random color
            pg.moveTo(color)
            pg.click(button="left")

            # using double clicks instead of moving down to *apply paint*
            pg.moveTo(region)
            pg.click(button="left", clicks=3, interval=0.3)

    def paint_all_pieces(self, pieces):
        """Accepts a hashmap containing the positions of all pieces of
        a certain type. It will go over each piece applying random color
        to the available regions.
        """
        for suit_piece in pieces:

            # access the hashed list by piece key to get points
            for position in pieces[suit_piece]:
                self.enter_paint_menu(position)
                self.paint_random(suit_piece)
                self.press("esc")
                self.sleep(1)

    def run(self):
        while self.running:
            self.take_fresh_suits()
            pieces_to_paint = self.get_all_targets()
            self.paint_all_pieces(pieces_to_paint)
            self.player.inventory.transfer_all(self.vault, "tek")
            self.vault.close()
