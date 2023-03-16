import json
import time

from ark import Player, config, TribeLog

from ...webhooks import TribeLogWebhook, InfoWebhook
from .medbrew_station import MedbrewStation
from ._settings import MedbrewStationSettings

with open("settings/settings.json") as f:
    config.ARK_PATH = json.load(f)["main"]["ark_path"]

def main():
    with open("settings/settings.json") as f:
        data = json.load(f)

    name = input("Name of the station to calibrate? INCLUDING NUMBER! For example: brew00\n")

    for s in range(5, -1, -1):
        print(f"Beginning calibration in {s}...", end="\r")
        time.sleep(1)

    player = Player(100, 100, 100, 100)

    grinding = MedbrewStation(
        name,
        player,
        TribeLogWebhook(TribeLog(), data["discord"]["webhook_alert"], data["discord"]["webhook_logs"]),
        InfoWebhook(data["discord"]["webhook_gacha"], ""),
        MedbrewStationSettings.load()
    )

    grinding._spawn_at(grinding.narcoberry_bed)
    for idx, (turn, val) in enumerate(grinding.narco_bench_turns, start=1):
        turn(val, delay=1)
        print(f"Looking at chembench {idx}")
        player.sleep(2)

    grinding._spawn_at(grinding.chembench_bed)

    for turn, val in grinding.gasoline_turns:
        turn(val, delay=1)
        print(f"Looking at gasoline")
        player.sleep(2)

    for turn, val in reversed(grinding.gasoline_turns):
        turn(val * -1, delay=1)

    for idx, (turn, val) in enumerate(grinding.meat_bench_turns, start=1):
        turn(val, delay=1)
        print(f"Looking at chembench {idx}")
        player.sleep(2)
    
    for idx, (turn, val) in enumerate(grinding.cooker_turns, start=1):
        turn(val, delay=1)
        print(f"Looking at cooker {idx}")
        player.sleep(2)

    grinding._spawn_at(grinding.tintoberry_bed)
    for idx, (turn, val) in enumerate(grinding.cooker_turns_2, start=1):
        turn(val, delay=1)
        print(f"Looking at cooker {idx}")
        player.sleep(2)


if __name__ == "__main__":
    main()
