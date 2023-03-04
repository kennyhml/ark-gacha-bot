import json
import time

from ark import Player, TribeLog, config

from .grinding_station import GrindingStation

import json

with open("settings/settings.json") as f:
    config.ARK_PATH = json.load(f)["main"]["ark_path"]


def main():

    do_turns = input("Do you want to calibrate the turns? y/n\n>>>").lower() == "y"
    do_dedis = input("Do you want to calibrate the dedi ocr? y/n\n>>>").lower() == "y"
    do_dedi_transfer = (
        input("Do you want to calibrate dedi_transfer? y/n\n>>>").lower() == "y"
    )
    do_vault_transfer = (
        input("Do you want to calibrate vault_transfer? y/n\n>>>").lower() == "y"
    )

    with open("settings/settings.json") as f:
        data = json.load(f)

    for s in range(5, -1, -1):
        print(f"Beginning calibration in {s}...", end="\r")
        time.sleep(1)

    player = Player(100, 100, 100, 100)
    grinding = GrindingStation(
        player,
        TribeLog(data["discord"]["webhook_alert"], data["discord"]["webhook_logs"], ""),
        "",
    )

    if do_turns:
        print("---------------Starting calibration for turns!---------------")
        grinding.spawn()
        player.spawn_in()

        for station in grinding.STATION_MAPPING:
            print(f"Turning to {station}...")
            grinding.turn_to(station)

            print(f"Should now be looking at {station}")
            time.sleep(2)

        print("Finished station calibration. Please ensure every turn was correct.\n")

    if do_dedis:
        print(
            "---------------Starting calibration for dedis!---------------\n"
            "For this step, please make sure that there is a valid amount of items in the dedis.\n"
            "A valid range is this:\n"
            "Pearls: 6000 - 60000\n"
            "Paste: 7000 - 180000\n"
            "Electronics: 800 - 10000\n"
            "Metal Ingot: 7000 - 60000\n"
            "NOTE! During this calibration, an open-cv window will pop up showing the result.\n"
            "It will NOT proceed until you close the window for each dedi!"
        )
        try:
            grinding.determine_materials(debug=True)
        except AttributeError:
            # the error from passing webhook as a string, silence
            pass

    if do_dedi_transfer:
        grinding._transfer_dedi_wall()
        print("Finished calibrating dedi transfer.")

    if do_vault_transfer:
        grinding._transfer_vault()
        print("Finished calibrating vault transfer.")

    print("Calibration complete.")


if __name__ == "__main__":
    main()
