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
