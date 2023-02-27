import time
import webbrowser
from typing import Literal

import psutil  # type: ignore[import]
import pyautogui  # type: ignore[import]
import pygetwindow  # type: ignore[import]
from ark import (ArkWindow, Console, EscapeMenu, MainMenu, Server, SessionList,
                 exceptions, Player)
from ark.server import server_query

from .webhooks import InfoWebhook
from discord import Embed

class Unstucking:
    """Handles stuck cases for server crashes, bot errors or game crashes."""

    def __init__(
        self,
        server: Server,
        player: Player,
        launcher: Literal["steam", "epic"],
        info_webhook: InfoWebhook,
    ) -> None:
        self._main_menu = MainMenu()
        self._session_list = SessionList()
        self._escape_menu = EscapeMenu()
        self._server = server
        self._launcher = launcher
        self._player = player
        self.webhook = info_webhook
        self.reconnected = False
        self.screen = ArkWindow()

    def unstuck(self) -> None:
        """Runs an analysis through different possible problems and attempts
        to fix them upon detection."""
        try:
            self._escape_menu.open()
            self._escape_menu.click("right")
            self._escape_menu.close()
        except exceptions.InterfaceError:
            print("Game not responding..")
        else:
            return

        if self.game_crashed():
            self.webhook.send_error("Unstucking", "Game Crashed!", mention=True)
            pyautogui.press("esc")
            time.sleep(30)
            self.restart()
            self.reconnect()
        
        elif not self.process_active():
            self.webhook.send_error("Unstucking", "Game Crashed!", mention=True)
            self.restart()
            self.reconnect()
        
        elif self._main_menu.player_disconnected() or self._main_menu.is_open():
            self.webhook.send_error("Unstucking", "Disconnected!", mention=True)
            pyautogui.press("esc")
            self.reconnect()
    
    def restart(self) -> None:
        """Restarts the game for epic only, waits for the main menu to load.
        Refreshes window boundaries once launched."""
        if self._launcher == "epic":
            webbrowser.open_new(
                "com.epicgames.launcher://apps/ark%3A743e47ee84ac49a1a49f4781da70e0d0%3Aaafc587fbf654758802c8e41e4fb3255?action=launch&silent=true"
            )
        else:
            webbrowser.open_new("steam://rungameid/346110")
        while not self._main_menu.is_open():
            time.sleep(1)

    def reconnect(self) -> None:
        """Reconnects to the server."""
        self.reconnected = True

        self._session_list.open()
        server_query.query(self._server)
        if self._server.status == "Down":
            self.webhook.send_error(
                "Unstucking",
                self.screen.grab_screen((0, 0, 1920, 1080)),
                ConnectionError(f"{self._server.name} has crashed!"),
                mention=True,
            )

        while self._server.status == "Down":
            server_query.query(self._server)
            time.sleep(15)

        self._session_list.connect(self._server)
        self._player.spawn_in()
        Console().set_gamma()

    def process_active(self) -> bool:
        """Checks if ark is an active process"""
        for process in psutil.process_iter():
            if process.name() == "ShooterGame.exe":
                return True
        return False

    def game_crashed(self) -> bool:
        """Checks if ark has crashed by grabbing the fatal error window."""
        try:
            return pygetwindow.getWindowsWithTitle("The UE4-ShooterGame")[0] is not None
        except IndexError:
            return False