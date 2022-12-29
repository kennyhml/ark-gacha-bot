""""
Part of the Ark API for tribelogs, contains common mistakes you want to replace
with a corrected version as well as what terms to ignore (C4, Baby...).

Just read (and use your brain).
"""


# common tesseract mistakes to account for in any tribelog messages
# could use regex for it to make it more powerful
CONTENTS_MAPPING = {
    "{": "(",
    "}": ")",
    "[": "(",
    "]": ")",
    "((": "(",
    "))": ")",
    "Owll": "Owl)",
    "\n": " ",
    "!!": "!",
    "Lvi": "Lvl",
    "Lyi": "Lvl",
    "Gaby": "Baby",
    "destroved": "destroyed",
    "destroyedl": "destroyed!",
    "destroyedl!": "destroyed!",
    "destrayed!": "destroyed!",
    "destraved": "destroyed",
    "Giaanotosaurus": "Giganotosaurus",
    "Giganotosaurusl": "Giganotosaurus)",
    "Giganotosaurusi": "Giganotosaurus)",
    "Large Gear Trap": "Large Bear Trap",
    "C4 Charae": "C4 Charge",
    "C4 Charce": "C4 Charge",
    "C4& Charae": "C4 Charge",
    "C4 Charace": "C4 Charge",
    "C4 Chareae": "C4 Charge",
    "(Pin Coded!": "(Pin Coded)",
    "(Pin Codedl": "(Pin Coded)",
    "tExo": "(Exo",
    "”": "''",
    "“": "'",
    '"': "'",
    "‘": "'",
    "’": "'",
    "''": "'",
    "hiled": "killed",
    "hilied": "killed",
    "Dcorframe": "Doorframe",
    "Ccorframe": "Doorframe",
    "Doaorframe": "Doorframe",
    "Doarframe": "Doorframe",
    "Ceilina": "Ceiling",
    "Ficor": "Floor",
    "iTek Turret!": "(Tek Turret)",
    "iTek Turret": "(Tek Turret",
    " Tek Turreti": " (Tek Turret)",
    "(Tek Turret!": "(Tek Turret)",
    " Tek Turret)": " (Tek Turret)",
    "fCarbonemvsl": "(Carbonemys)",
    "Carbonemvs": "Carbonemys",
    "(Carbonemysl!": "(Carbonemys)!",
    "iCarbonemysl": "(Carbonemys)",
    "iCarbonemysi": "(Carbonemys)",
    "(Shadowmane!": "(Shadowmane)!",
    "Desmadus": "Desmodus",
    "Desmoadus": "Desmodus",
    "(€lonel": "[CLONE]",
    "Liahtnina": "Lightning",
    "tLightning": "(Lightning",
    "Wvvern": "Wyvern",
    "Wyvern!": "Wyvern!)",
    "fLi": "(Li",
    "ernl": "ern)",
    "Fiardhawk": "Fjordhawk",
    "fF": "(F",
    "wki": "wk)",
    "iTek": "(Tek",
    "iTribe": "(Tribe",
    "i!": ")!",
    "saurus!": "saurus)!",
    "(Fin": "(Pin",
    "Caded": "Coded",
    "Codedl": "Coded)",
    "Daeedon": "Daeodon",
    "Daeodon!": "Daeodon)",
    "Heavv": "Heavy",
    "fHeavy": "(Heavy",
    "Astradelphis": "Astrodelphis",
    "Astredelphis": "Astrodelphis",
    "fAstra": "(Astra",
    "Astrodelphisi": "Astrodelphis)",
    "Vetonasaur": "Velonasaur",
    "saurl": "saur)",
    "Preranodon": "Pteranodon",
    "Preranodon!": "Pteranodon)",
    "iDesmodus": "(Desmodus",
    "R - ": "R-",
    "R- ": "R-",
    "R -": "R-",
    "IR-": "(R-",
    "iTribe": "Tribe",
    "i(": "(",
    "!)": ")",
    "fExo": "(Exo",
    "Exo-Mete": "Exo-Mek",
    "Exo-Met": "Exo-Mek",
}

# RGB to denoise with if the templates are located in the tribelog message
DENOISE_MAPPING: dict[tuple[int, int, int], str | list] = {
    (255, 0, 0): [
        "templates/tribelog_red_your.png",
        "templates/tribelog_enemy_destroyed.png",
    ],
    (208, 3, 211): "templates/tribelog_purple_your.png",
    (158, 76, 76): "templates/tribelog_sensor.png",
}

# Denoise RGB indicating a certain tribelog event
EVENT_MAPPING: dict[tuple, str] = {
    (255, 0, 0): "Something destroyed!",
    (208, 3, 211): "Something killed!",
    (158, 76, 76): "Tek Sensor triggered!",
}

# common mistakes to replace in the daytime OCR
DAYTIME_MAPPING: dict[str, str] = {
    "|": "",
    "I": "1",
    "v": "y",
    "O": "0",
    ".": ",",
    "l": "1",
    "i": "1",
    "S": "5",
    "B": "8",
    "Dayy": "Day",
    ";": "",
}

# terms to prevent alerting for
INGORED_TERMS: list[str] = ["C4", "Baby"]