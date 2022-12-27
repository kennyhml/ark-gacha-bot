import time
from threading import Thread

from pynput import keyboard  # type: ignore[import]

from bot.ark_bot import ArkBot
from bot.gacha_bot import GachaBot


def main():
    bot = GachaBot()

    bot.stations[2].transfer_dedi_wall()

    quit()

    while ArkBot.running:
        bot.do_next_task()


def on__key_press(key):
    """Connets inputs from listener thread to their corresponding function"""

    if key == keyboard.Key.f1:
        # make sure bot is not already active
        if not (ArkBot.paused or ArkBot.running):
            print("Started!")
            ArkBot.running = True

            bot = Thread(target=main, daemon=True, name="Main bot Thread")
            bot.start()
            bot.run
            
    elif key == keyboard.Key.f3:
        if ArkBot.running:
            print("Terminated!")
            ArkBot.paused = False
            ArkBot.running = False

    elif key == keyboard.Key.f5:
        if ArkBot.running and not ArkBot.paused:
            print("Paused!")
            ArkBot.paused = True

        elif ArkBot.running and ArkBot.paused:
            print("Resumed!")
            ArkBot.paused = False


if __name__ == "__main__":
    ArkBot.running = False
    ArkBot.paused = False
    listener = keyboard.Listener(on_press=on__key_press)
    listener.start()  # start listener thread

    while True:
        time.sleep(100000)
