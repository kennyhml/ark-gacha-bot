import time
from threading import Thread

from pynput import keyboard  # type: ignore[import]

from bot.ark_bot import ArkBot
from bot.gacha_bot import GachaBot

from gui.gachaUI import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
import sys
import json
import os 

def main():
    bot = GachaBot()
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

def save_settings():
    settings = {}
    "takes information from ui and writes it to settings json file"
    settings["account_name"] = ui.account_name.toPlainText()
    settings["bed_position"] = [int(ui.bed_x.text()), int(ui.bed_y.text())]
    settings["crystal_prefix"] = ui.crystal_prefix.toPlainText()
    settings["crystal_beds"] = int(ui.crystal_beds.text())
    settings["seed_prefix"] = ui.seed_prefix.toPlainText()
    settings["seed_beds"] = int(ui.seed_beds.text())
    settings["berry_prefix"] = ui.berry_prefix.toPlainText()
    settings["berry_beds"] = int(ui.berry_beds.text())
    settings["meat_prefix"] = ui.meat_prefix.toPlainText()
    settings["meat_beds"] = int(ui.meat_beds.text())
    settings["crystal_interval"] = int(ui.crystal_interval.text())
    settings["stryder_depositing"] = ui.stryder_depositing.isChecked()
    settings["drop_items"] = ui.drop_items.toPlainText().split(",")
    settings["keep_items"] = ui.keep_items.toPlainText().split(",")
    settings["game_launcher"] = ui.game_launcher.currentText()
    settings["server_name"] = ui.server_name.toPlainText()
    settings["server_search"] = ui.server_search.toPlainText()
    settings["pod_name"] = ui.pod_name.toPlainText()
    settings["webhook_alert"] = ui.webhook_alert.toPlainText()
    settings["webhook_gacha"] = ui.webhook_gacha.toPlainText()
    settings["webhook_logs"] = ui.webhook_logs.toPlainText()

    with open("settings/settings.json", "w") as f:
        f.write(json.dumps(settings, indent=4, sort_keys=True)) 

    keybinds = {}
    "takes information from ui and writes it to keybinds json file"
    keybinds["console"] = ui.console.toPlainText()
    keybinds["crouch"] = ui.crouch.toPlainText()
    keybinds["drop"] = ui.drop.toPlainText()
    keybinds["hotbar_0"] = ui.hotbar_0.toPlainText()
    keybinds["hotbar_1"] = ui.hotbar_1.toPlainText()
    keybinds["hotbar_2"] = ui.hotbar_2.toPlainText()
    keybinds["hotbar_3"] = ui.hotbar_3.toPlainText()
    keybinds["hotbar_4"] = ui.hotbar_4.toPlainText()
    keybinds["hotbar_5"] = ui.hotbar_5.toPlainText()
    keybinds["hotbar_6"] = ui.hotbar_6.toPlainText()
    keybinds["hotbar_7"] = ui.hotbar_7.toPlainText()
    keybinds["hotbar_8"] = ui.hotbar_8.toPlainText()
    keybinds["hotbar_9"] = ui.hotbar_9.toPlainText()
    keybinds["inventory"] = ui.inventory.toPlainText()
    keybinds["prone"] = ui.prone.toPlainText()
    keybinds["target_inventory"] = ui.target_inventory.toPlainText()
    keybinds["toggle_hud"] = ui.toggle_hud.toPlainText()
    keybinds["logs"] = ui.logs.toPlainText()
    keybinds["use"] = ui.use.toPlainText()

    with open("settings/keybinds.json", "w") as f:
        f.write(json.dumps(keybinds, indent=4, sort_keys=True))

def load_settings():
    try:
        if not os.path.exists("settings/settings.json"):
            settings = {}
            with open("settings/settings.json", "w") as f:
                f.write(json.dumps(settings, indent=4, sort_keys=True))

        with open('settings/settings.json') as json_file:
            settings = json.load(json_file)

        if not os.path.exists("settings/keybinds.json"):
            keybinds = {}
            with open("settings/keybinds.json", "w") as f:
                f.write(json.dumps(keybinds, indent=4, sort_keys=True))

        with open('settings/keybinds.json') as json_file:
            keybinds = json.load(json_file)

        update_ui(settings, keybinds) #will update ui visuals to display the settings from settings files
    except Exception as e:
        print("ERROR: load_settings()")
        print(e)

