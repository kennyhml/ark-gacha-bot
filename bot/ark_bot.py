"""
API for ark bot related functions such as input emulation and template matching with window scaling.
"""

import json
import os
import time
from typing import Optional

import pyautogui as pg  # type: ignore[import]
import pydirectinput as input  # type: ignore[import]
import win32clipboard # type: ignore[import]
from dacite import from_dict
from discord import File, Webhook  # type: ignore[import]
from pynput.mouse import Button, Controller  # type: ignore[import]

from ark.exceptions import BotTerminatedError

mouse = Controller()
from ark.window import ArkWindow
from bot.settings import Keybinds

pg.FAILSAFE = False

class ArkBot(ArkWindow):
    """Main ArkBot class
    ----------------------------
    Responsible for handling mouse movements and clicks in the ark window
    as well as loading the configs.

    Class attributes:
    -----------------
    paused :class:`bool`:
        Whether the bot is currently paused or not

    running :class:`bool`:
        Whether the bot is currently running or not

    TODO:
    Find a better way to control the runtime state to reduce cohesion.
    """
    __version__ = "1.3.3"
    paused = False
    running = True
    default_avatar = "https://steamuserimages-a.akamaihd.net/ugc/883133594330098188/6F62B1436FB2C7F26F028ACCA931CB5AE7C3F4F3/?imw=512&&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=false"

    def __init__(self) -> None:
        super().__init__()
        with open("settings/keybinds.json") as f:
            self.keybinds: Keybinds = from_dict(Keybinds, json.load(f))

    def check_status(self):
        """Bot runtime check, raises `TerminatedException` if the
        bot has been terminated (by user keypress). Sleeps indefinitely
        while paused by user."""

        if not self.running:
            raise BotTerminatedError

        while self.paused:
            time.sleep(0.1)
            if not self.running:
                raise BotTerminatedError

    def sleep(self, duration: int | float):
        """Sleeps the given duration.

        Parameters:
        -------------
        duration :class:`int` | `float`:
            The duration to sleep.
        """
        self.check_status()
        time.sleep(duration)

    def move_to(
        self, x: Optional[int] = None, y: Optional[int] = None, convert: bool = True
    ) -> None:
        """Moves to the given position, scales passed coordinates by default.

        Parameters
        -----------
        x, y: :class:`int` | `tuple`
            The coordinates to move to, normalized

        convert: :class:`bool`
            Convert the coordinate to the current resolution
        """
        self.check_status()
        x, y = pg._normalizeXYArgs(x, y)

        # we may not need to convert if the point comes from a template match
        if convert:
            x, y = self.convert_point(x, y)

        input.moveTo(x, y)

    def click(self, button):
        """Sends a click event for the given button.

        Parameters:
        -------------
        button :class:`str`:
            The button click to emulate.
        """
        self.check_status()
        pg.click(button=button)

    def press(self, key):
        """Sends a press event for the given key.

        Parameters:
        -------------
        key :class:`str`:
            The key press to emulate.
        """
        self.check_status()

        # check if pydirectinput supports the key
        if key not in ["mouse4", "mouse5"]:
            pg.press(key)
            return

        # use pynputs Controller to emulate side mouse button presses
        mouse.click(Button.x1 if key == "mouse5" else Button.x2)

    def click_at(self, x=None, y=None, button: str = "left", delay: float = 0.1):
        """Moves to a given location and clicks with the mouse.

        Parameters:
        ----------
        pos: :class:`tuple`
            The (x,y) coordinates of the point

        button: :class:`str`
            The button to press
        """
        x, y = pg._normalizeXYArgs(x, y)
        self.move_to(self.convert_point(x, y))
        self.sleep(delay)
        pg.click(button=button)
        self.sleep(0.1)

    def set_clipboard(self, text):
        """Puts the passed text into the clipboard to allow for pasting"""
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_TEXT)
        win32clipboard.CloseClipboard()

    def send_to_discord(
        self,
        webhook: Webhook,
        message: str,
        file: str = "",
        name: str = "Ark Bot",
        avatar: str = default_avatar,
    ) -> None:
        """Sends the given message to the given webhook.
        Parameters:
        -----------
        webhook :class:`Webhook`:
            A discord.Webhook object to send the message to
        message :class:`str`:
            The message to send to discord
        name :class:`str`:
            The appearance name of the webhook bot, Ark Bot by default
        avatar :class:`str`:
            The url of the "profile picture" of the webhook bot, Ark Logo by default
        """
        try:
            if file:
                file = File(file)
            webhook.send(content=message, username=name, avatar_url=avatar, file=file)
        except Exception as e:
            print(f"Failed to post to discord!\n{e}")