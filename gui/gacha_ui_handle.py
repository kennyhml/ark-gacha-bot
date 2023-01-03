import json
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

import gui.resources
from gui.gachaUI import Ui_MainWindow

class MainUi(QMainWindow, Ui_MainWindow):
    """Main ui handle, inherits widget data from pyside created UI_MainWindow."""

    def __init__(self) -> None:
        self._app = QApplication([])
        self._main_win = QtWidgets.QMainWindow()
        super().__init__()
        self.setupUi(self._main_win)
        self.load_settings()
        self.populate_ui()
        self.connect_text_changes_to_save()

    def display(self):
        """Displays the ui"""
        self._main_win.show()
        self._main_win.setWindowTitle(f"Ling Ling")
        sys.exit(self._app.exec())

    def load_settings(self):
        """Attempts to load the settings"""
        assert all(
            os.path.exists(f"settings/{file}") for file in {"keybinds.json", "settings.json"}
        ), "Your config files are missing, please redownload them."

        try:

            with open("settings/keybinds.json") as json_file:
                self.keybinds = json.load(json_file)

            with open("settings/settings.json") as json_file:
                self.settings = json.load(json_file)

        except Exception as e:
            print(f"Critical error loading config!\n{e}")

    def populate_ui(self) -> None:
        """Populates the widgets with the saved values.

        Considering using `get()` with default values instead.
        """
        self.account_name.setPlainText(self.settings["account_name"])
        self.crystal_prefix.setPlainText(self.settings["crystal_prefix"])
        self.seed_prefix.setPlainText(self.settings["seed_prefix"])
        self.berry_prefix.setPlainText(self.settings["berry_prefix"])
        self.meat_prefix.setPlainText(self.settings["meat_prefix"])
        self.server_name.setPlainText(self.settings["server_name"])
        self.server_search.setPlainText(self.settings["server_search"])
        self.pod_name.setPlainText(self.settings["pod_name"])
        self.webhook_alert.setPlainText(self.settings["webhook_alert"])
        self.webhook_gacha.setPlainText(self.settings["webhook_gacha"])
        self.webhook_logs.setPlainText(self.settings["webhook_logs"])
        self.bed_x.setValue(int(self.settings["bed_position"][0]))
        self.bed_y.setValue(int(self.settings["bed_position"][1]))
        self.crystal_beds.setValue(int(self.settings["crystal_beds"]))
        self.seed_beds.setValue(int(self.settings["seed_beds"]))
        self.berry_beds.setValue(int(self.settings["berry_beds"]))
        self.meat_beds.setValue(int(self.settings["meat_beds"]))
        self.crystal_interval.setValue(int(self.settings["crystal_interval"]))
        self.stryder_depositing.setChecked(self.settings["stryder_depositing"])
        self.drop_items.setPlainText(",".join(self.settings["drop_items"]))
        self.keep_items.setPlainText(",".join(self.settings["keep_items"]))
        self.console.setPlainText(self.keybinds["console"])
        self.crouch.setPlainText(self.keybinds["crouch"])
        self.drop.setPlainText(self.keybinds["drop"])
        self.inventory.setPlainText(self.keybinds["inventory"])
        self.prone.setPlainText(self.keybinds["prone"])
        self.target_inventory.setPlainText(self.keybinds["target_inventory"])
        self.toggle_hud.setPlainText(self.keybinds["toggle_hud"])
        self.logs.setPlainText(self.keybinds["logs"])
        self.use.setPlainText(self.keybinds["use"])
        self.hotbar_0.setPlainText(self.keybinds["hotbar_0"])
        self.hotbar_1.setPlainText(self.keybinds["hotbar_1"])
        self.hotbar_2.setPlainText(self.keybinds["hotbar_2"])
        self.hotbar_3.setPlainText(self.keybinds["hotbar_3"])
        self.hotbar_4.setPlainText(self.keybinds["hotbar_4"])
        self.hotbar_5.setPlainText(self.keybinds["hotbar_5"])
        self.hotbar_6.setPlainText(self.keybinds["hotbar_6"])
        self.hotbar_7.setPlainText(self.keybinds["hotbar_7"])
        self.hotbar_8.setPlainText(self.keybinds["hotbar_8"])
        self.hotbar_9.setPlainText(self.keybinds["hotbar_9"])

    def connect_text_changes_to_save(self):
        """Adds the callback functions to the widgets connect method."""

        self.account_name.textChanged.connect(self.save_settings)
        self.bed_x.textChanged.connect(self.save_settings)
        self.bed_y.textChanged.connect(self.save_settings)
        self.crystal_prefix.textChanged.connect(self.save_settings)
        self.crystal_beds.textChanged.connect(self.save_settings)
        self.seed_prefix.textChanged.connect(self.save_settings)
        self.seed_beds.textChanged.connect(self.save_settings)
        self.berry_prefix.textChanged.connect(self.save_settings)
        self.berry_beds.textChanged.connect(self.save_settings)
        self.meat_prefix.textChanged.connect(self.save_settings)
        self.meat_beds.textChanged.connect(self.save_settings)
        self.crystal_interval.textChanged.connect(self.save_settings)
        self.stryder_depositing.stateChanged.connect(self.save_settings)
        self.drop_items.textChanged.connect(self.save_settings)
        self.game_launcher.currentIndexChanged.connect(self.save_settings)
        self.keep_items.textChanged.connect(self.save_settings)
        self.server_name.textChanged.connect(self.save_settings)
        self.server_search.textChanged.connect(self.save_settings)
        self.pod_name.textChanged.connect(self.save_settings)
        self.webhook_alert.textChanged.connect(self.save_settings)
        self.webhook_gacha.textChanged.connect(self.save_settings)
        self.webhook_logs.textChanged.connect(self.save_settings)
        self.console.textChanged.connect(self.save_settings)
        self.crouch.textChanged.connect(self.save_settings)
        self.drop.textChanged.connect(self.save_settings)
        self.hotbar_0.textChanged.connect(self.save_settings)
        self.hotbar_1.textChanged.connect(self.save_settings)
        self.hotbar_2.textChanged.connect(self.save_settings)
        self.hotbar_3.textChanged.connect(self.save_settings)
        self.hotbar_4.textChanged.connect(self.save_settings)
        self.hotbar_5.textChanged.connect(self.save_settings)
        self.hotbar_6.textChanged.connect(self.save_settings)
        self.hotbar_7.textChanged.connect(self.save_settings)
        self.hotbar_8.textChanged.connect(self.save_settings)
        self.hotbar_9.textChanged.connect(self.save_settings)
        self.inventory.textChanged.connect(self.save_settings)
        self.prone.textChanged.connect(self.save_settings)
        self.target_inventory.textChanged.connect(self.save_settings)
        self.toggle_hud.textChanged.connect(self.save_settings)
        self.logs.textChanged.connect(self.save_settings)
        self.use.textChanged.connect(self.save_settings)

    def save_settings(self) -> None:
        "Saves the current config locally in the .json file"
        settings = {}

        settings["account_name"] = self.account_name.toPlainText()
        settings["bed_position"] = [int(self.bed_x.text()), int(self.bed_y.text())]
        settings["crystal_prefix"] = self.crystal_prefix.toPlainText()
        settings["crystal_beds"] = int(self.crystal_beds.text())
        settings["seed_prefix"] = self.seed_prefix.toPlainText()
        settings["seed_beds"] = int(self.seed_beds.text())
        settings["berry_prefix"] = self.berry_prefix.toPlainText()
        settings["berry_beds"] = int(self.berry_beds.text())
        settings["meat_prefix"] = self.meat_prefix.toPlainText()
        settings["meat_beds"] = int(self.meat_beds.text())
        settings["crystal_interval"] = int(self.crystal_interval.text())
        settings["stryder_depositing"] = self.stryder_depositing.isChecked()
        settings["drop_items"] = self.drop_items.toPlainText().split(",")
        settings["keep_items"] = self.keep_items.toPlainText().split(",")
        settings["game_launcher"] = self.game_launcher.currentText()
        settings["server_name"] = self.server_name.toPlainText()
        settings["server_search"] = self.server_search.toPlainText()
        settings["pod_name"] = self.pod_name.toPlainText()
        settings["webhook_alert"] = self.webhook_alert.toPlainText()
        settings["webhook_gacha"] = self.webhook_gacha.toPlainText()
        settings["webhook_logs"] = self.webhook_logs.toPlainText()

        with open("settings/settings.json", "w") as f:
            f.write(json.dumps(settings, indent=4))

        self.save_keybinds()

    def save_keybinds(self) -> None:
        "Saves the current keybind config locally in the .json file"
        keybinds = {}

        keybinds["console"] = self.console.toPlainText()
        keybinds["crouch"] = self.crouch.toPlainText()
        keybinds["drop"] = self.drop.toPlainText()
        keybinds["hotbar_0"] = self.hotbar_0.toPlainText()
        keybinds["hotbar_1"] = self.hotbar_1.toPlainText()
        keybinds["hotbar_2"] = self.hotbar_2.toPlainText()
        keybinds["hotbar_3"] = self.hotbar_3.toPlainText()
        keybinds["hotbar_4"] = self.hotbar_4.toPlainText()
        keybinds["hotbar_5"] = self.hotbar_5.toPlainText()
        keybinds["hotbar_6"] = self.hotbar_6.toPlainText()
        keybinds["hotbar_7"] = self.hotbar_7.toPlainText()
        keybinds["hotbar_8"] = self.hotbar_8.toPlainText()
        keybinds["hotbar_9"] = self.hotbar_9.toPlainText()
        keybinds["inventory"] = self.inventory.toPlainText()
        keybinds["prone"] = self.prone.toPlainText()
        keybinds["target_inventory"] = self.target_inventory.toPlainText()
        keybinds["toggle_hud"] = self.toggle_hud.toPlainText()
        keybinds["logs"] = self.logs.toPlainText()
        keybinds["use"] = self.use.toPlainText()

        with open("settings/keybinds.json", "w") as f:
            f.write(json.dumps(keybinds, indent=4))
