from enum import Enum, auto

class Status(str, Enum):
    WAITING_FOR_WOOD = "Waiting for wood"
    COOKING_WOOD = "Cooking wood"
    WAITING_FOR_GUNPOWDER = "Waiting for gunpowder"
    WAITING_FOR_ARB = "Waiting for ARB"