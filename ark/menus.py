import pyautogui as pg

from ark.entities.player import Player
from ark.server import Server
from bot.ark_bot import ArkBot
from ark.exceptions import ServerNotFoundError


class MainMenu(ArkBot):
    """Represents the ark main menu."""

    def is_open(self) -> bool:
        """Checks if the main menu is currently open."""
        return (
            self.locate_template(
                "templates/main_menu_options.png",
                region=(20, 600, 230, 76),
                confidence=0.8,
            )
            is not None
        )

    def player_disconnected(self) -> bool:
        """Checks if the player was disconnected."""
        return (
            self.locate_template(
                "templates/main_menu_accept.png",
                region=(515, 320, 910, 390),
                confidence=0.8,
            )
            is not None
        )

    def open_session_list(self) -> None:
        """Opens the session list."""
        session_list = SessionList()
        while not session_list.is_open():
            self.click_at(117, 528, delay=0.5)
            self.sleep(2)


class SessionList(ArkBot):
    """Represents the ark session list. Responsible for rejoining servers."""

    FILTERS = {"Official Servers": (369, 863), "Favorites": (373, 925)}

    def is_open(self) -> bool:
        """Checks if the session list menu is open"""
        return (
            self.locate_template(
                "templates/session_list.png",
                region=(110, 100, 230, 80),
                confidence=0.8,
            )
            is not None
        )

    def server_found(self) -> bool:
        """Checks if the favorited server has been found"""
        return (
            self.locate_template(
                "templates/server_favorite.png",
                region=(90, 200, 430, 90),
                confidence=0.75,
            )
            is not None
        )

    def refresh(self) -> None:
        """Clicks the refresh button"""
        self.click_at(1229, 941, delay=0.5)

    def join_server(self, server: Server) -> bool:
        """Joins the given server by the servers search name attribute.

        Parameters:
        ----------
        server :class:`Server`:
            The server to join as a Server object.

        Returns:
        ----------
        Whether the server could be joined or not.

        Handles:
        ----------
        `ServerNotFoundError` by returning False
        """
        try:
            self.search_server(server)
        except ServerNotFoundError:
            print("Failed to find the server after 15min!")
            return

        # click join, wait to load in
        self.click_at(990, 943, delay=0.5)
        Player().await_spawned()
        print("Successfully joined the server!")
        return True

    def search_server(self, server: Server) -> None:
        """Searches for the given server, waits for it to pop up.

        Parameters:
        ----------
        server :class:`Server`:
            The server to searcg for as a Server object.
        """
        # click searchbar, search for the server
        self.click_at(616, 143, delay=0.5)
        pg.typewrite(server.search_name, interval=0.01)
        self.press("enter")
        self.sleep(5)

        # attempt to find the server up to 30 times, waiting 30 seconds each time.
        # after each 30 seconds the session list is refreshed
        attempts = 0
        for _ in range(30):
            count = 0
            while not self.server_found():
                self.sleep(1)
                count += 1

                if count > 30:
                    attempts += 1
                    self.refresh()
                    break
            else:
                # server found, click join
                self.click_at(959, 237, delay=0.5)
                return
        raise ServerNotFoundError(f"Failed to find {server.name}!")


class IngameMenu(ArkBot):
    """Represents the ark ingame (escape) menu."""

    def is_open(self) -> bool:
        """Checks if the menu is open."""
        return (
            self.locate_template(
                "templates/resume.png", region=(750, 215, 425, 200), confidence=0.8
            )
            is not None
        )

    def check_reponding(self) -> bool:
        """Checks if the game is responsive by seeing if the escape
        menu comes up when pressing escape, after 60 seconds of unsuccessful
        attempts it will assume the game is not responding.

        Leaves the escape menu in a closed state. Useful for unstucking out of
        not closed inventories or such.
        """
        count = 0
        # escape menu was already open prior to checking
        if self.is_open():
            while self.is_open():
                count += 1
                self.press("esc")
                self.sleep(2)
                if count > 30:
                    return False
            return True

        # escape menu was not yet open
        while not self.is_open():
            count += 1
            self.press("esc")
            self.sleep(2)
            if count > 30:
                return False
        self.press("esc")
        self.sleep(2)
        return True