import pyautogui as pg  # type: ignore[import]

from bot.ark_bot import ArkBot


class Console(ArkBot):
    def is_open(self):
        """Checks if the console is open by matching the black par"""
        return pg.pixelMatchesColor(
            *self.convert_point(976, 1071), (0, 0, 0), tolerance=3
        )

    def open(self):
        """Opens the console by checking for it to open, times out after 10s"""
        c = 0
        while not self.is_open():
            c += 1
            self.press(self.keybinds.console)
            self.sleep(0.2)

            if c > 50:
                raise TimeoutError("Failed to open the console")

    def set_fps(self, fps: str = "10"):
        """Sets the fps to the given value"""
        self.open()

        pg.typewrite(f"t.maxfps {fps}", interval=0.001)
        self.sleep(0.5)
        self.press("enter")

    def set_gamma(self, gamma: str = "5"):
        """Sets gamma to the given value"""
        self.open()

        pg.typewrite(f"gamma {gamma}", interval=0.001)
        self.sleep(0.5)
        self.press("enter")

    def run_required_commands(self):
        """Sets up max fps and gamma with default parameters"""
        self.set_fps()
        self.set_gamma()
