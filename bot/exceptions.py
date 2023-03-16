class StationError(Exception):
    """Raised when something went wrong on a station"""


class NoCrystalAddedError(StationError):
    """Raised when no crystal is added at the crystal station"""

class ConfigError(Exception):
    """Raised when a setting was incorrect."""

class MissingPelletsError(Exception):
    """Raised when pellets are missing"""

class StationNotReadyError(Exception):
    """Raised when a station was not actually ready yet."""