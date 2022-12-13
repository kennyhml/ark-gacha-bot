"""
A module containing all exceptions raised in the ark API classes,
Sorted after situation
"""
class BotTerminatedError(Exception):
    """Raised when the bot has been termined by user or critical error"""

class InventoryNotAccessibleError(Exception):
    """Raised when the inventory cannot be accessed."""


class InventoryNotClosableError(Exception):
    """Raised when the inventory cannot be closed"""


class ReceivingRemoveInventoryTimeout(Exception):
    """Raised when the 'Receiving Remote Inventory' text does not disappear."""


class NoItemsAddedError(Exception):
    """Raised when items were not added to the inventory if expected."""

class NoItemsDepositedError(Exception):
    """Raised when the 'X items deposited.' message does not appear."""


class NoGasolineError(Exception):
    """Raised when a structure can not be turned on"""


class TekPodNotAccessibleError(Exception):
    """Raised when the tek pod cannot be accessed."""


class BedNotAccessibleError(Exception):
    """Raised when the bed map could not be opened."""


class PlayerDidntTravelError(Exception):
    """Raised when the travel screen could not be detected."""

class LogsNotOpenedError(Exception):
    """Raised when the logs could not be opened"""

class InvalidStationError(Exception):
    """Raised when the given station to turn to doesnt exist"""

class DedisNotDetermined(Exception):
    """Raised when one or more dedis could not be determined whatsoever."""

class ServerNotFoundError(Exception):
    """Raised when a server could not be found after 15 minutes."""

class DediNotInRangeError(Exception):
    """Raised when the dedi deposit text could not be detected"""

class NoItemsLeftError(Exception):
    """Raised when there is no berries left to deposit"""

class DinoNotMountedError(Exception):
    """Raised when a dino cannot be mounted, either because it does not
    have a saddle, or because its not close enough."""