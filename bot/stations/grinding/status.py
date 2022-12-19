from enum import Enum

class Status(str, Enum):
    WAITING_FOR_ITEMS = "Waiting for items"
    QUEUING_ELECTRONICS = "Queuing electronics"
    AWAITING_CRAFT = "Awaiting craft"