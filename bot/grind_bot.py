from bot.ark_bot import ArkBot
from ark.player import Player

from ark.inventories import Vault, DedicatedStorage, Grinder, Inventory

from ark.items import *
from PIL import Image
from math import floor
from ark.beds import BedMap
from itertools import cycle
import pydirectinput as input

import numpy as np
import cv2 as cv
from pytesseract import pytesseract as tes


AUTO_TURRET_COST = {"paste": 50, "electronics": 70, "ingots": 140, "poly": 20}
TURRET_COST = {"paste": 200, "electronics": 270, "ingots": 540, "poly": 70}


class GrindBot(ArkBot):
    """Grind and craft handler class.

    Allows ling ling to spawn at a grind bed and turn grinded resources into structures.
    """

    def __init__(self) -> None:
        super().__init__()
        self.player = Player()
        self.beds = BedMap()
        self.grinder = Grinder()
        self.vault = Vault()
        self.dedis = DedicatedStorage()
        self.exo_mek = Inventory("Exo Mek", "exo_mek")

        self.current_station = "Gear Vault"

        self.station_turns = {
            "Grinder": (self.player.turn_x_by, -50),
            "Exo Mek": (self.player.turn_x_by, -110),
            "Vault": (self.player.turn_x_by, -95),
            "Crystal": (self.player.turn_x_by, -70),
            "Hide": (self.player.turn_y_by, 40),
            "Metal": (self.player.turn_x_by, -60),
            "Electronics": (self.player.turn_y_by, -40),
            "Pearls": (self.player.turn_x_by, -60),
            "Paste": (self.player.turn_y_by, 40),
            "Gear Vault": [(self.player.turn_y_by, -40), (self.player.turn_x_by, -70)],
        }

    def resync_to_vault(self, turn: bool = True) -> None:
        """Uses the bed to lay down and turn to get back the original position"""
        self.beds.lay_down()
        self.press(self.keybinds.use)
        self.sleep(1)
        if turn:
            self.player.turn_90_degrees("left")
            self.sleep(0.5)
            self.current_station = "Gear Vault"
            return

        self.current_station = "Electronics"

    def find_quickest_way_to(self, target_station) -> list[str]:
        stations = list(self.station_turns)

        start_counting = False
        forward_path = []
        if target_station == self.current_station:
            return [], "stay"

        for station in cycle(stations):
            if station == self.current_station:
                start_counting = True
                continue

            if not start_counting:
                continue

            forward_path.append(station)
            if station == target_station:
                break

        start_counting = False
        backward_path = []

        for station in cycle(reversed(stations)):
            if station == self.current_station:
                start_counting = True

            if not start_counting:
                continue

            backward_path.append(station)
            if station == target_station:
                break

        if len(forward_path) < len(backward_path):
            return forward_path, "forward"
        return backward_path, "backwards"

    def turn_to(self, target) -> None:
        path, direction = self.find_quickest_way_to(target)

        for station in path:
            self.current_station = station
            if direction == "backwards" and station == target:
                return

            if isinstance(self.station_turns[station], list):
                for turn in self.station_turns[station]:
                    method = turn[0]
                    args = turn[1] * (-1 if direction == "backwards" else 1)
                    method(args)
                    self.sleep(0.2)
                continue

            method = self.station_turns[station][0]
            args = self.station_turns[station][1] * (
                -1 if direction == "backwards" else 1
            )
            method(args)
            self.sleep(0.2)

    def grind_down_for_metal(self) -> None:
        gear = [fabricated_pistol, fabricated_sniper, assault_rifle, pumpgun]

        for item in gear:
            self.vault.open()
            self.player.inventory.drop_all_items("poly")

            self.vault.search_for(item.name)
            self.sleep(0.5)
            if not self.vault.has_item(item):
                continue

            self.vault.take_all()
            self.vault.close()

            self.turn_to("Grinder")
            self.grinder.open()
            self.grinder.turn_on()

            self.player.inventory.transfer_all(self.grinder, item.name)
            self.sleep(1)
            self.grinder.grind_all()

            self.grinder.take_all_items("poly")
            self.grinder.take_all_items("paste")
            self.grinder.close()

            self.turn_to("Paste")
            self.sleep(0.5)
            self.dedis.attempt_deposit(None, False)
            self.turn_to("Gear Vault")

        self.player.inventory.open()
        self.player.inventory.drop_all()
        self.player.inventory.close()

        self.turn_to("Grinder")
        self.player.crouch()
        self.grinder.open()
        self.sleep(0.5)

        self.player.do_drop_script(metal_ingot, self.grinder)
        self.resync_to_vault()

        self.turn_to("Metal")
        self.dedis.attempt_deposit(None, False)

    def grind_riot_gear(self) -> None:
        """Grind all the riot gear down, keep first 2 poly and all pearls, crystal
        from helmets into dedis."""
        # all pieces to grind
        gear = [riot_leggs, riot_chest, riot_gauntlets, riot_boots, riot_helmet]
        any_found = False

        for i, item in enumerate(gear):
            self.vault.open()
            self.vault.search_for(item.name)
            self.sleep(0.5)
            if not self.vault.has_item(item):
                continue
            any_found = True

            self.vault.take_all()
            self.vault.close()

            self.turn_to("Grinder")
            self.grinder.open()
            self.sleep(0.4)
            self.grinder.turn_on()

            self.player.inventory.transfer_all(self.grinder, item.name)
            self.sleep(1)
            self.grinder.grind_all()

            self.grinder.take_all_items("poly")
            self.grinder.take_all_items("pearl")
            self.grinder.close()

            if (i + 1) <= 2:
                self.turn_to("Exo Mek")
                self.exo_mek.open()
                self.player.inventory.transfer_all(self.exo_mek, "poly")
                self.exo_mek.close()
            else:
                self.player.inventory.open()
                self.player.inventory.drop_all_items("poly")
                self.player.inventory.close()

            self.turn_to("Pearls")
            self.sleep(1)
            self.dedis.attempt_deposit(None, False)
            self.sleep(1)
            self.turn_to("Gear Vault")

        if not any_found:
            return

        self.vault.close()
        self.turn_to("Grinder")
        self.player.crouch()
        self.grinder.open()
        self.player.do_drop_script(crystal, self.grinder)
        self.resync_to_vault()

        self.turn_to("Crystal")
        self.dedis.attempt_deposit(crystal, check_amount=False)
        self.sleep(0.5)
        self.turn_to("Gear Vault")
        self.sleep(0.5)

    def craft_turrets(self) -> None:
        self.turn_to("Exo Mek")
        self.exo_mek.open()
        self.exo_mek.open_craft()
        return

    def find_all_dedi_positions(self, image) -> list[tuple]:

        images = {}

        for dedi in ("pearl", "paste", "ingots", "electronics", "crystal", "hide"):
            region = self.find_dedi(dedi, image)
            if not region:
                return
            # convert bc grab screen is retarded + extend boundaries
            region = int(region[0] - 80), int(region[1] + region[3] + 5), 350, 130

            pil_img = Image.open(image)
            images[dedi] = pil_img.crop(
                (region[0], region[1], region[0] + region[2], region[1] + region[3])
            )
        return images

    def find_dedi(self, item, img) -> tuple:
        return self.locate_in_image(
            f"templates/{item}_dedi.png", img, confidence=0.8, grayscale=True
        )

    def get_dedi_screenshot(self) -> None:
        self.resync_to_vault(False)

        self.player.look_up_hard()
        self.sleep(0.2)
        self.player.look_down_hard()
        self.player.disable_hud()
        self.sleep(0.5)
        self.player.turn_y_by(-160)
        self.sleep(0.3)
        img = self.grab_screen(region=(0, 0, 1920, 1080), path="temp/dedis.png")
        self.sleep(0.5)

        self.player.disable_hud()
        return img

    def get_dedi_materials(self):
        """Tries to get the dedi materials up to 10 times. Will return a dict
        of the material and its amount on the first successful attempt.

        Raises `DediNotFoundError` after 10 unsuccessful attempts.
        """

        for i in range(10):
            amounts = {}

            # get dedi wall image
            dedis_image = self.get_dedi_screenshot()
            # get all dedis regions
            dedis = self.find_all_dedi_positions(dedis_image)

            # one dedi could not be determined, trying to move around
            if not dedis:
                print("Missing a dedi!")
                if i % 3 == 0 or not i:
                    self.press("w")
                else:
                    self.press("s")
                continue

            # got all regions, denoise and OCR the amount
            for name in dedis:
                img = self.denoise_text(dedis[name], (229, 230, 110), 15)
                raw_result = tes.image_to_string(
                    img,
                    config="-c tessedit_char_whitelist=0123456789 --psm 6 -l eng",
                ).rstrip()

                # add material and its amount to our dict
                amounts[name] = int(raw_result)

            print(amounts)
            return amounts

        raise Exception

    def get_crafting_method(self, owned_items):
        """Receives the list of materials we own and figures out the most 'efficient'
        way to craft turrets mainly taking in consideration the balance between metal
        and electronics.

        It first calculates the usage of the crafted mats we have, and then calculates
        with pearls and ingots instead of electronics.
        """
        # print(f"Materials owned at start: {owned_items}")

        # set our costs, no pearls for now
        cost = {"paste": 0, "ingots": 0, "electronics": 0}
        # find how many turrets we can craft right away
        lowest_1 = min(owned_items[material] / TURRET_COST[material] for material in cost)

        # set the inital cost 
        phase_1 = {
            "paste": int(TURRET_COST["paste"] * lowest_1),
            "ingots": int(TURRET_COST["ingots"] * lowest_1),
            "electronics": int(TURRET_COST["electronics"] * lowest_1),
        }

        # add the initial cost, remove it from the owned mats
        for material in phase_1:
            cost[material] += phase_1[material]
            owned_items[material] -= phase_1[material]

        # print(f"Cost for phase 1: {cost}, materials owned after {owned_items}")

        # set new turret cost using pearls and more ingots instead, set pearl value
        raw_turret_cost = {
            "paste": 200,
            "pearl": 270 * 3,
            "ingots": 540 + 270
        }
        cost["pearl"] = 0

        # once again get the amount of craftable turrets, create phase 2 cost
        lowest_2 = min(owned_items[material] / raw_turret_cost[material] for material in raw_turret_cost)
        phase_2 = {
            "paste": int(raw_turret_cost["paste"] * lowest_2),
            "ingots": int(raw_turret_cost["ingots"] * lowest_2),
            "pearl": int(raw_turret_cost["pearl"] * lowest_2)
        }

        # add each material to the total cost, electronics to craft is now pearls / 3
        for material in phase_2:
            cost[material] += phase_2[material]

        # print(f"Cost for phase 2: {phase_2}, total cost: {cost}\n\n")
        print(f"Need to craft {round(cost['pearl'] / 3)} electronics for {floor(lowest_1 + lowest_2)} Turrets")

        return cost


    def start(self):
        """Starts the crafting station"""
        self.grind_riot_gear()

        self.grind_down_for_metal()
        
        # self.craft_turrets()