def update_ui(settings, keybinds):
    "sets ui values to match settings file values"
    ui.account_name.setPlainText(settings["account_name"])
    ui.crystal_prefix.setPlainText(settings["crystal_prefix"])
    ui.seed_prefix.setPlainText(settings["seed_prefix"])
    ui.berry_prefix.setPlainText(settings["berry_prefix"])
    ui.meat_prefix.setPlainText(settings["meat_prefix"])
    ui.server_name.setPlainText(settings["server_name"])
    ui.server_search.setPlainText(settings["server_search"])
    ui.pod_name.setPlainText(settings["pod_name"])
    ui.webhook_alert.setPlainText(settings["webhook_alert"])
    ui.webhook_gacha.setPlainText(settings["webhook_gacha"])
    ui.webhook_logs.setPlainText(settings["webhook_logs"])
    ui.bed_x.setValue(int(settings["bed_position"][0]))
    ui.bed_y.setValue(int(settings["bed_position"][1]))
    ui.crystal_beds.setValue(int(settings["crystal_beds"]))
    ui.seed_beds.setValue(int(settings["seed_beds"]))
    ui.berry_beds.setValue(int(settings["berry_beds"]))
    ui.meat_beds.setValue(int(settings["meat_beds"]))
    ui.crystal_interval.setValue(int(settings["crystal_interval"]))
    ui.stryder_depositing.setChecked(settings["stryder_depositing"])
    ui.drop_items.setPlainText(",".join(settings["drop_items"]))
    ui.keep_items.setPlainText(",".join(settings["keep_items"]))

    ui.console.setPlainText(keybinds["console"])
    ui.crouch.setPlainText(keybinds["crouch"])
    ui.drop.setPlainText(keybinds["drop"])
    ui.inventory.setPlainText(keybinds["inventory"])
    ui.prone.setPlainText(keybinds["prone"])
    ui.target_inventory.setPlainText(keybinds["target_inventory"])
    ui.toggle_hud.setPlainText(keybinds["toggle_hud"])
    ui.logs.setPlainText(keybinds["logs"])
    ui.use.setPlainText(keybinds["use"])
    ui.hotbar_0.setPlainText(keybinds["hotbar_0"])
    ui.hotbar_1.setPlainText(keybinds["hotbar_1"])
    ui.hotbar_2.setPlainText(keybinds["hotbar_2"])
    ui.hotbar_3.setPlainText(keybinds["hotbar_3"])
    ui.hotbar_4.setPlainText(keybinds["hotbar_4"])
    ui.hotbar_5.setPlainText(keybinds["hotbar_5"])
    ui.hotbar_6.setPlainText(keybinds["hotbar_6"])
    ui.hotbar_7.setPlainText(keybinds["hotbar_7"])
    ui.hotbar_8.setPlainText(keybinds["hotbar_8"])
    ui.hotbar_9.setPlainText(keybinds["hotbar_9"])

def connect_text_changes_to_save():
    "Binds ui changes to call save_settings function"

    ui.account_name.textChanged.connect(save_settings)
    ui.bed_x.textChanged.connect(save_settings)
    ui.bed_y.textChanged.connect(save_settings)
    ui.crystal_prefix.textChanged.connect(save_settings)
    ui.crystal_beds.textChanged.connect(save_settings)
    ui.seed_prefix.textChanged.connect(save_settings)
    ui.seed_beds.textChanged.connect(save_settings)
    ui.berry_prefix.textChanged.connect(save_settings)
    ui.berry_beds.textChanged.connect(save_settings)
    ui.meat_prefix.textChanged.connect(save_settings)
    ui.meat_beds.textChanged.connect(save_settings)
    ui.crystal_interval.textChanged.connect(save_settings)
    ui.stryder_depositing.stateChanged.connect(save_settings)
    ui.drop_items.textChanged.connect(save_settings)
    ui.game_launcher.currentIndexChanged.connect(save_settings)
    ui.keep_items.textChanged.connect(save_settings)
    ui.server_name.textChanged.connect(save_settings)
    ui.server_search.textChanged.connect(save_settings)
    ui.pod_name.textChanged.connect(save_settings)
    ui.webhook_alert.textChanged.connect(save_settings)
    ui.webhook_gacha.textChanged.connect(save_settings)
    ui.webhook_logs.textChanged.connect(save_settings)

    ui.console.textChanged.connect(save_settings)
    ui.crouch.textChanged.connect(save_settings)
    ui.drop.textChanged.connect(save_settings)
    ui.hotbar_0.textChanged.connect(save_settings)
    ui.hotbar_1.textChanged.connect(save_settings)
    ui.hotbar_2.textChanged.connect(save_settings)
    ui.hotbar_3.textChanged.connect(save_settings)
    ui.hotbar_4.textChanged.connect(save_settings)
    ui.hotbar_5.textChanged.connect(save_settings)
    ui.hotbar_6.textChanged.connect(save_settings)
    ui.hotbar_7.textChanged.connect(save_settings)
    ui.hotbar_8.textChanged.connect(save_settings)
    ui.hotbar_9.textChanged.connect(save_settings)
    ui.inventory.textChanged.connect(save_settings)
    ui.prone.textChanged.connect(save_settings)
    ui.target_inventory.textChanged.connect(save_settings)
    ui.toggle_hud.textChanged.connect(save_settings)
    ui.logs.textChanged.connect(save_settings)
    ui.use.textChanged.connect(save_settings)

if __name__ == "__main__":
    ArkBot.running = False
    ArkBot.paused = False
    listener = keyboard.Listener(on_press=on__key_press)
    listener.start()  # start listener thread

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow) #loads ui from generated ui file

    load_settings()#loads settings froms settings files
    connect_text_changes_to_save()

    MainWindow.show() #displays ui
    sys.exit(app.exec_())
