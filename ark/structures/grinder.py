



from ark.structures.structure import Structure
from ark.exceptions import NoGasolineError

class Grinder(Structure):
    """Represents the grinder inventory in ark.

    Is able to be turned on and off and grind all.
    """

    def __init__(self) -> None:
        super().__init__("Grinder", "grinder")

    def can_turn_on(self) -> bool:
        """Checks if the grinder can be turned on"""
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
        """Checks if the grinder is already turned on"""
        return (
            self.locate_template(
                "templates/turn_off.png",
                region=(740, 570, 444, 140),
                confidence=0.85,
                grayscale=True,
            )
            is not None
        )

    def can_grind(self) -> bool:
        """Checks if the grinder can grind"""
        return (
            self.locate_template(
                "templates/grind_all_items.png",
                region=(740, 570, 444, 140),
                confidence=0.85,
            )
            is not None
        )

    def turn_on(self) -> None:
        """Turns the grinder on, assumes it is already open.

        Raises a `NoGasolineError` if it is unable to do so.
        """
        if self.is_turned_on():
            print("Grinder is already on!")
            return

        if not self.can_turn_on():
            raise NoGasolineError

        while self.can_turn_on():
            self.click_at(964, 615, delay=0.3)
            self.sleep(1)

        print("Grinder has been turned on!")
        self.sleep(1)

    def turn_off(self) -> None:
        """Turns the grinder off, assumes it is already open."""
        if self.can_turn_on():
            print("Grinder is already off!")
            return

        while self.is_turned_on():
            self.click_at(964, 615, delay=0.3)
            self.sleep(1)
        print("Grinder has been turned off!")

    def grind_all(self) -> bool:
        """Presses the grind all button if it is available.
        Returns whether items got grinded or not.
        """
        if not self.can_grind():
            print("There is no items to grind!")
            return False

        self.click_at(969, 663, delay=0.3)
        return True