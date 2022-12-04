import psutil
import pygetwindow

from ark.menus import MainMenu, SessionList, IngameMenu
from ark.server import Server
from bot.ark_bot import ArkBot


class UnstuckHandler(ArkBot):
    def __init__(self) -> None:
        super().__init__()
        self._main_menu = MainMenu()
        self._session_list = SessionList()
        self._ingame_menu = IngameMenu()
        self._server = Server("47", "s47", "TheCenter")

    def attempt_fix(self) -> None:

        if self.game_crashed():
            # restart
            return

        if not self.process_active():
            # fatal error already closed somehow, game fully closed
            # restart
            return

        if self._main_menu.player_disconnected() or self._main_menu.is_open():
            print("Disconnected!")
            self.press("esc")
            self.reconnect()
            return

        print("Got stuck in some menu?")
        self.game_responding()
        # could also have knocked out or been moved away from a
        # bed, gonna have to wait to die :(

    def reconnect(self) -> None:
        self._main_menu.open_session_list()
        self._session_list.join_server(self._server)

    def game_responding(self) -> bool:
        """Checks if the game is responsive by seeing if the escape
        menu comes up when pressing escape, after 60 seconds of unsuccessful
        attempts it will assume the game is not responding.

        Leaves the escape menu in a closed state.
        """
        count = 0

        if self._ingame_menu.is_open():
            while self._ingame_menu.is_open():
                count += 1
                self.press("esc")
                self.sleep(2)
                if count > 30:
                    return False
            return True

        while not self._ingame_menu.is_open():
            count += 1
            self.press("esc")
            self.sleep(2)
            if count > 30:
                return False
        self.press("esc")
        self.sleep(2)
        return True

    def process_active(self) -> bool:
        """Checks if ark is an active process"""
        for process in psutil.process_iter():

            if process.name() == "ShooterGame.exe":
                return True

    def game_crashed(self) -> bool:
        """Checks if ark has crashed by grabbing the fatal error window."""
        try:
            return pygetwindow.getWindowsWithTitle("The UE4-ShooterGame")[0] is not None
        except IndexError:
            return False
