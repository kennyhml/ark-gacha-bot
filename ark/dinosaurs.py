from bot.ark_bot import ArkBot
from ark.inventories import Inventory

from ark.exceptions import DinoNotMountedError


class Dinosaur(ArkBot):
    def __init__(self, entity_name, action_wheel_img) -> None:
        super().__init__()
        self.name = entity_name
        self.inventory = Inventory(entity_name, action_wheel_img)

    def is_mounted(self) -> bool:
        return (
            self.locate_template(
                "templates/stamina_mount.png",
                region=(1880, 53, 31, 44),
                confidence=0.6,
            )
            is not None
        )

    def can_ride(self) -> bool:
        return (
            self.locate_template(
                "templates/ride.png",
                region=(0, 0, 1920, 1080),
                confidence=0.7,
            )
            is not None
        )

    def can_access(self) -> bool:
        return (
            self.locate_template(
                "templates/can_access.png",
                region=(0, 0, 1920, 1080),
                confidence=0.7,
            )
            is not None
        )

    def await_mounted(self) -> bool:
        counter = 0
        while not self.is_mounted():
            self.sleep(0.1)
            if self.inventory.is_open():
                raise DinoNotMountedError(
                    f"Failed to mount {self.name}, accessed inventory instead!"
                    "Please ensure a saddle is equipped."
                )
            counter += 1
            if counter > 130:
                return False
        return True

    def await_dismounted(self) -> bool:
        counter = 0
        while self.is_mounted():
            self.sleep(0.1)
            counter += 1
            if counter > 130:
                return False
        return True

    def mount(self) -> None:
        counter = 0
        while not self.is_mounted():
            self.press(self.keybinds.use)
            if self.await_mounted():
                return
            counter += 1
            if counter >= 4:
                raise DinoNotMountedError(f"Failed to mount {self.name} after 60s!")
        self.sleep(0.5)

    def dismount(self) -> None:
        while self.is_mounted():
            self.press(self.keybinds.use)
            if self.await_dismounted():
                return
                
        self.sleep(0.5)

    def attack(self, button: str) -> None:
        self.click(button)