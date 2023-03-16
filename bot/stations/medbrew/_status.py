from enum import Enum

class Status(str, Enum):
    WAITING_FOR_BERRIES = "Waiting for berries"
    CRAFTING_NARCOTICS = "Crafting narcotics"
    COOKING_MEDBREWS = "Cooking medbrews"