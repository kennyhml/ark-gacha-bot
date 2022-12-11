from dataclasses import dataclass

import pyautogui as pg
import pydirectinput as input

from ark.buffs import pod_xp
from ark.exceptions import BedNotAccessibleError, PlayerDidntTravelError
from ark.player import Player
from bot.ark_bot import ArkBot
from bot.unstucking import UnstuckHandler
from ark.server import Server

@dataclass
class Bed:
    name: str
    coords: tuple


class BedMap(ArkBot):
    """Main Bed Travelling Handler
    -----------------------------

    Handles travelling to beds up until the point where the flash screen appears.
    Methots are passed a `Bed` object for the beds name and location.
    """

    BEDS_REGION = (160, 70, 1050, 880)
    SEARCH_BAR = (306, 982)
    SPAWN_BUTTON = (731, 978)

    def is_open(self) -> bool:
        """Checks if the Bed menu is open"""
        return (
            self.locate_template(
                "templates/bed_filter.png", region=(140, 950, 150, 50), confidence=0.8
            )
            is not None
        )

    def open(self) -> bool:
        """Opens the bed menu. Times out after 30 unsuccessful
        attempts raising a `TimeoutError`"""
        c = 0
        while not self.is_open():
            c += 1
            self.press(self.keybinds.use)
            self.sleep(1)

            if c > 30:
                raise BedNotAccessibleError("Failed to access the bed!")

    def travelling(self) -> bool:
        """Check if we are currently travelling (whitescreen)"""
        return pg.pixelMatchesColor(959, 493, (255, 255, 255), tolerance=0)

    def await_travelling(self) -> None:
        """Waits for the whitescreent to appear to find out we travelled.
        Times out after 30 seconds raising a `TimeoutError`.
        """
        c = 0
        while not self.travelling():
            self.sleep(0.1)
            c += 1
            if c > 300:
                raise PlayerDidntTravelError("Failed to travel!")

        print("Now travelling!")

    def click_searchbar(self) -> None:
        """Clicks into the searchbar"""
        self.click_at(self.SEARCH_BAR)

    def click_spawn_button(self) -> None:
        """Clicks the spawn button"""
        self.click_at(self.SPAWN_BUTTON)

    def search(self, bed: Bed) -> None:
        """Searches for the given beds name"""
        self.click_searchbar()
        pg.typewrite(bed.name.lower(), interval=0.001)
        self.sleep(0.3)

    def travel_to(self, bed: Bed, from_pod: bool = False) -> None:
        """Travels to the given beds name"""

        print(f"Travelling to {bed.name}")

        # lay into the bed to make sure we dont access bags
        player = Player()
        if not from_pod:
            player.prone()
        player.look_down_hard()

        # open the bed map and travel to the bed
        self.open()
        self.search(bed)

        for _ in range(3):
            try:
                self.click_at(bed.coords)
                self.click_spawn_button()

                # wait for flash screen, then the HP bar
                self.await_travelling()
                return

            except PlayerDidntTravelError:
                if not UnstuckHandler(Server("47", "s47", "Center")).attempt_fix():
                    self.running = False
                print("Unable to travel! Trying again...")
                self.sleep(20)
        
    def lay_down(self) -> None:
        # lay into the bed to make sure we dont access bags
        player = Player()

        player.look_down_hard()
        player.turn_y_by(-40)
        self.sleep(0.5)
        
        input.keyDown(player.keybinds.use)
        player.sleep(1)

        # move to the lay option, pyautogui doesnt work for this
        input.moveTo(1266, 541, duration=0.1)
        player.sleep(0.1)
        input.moveTo(1266, 540, duration=0.1)
        player.sleep(0.3)
        input.keyUp(player.keybinds.use)
        player.click("left")

        # 'use' only needs to be held if we hold for too long after clicking
        input.keyUp(player.keybinds.use)
        player.sleep(10)


class TekPod(Bed):
    player = Player()
    discord_image = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/0/0b/Tek_Sleeping_Pod_%28Aberration%29.png/revision/latest/scale-to-width-down/228?cb=20171214081119"

    def can_enter(self) -> bool:
        return (
            self.player.locate_template(
                f"templates/pod.png",
                region=(840, 425, 240, 230),
                confidence=0.7,
            )
            is not None
        )

    def enter(self) -> bool:
        self.player.look_down_hard()
        self.player.sleep(1)
        input.keyDown(self.player.keybinds.use)

        self.player.sleep(1)
        if not self.can_enter():
            input.keyUp(self.player.keybinds.use)
            return False

        # move to the lay option, pyautogui doesnt work for this
        input.moveTo(1266, 541, duration=0.1)
        self.player.sleep(0.1)
        input.moveTo(1266, 540, duration=0.1)
        self.player.sleep(0.5)
        self.player.click("left")

        # 'use' only needs to be held if we hold for too long after clicking
        self.player.sleep(0.2)
        input.keyDown(self.player.keybinds.use)
        self.player.sleep(2)
        return self.player.has_effect(pod_xp)

    def leave(self) -> None:
        while self.player.has_effect(pod_xp):
            self.player.press(self.player.keybinds.use)
            self.player.sleep(3)

    def heal(self, duration) -> None:
        self.player.sleep(duration)