import webbrowser

import psutil  # type: ignore[import]
import pygetwindow  # type: ignore[import]

from ark.console import Console
from ark.menus import IngameMenu, MainMenu, SessionList
from ark.server import Server
from bot.ark_bot import ArkBot


class UnstuckHandler(ArkBot):
    """Handles stuck cases for server crashes, bot errors or game crashes."""

    def __init__(self, server) -> None:
        super().__init__()
        self._main_menu = MainMenu()
        self._session_list = SessionList()
        self._ingame_menu = IngameMenu()
        self._server = server
        self.reconnected = False

    def attempt_fix(self) -> bool:
        """Runs an analysis through different possible problems and attempts
        to fix them upon detection."""

        self.set_foreground()
        if self._ingame_menu.check_reponding():
            return True

        if self.game_crashed():
            print("Analysis: Game is crashed! Restarting...")
            self.press("esc")
            self.sleep(30)
            self.restart()
            self.reconnect()

        elif not self.process_active():
            print("Analysis: Game is fully closed! Restarting...")
            self.restart()
            self.reconnect()
            self.update_boundaries()

        elif self._main_menu.player_disconnected() or self._main_menu.is_open():
            print("Analysis: Player got disconnected! Restarting...")
            self.press("esc")
            self.reconnect()

        return self._ingame_menu.check_reponding()

    def restart(self) -> None:
        """Restarts the game for epic only, waits for the main menu to load.
        Refreshes window boundaries once launched."""
        webbrowser.open_new(
            "com.epicgames.launcher://apps/ark%3A743e47ee84ac49a1a49f4781da70e0d0%3Aaafc587fbf654758802c8e41e4fb3255?action=launch&silent=true"
        )
        while not self._main_menu.is_open():
            self.sleep(1)
        self.update_boundaries()

    def reconnect(self) -> None:
        """Reconnects to the server."""
        self.reconnected = True
        self._main_menu.open_session_list()
        self._session_list.join_server(self._server)
        self.sleep(30)
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
