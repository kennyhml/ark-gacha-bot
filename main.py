import time
from threading import Thread

from ark import State, config
from pynput import keyboard  # type: ignore[import]

from bot.gacha_bot import GachaBot


def main():
    bot = GachaBot()
    while State.running:
        bot.do_next_task()


def on__key_press(key):
    """Connets inputs from listener thread to their corresponding function"""
    if key == keyboard.Key.f1:
        # make sure bot is not already active
        if not (State.paused or State.running):
            print("Started!")
            State.running = True

            bot = Thread(target=main, daemon=True, name="Main bot Thread")
            bot.start()

    elif key == keyboard.Key.f3:
        if State.running:
            print("Terminated!")
            State.paused = False
            State.running = False

    elif key == keyboard.Key.f5:
        if State.running and not State.paused:
            print("Paused!")
            State.paused = True

        elif State.running and State.paused:
            print("Resumed!")
            State.paused = False


if __name__ == "__main__":
    State.running = False
    State.paused = False

    listener = keyboard.Listener(on_press=on__key_press)
    listener.start()  # start listener thread

    while True:
        time.sleep(1000)