


from ark.structures.structure import Structure
from ark.exceptions import NoGasolineError

class IndustrialForge(Structure):
    """Represents the Industrial Forge inventory in ark.

    Is able to be turned on and off.
    """

    def __init__(self) -> None:
        super().__init__("Industrial Forge", "indi_forge")

    def can_turn_on(self) -> bool:
        """Checks if the Industrial Forge can be turned on"""
        return (
            self.locate_template(
                "templates/turn_on.png",
                region=(740, 570, 444, 140),
                confidence=0.85,
                grayscale=True,
            )
            is not None
        )

    def is_turned_on(self) -> bool:
        """Checks if the Industrial Forge is already turned on"""
        return (
            self.locate_template(
                "templates/turn_off.png",
                region=(740, 570, 444, 140),
                confidence=0.85,
                grayscale=True,
            )
            is not None
        )

    def turn_on(self) -> None:
        """Turns the Industrial Forge on, assumes it is already open.

        Raises a `NoGasolineError` if it is unable to do so.
        """
        if self.is_turned_on():
            print("Industrial Forge is already on!")
            return

        if not self.can_turn_on():
            raise NoGasolineError

        while self.can_turn_on():
            self.click_at(964, 615, delay=0.3)
            self.sleep(1)

        print("Industrial Forge has been turned on!")
        self.sleep(1)

    def turn_off(self) -> None:
        """Turns the Industrial Forge off, assumes it is already open."""
        if self.can_turn_on():
            print("Industrial Forge is already off!")
            return

        while self.is_turned_on():
            self.click_at(964, 615, delay=0.3)
            self.sleep(1)
        print("Industrial Forge has been turned off!")