from enum import Enum

class Status(str, Enum):
    WAITING_FOR_ITEMS = "Waiting for items"
    CRAFTING_SUBCOMPONENTS = "Queuing subcomponents"
    AWAITING_CRAFT = "Awaiting craft"
    AWAITING_EVALUTION = "Awaiting evaluation"
    AWAITING_PICKUP = "Awaiting pickup"