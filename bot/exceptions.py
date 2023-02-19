class StationError(Exception):
    """Raised when something went wrong on a station"""


class NoCrystalAddedError(StationError):
    """Raised when no crystal is added at the crystal station"""