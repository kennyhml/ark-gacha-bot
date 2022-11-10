import sys, json, os, ctypes
from pynput.keyboard import Key, Listener
from gui.ArkBotUI import Ui_gachaLogBotUI
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
from threading import Thread
import ytrap, arkMonitoring, bot.ark_bot as ark_bot, pyautogui


































version = "v2.0"
lastUpdatedDate = "22nd July 2022"
writeJson = False
global settings
global saveChanges
keys = {}
#global botStatusText

# botStatus used to track what the bot is doing:
# 0 = off
# 1 = on
# 2 = paused
botStatus = 0

# True means changes are saved and False means changes are temporarily ignored
saveChanges = True

def getThisLocation():
    for i in settings["locations"]:
        if i["name"] == ui.baseLocationList.currentText():
            return i

def onKeyRelease(key):
    pass

def updateStatus():
    # Set the status text to show before the bot is run for the first time
    if(ytrap.getStatus() == ""):
        ui.botStatus.setText("Ready. Press F1 to start.")
    # Otherwise show the status text provided by YTrap
    else:
        ui.botStatus.setText(ytrap.getStatus())

def onKeyPress(key):
    global botStatus

    if (key == Key.f1):
        if (botStatus == 0):
            # Start the monitoring thread so we can detect if it crashes
            monitoring = Thread(target=arkMonitoring.start, args=([getThisLocation()]), daemon=True)
            monitoring.start()

            # Start the gacha bot itself
            ArkBot = Thread(target=ytrap.start, args=([getThisLocation()]), daemon=True)
            ArkBot.start()

            # Set the status to 1 because it started
            botStatus = 1

            # Update the status text so people know it started
            updateStatus()

    if (key == Key.f2):
        if (botStatus == 1):
            ytrap.stop()
            arkMonitoring.stop()
            ytrap.setStatusText("Ready. Press F1 to start.")

            botStatus = 0
    if (key == Key.f3):
        if (botStatus == 1):
            ark_bot.pause(not ark_bot.getPaused())
            if (ark_bot.getPaused()):
                arkMonitoring.pause(True)
                ytrap.setStatusText("Paused")
            else:
                arkMonitoring.pause(False)
                ytrap.setStatusText("Resumed")
    if (key == Key.f4):
        if (botStatus == 1):
            ytrap.setStatusText("Unstucking bot...")
            if ytrap.botUnstuck():
                botStatus = 0
                pyautogui.press('F1')
            else:
                pyautogui.press('F2')

# Adds the drop down options
def LoadUIStaticValues():

    #load map list
    ui.mapLocationList.addItems(["Other", "Aberration", "Gen2"])

    ui.mapLocationList.setCurrentIndex(0)

    #load Gacha load method
    ui.gachaLoadMethodList.addItems(["YTrap", "Metal", "None"])
    ui.gachaLoadMethodList.setCurrentIndex(0)

    ui.turnDirectionList.addItems(["Left", "Right", "360"])
    ui.turnDirectionList.setCurrentIndex(1)

    ui.pickupMethodList.addItems(["F Spam", "Whip"])
    ui.pickupMethodList.setCurrentIndex(0)

    ui.dedisAmountList.addItems(["2","4"])
    ui.dedisAmountList.setCurrentIndex(0)

    ui.polyVaultList.addItems(["Disable", "Left", "Right", "Both Sides", "Above", "360"])
    ui.polyVaultList.setCurrentIndex(0)

    ui.suicideMethodList.addItems(["Suicide", "Tek Pod"])
    ui.suicideMethodList.setCurrentIndex(0)

    ui.gameLauncherList.addItems(["Steam", "Epic"])
    ui.gameLauncherList.setCurrentIndex(0)

    # Defines possible keybinds shown to the user in the config
    # Must correspond exactly to the KEYBOARD_KEYS in pyautogui
    # https://pyautogui.readthedocs.io/en/latest/keyboard.html
    possibleKeybinds = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                        "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                        "u", "v", "w", "x", "y", "z", "1", "2", "3", "4",
                        "5", "6", "7", "8", "9", "0", "tab", "`", "~",
                        "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "+", "=",
                        "{", "}", "[", "]", "|", "\\", "capslock", "num0", "num1", "num2",
                        "num3", "num4", "num5", "num6", "num7", "num8",
                        "num9", "pgdown", "pgup", "insert", "tab", "space", "shift", "ctrl"]

    ui.arkCrouch.addItems(possibleKeybinds)
    ui.arkCrouch.setCurrentIndex(0)

    ui.arkProne.addItems(possibleKeybinds)
    ui.arkProne.setCurrentIndex(0)

    ui.arkUse.addItems(possibleKeybinds)
    ui.arkUse.setCurrentIndex(0)

    ui.arkInventory.addItems(possibleKeybinds)
    ui.arkInventory.setCurrentIndex(0)

    ui.arkTargetInventory.addItems(possibleKeybinds)
    ui.arkTargetInventory.setCurrentIndex(0)

    ui.arkDropItem.addItems(possibleKeybinds)
    ui.arkDropItem.setCurrentIndex(0)

    ui.arkToggleHUD.addItems(possibleKeybinds)
    ui.arkToggleHUD.setCurrentIndex(0)

    ui.arkConsole.addItems(possibleKeybinds)
    ui.arkConsole.setCurrentIndex(0)

    ui.arkTribeLog.addItems(possibleKeybinds)
    ui.arkTribeLog.setCurrentIndex(0)

    ui.arkHotbar1.addItems(possibleKeybinds)
    ui.arkHotbar1.setCurrentIndex(0)

    ui.arkHotbar2.addItems(possibleKeybinds)
    ui.arkHotbar2.setCurrentIndex(0)

    ui.arkHotbar3.addItems(possibleKeybinds)
    ui.arkHotbar3.setCurrentIndex(0)

    ui.arkHotbar4.addItems(possibleKeybinds)
    ui.arkHotbar4.setCurrentIndex(0)

    ui.arkHotbar5.addItems(possibleKeybinds)
    ui.arkHotbar5.setCurrentIndex(0)

    ui.arkHotbar6.addItems(possibleKeybinds)
    ui.arkHotbar6.setCurrentIndex(0)

    ui.arkHotbar7.addItems(possibleKeybinds)
    ui.arkHotbar7.setCurrentIndex(0)

    ui.arkHotbar8.addItems(possibleKeybinds)
    ui.arkHotbar8.setCurrentIndex(0)

    ui.arkHotbar9.addItems(possibleKeybinds)
    ui.arkHotbar9.setCurrentIndex(0)

    ui.arkHotbar0.addItems(possibleKeybinds)
    ui.arkHotbar0.setCurrentIndex(0)

    ui.buttonAddLocation.clicked.connect(lambda: addLocation(MainWindow))
    ui.buttonRenameLocation.clicked.connect(lambda: renameLocation(MainWindow))
    ui.buttonDelete.clicked.connect(deleteLocation)

def msgBox(msg):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setText(msg)
    msgBox.setWindowTitle("OpenElement Message")
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msgBox.exec_()

def saveSettingsAll():
    saveKeybinds()
    saveSettings()
    toggleUIOptions()


def saveSettings():
    global settings
    global saveChanges
    #get values?
    #write settings to disk?

    if saveChanges == False:
        return

    #lets start with all the listboxes
    for i in range(len(settings["locations"])):
        if settings["locations"][i]["name"] == ui.baseLocationList.currentText():
            if ui.mapLocationList.currentText() == "Aberration":
                settings["locations"][i]["aberrationMode"] = True
                settings["locations"][i]["dropGen2Suits"] = False
            elif ui.mapLocationList.currentText() == "Gen2":
                settings["locations"][i]["aberrationMode"] = False
                settings["locations"][i]["dropGen2Suits"] = True
            else:
                settings["locations"][i]["aberrationMode"] = False
                settings["locations"][i]["dropGen2Suits"] = False

            settings["locations"][i]["turnDirection"] = ui.turnDirectionList.currentText()
            settings["locations"][i]["loadGachaMethod"] = ui.gachaLoadMethodList.currentText()
            settings["locations"][i]["pickupMethod"] = ui.pickupMethodList.currentText()
            settings["locations"][i]["numDedis"]  = int(ui.dedisAmountList.currentText())
            settings["locations"][i]["polyVaults"] = ui.polyVaultList.currentText()
            settings["locations"][i]["suicideMethod"] = ui.suicideMethodList.currentText()
            settings["locations"][i]["gameLauncher"] = ui.gameLauncherList.currentText()

            ##checkboxes
            settings["locations"][i]["singlePlayer"] = ui.checkbox_isSingleplayer.isChecked()
            settings["locations"][i]["openTribeLog"] = ui.checkboxTribeLogs.isChecked()

            #Spinboxes
            settings["locations"][i]["bedX"] = int(ui.inputBedX.text())
            settings["locations"][i]["bedY"] = int(ui.inputBedY.text())
            settings["locations"][i]["seedBeds"] = int(ui.inputSeedBeds.text())
            settings["locations"][i]["crystalBeds"] = int(ui.inputCrystalBeds.text())
            settings["locations"][i]["crystalInterval"] = int(ui.inputPickupInterval.text())
            settings["locations"][i]["suicideFrequency"] = int(ui.inputSuicideFrequency.text())
            settings["locations"][i]["showLogInterval"] = int(ui.inputLogInterval.text())

            #Textboxes
            settings["locations"][i]["crystalBedPrefix"] = ui.inputCrystalBedPrefix.toPlainText()
            settings["locations"][i]["seedBedPrefix"] = ui.inputSeedPrefix.toPlainText()
            settings["locations"][i]["suicideBed"] = ui.inputSuicideBedPrefix.toPlainText()

            if ui.inputItemDrop.toPlainText() == "":
                settings["locations"][i]["dropItems"] = []
            elif ui.inputItemDrop.toPlainText() == "*":
                settings["locations"][i]["dropItems"] = [""]
            else:
                settings["locations"][i]["dropItems"] = ui.inputItemDrop.toPlainText().split(", ")

            if ui.inputItemKeep.toPlainText() == "":
                settings["locations"][i]["keepItems"] = []
            if ui.inputItemKeep.toPlainText() == "*":
                settings["locations"][i]["keepItems"] = [""]
            else:
                settings["locations"][i]["keepItems"] = ui.inputItemKeep.toPlainText().split(", ")

            settings["locations"][i]["serverName"] = ui.inputServerName.toPlainText()
            settings["locations"][i]["accountName"] = ui.inputDiscordName.toPlainText()
            settings["locations"][i]["webhookGacha"] = ui.inputGachaWebhook.toPlainText()
            settings["locations"][i]["serverSearch"] = ui.inputServerQuery.toPlainText()
            settings["locations"][i]["webhookAlert"] = ui.inputAlertWebhook.toPlainText()
            settings["locations"][i]["webhookTribeLog"] = ui.inputTribeWebhook.toPlainText()
            settings["locations"][i]["tagLevel0"] = ui.inputTag0.toPlainText()
            settings["locations"][i]["tagLevel1"] = ui.inputTag1.toPlainText()
            settings["locations"][i]["tagLevel2"] = ui.inputTag2.toPlainText()
            settings["locations"][i]["tagLevel3"] = ui.inputTag3.toPlainText()
            settings["locations"][i]["tagLevel4"] = ui.inputTag4.toPlainText()
            settings["locations"][i]["tagLevel5"] = ui.inputTag5.toPlainText()

    # Write these changes to settings.json
    with open("settings.json", "w") as f:
        f.write(json.dumps(settings, indent=4, sort_keys=True))

def saveKeybinds():
    keys["arkCrouch"] = ui.arkCrouch.currentText()
    keys["arkProne"] = ui.arkProne.currentText()
    keys["arkUse"] = ui.arkUse.currentText()
    keys["arkInventory"] = ui.arkInventory.currentText()
    keys["arkTargetInventory"] = ui.arkTargetInventory.currentText()
    keys["arkDropItem"] = ui.arkDropItem.currentText()
    keys["arkToggleHUD"] = ui.arkToggleHUD.currentText()
    keys["arkConsole"] = ui.arkConsole.currentText()
    keys["arkTribeLog"] = ui.arkTribeLog.currentText()
    keys["arkHotbar0"] = ui.arkHotbar0.currentText()
    keys["arkHotbar1"] = ui.arkHotbar1.currentText()
    keys["arkHotbar2"] = ui.arkHotbar2.currentText()
    keys["arkHotbar3"] = ui.arkHotbar3.currentText()
    keys["arkHotbar4"] = ui.arkHotbar4.currentText()
    keys["arkHotbar5"] = ui.arkHotbar5.currentText()
    keys["arkHotbar6"] = ui.arkHotbar6.currentText()
    keys["arkHotbar7"] = ui.arkHotbar7.currentText()
    keys["arkHotbar8"] = ui.arkHotbar8.currentText()
    keys["arkHotbar9"] = ui.arkHotbar9.currentText()
    keys["arkHotbar0"] = ui.arkHotbar0.currentText()

    with open("media/keybinds.json", "w") as keybinds:
        keybinds.write(json.dumps(keys, indent=4, sort_keys=True))

def loadKeybinds():
    try:
        # Open the keybinds file
        with open("media/keybinds.json", "r") as keybinds:
            keys = json.load(keybinds)

            # Assign the keybinds from the file to the GUI
            ui.arkConsole.setCurrentText(keys["arkConsole"])
            ui.arkCrouch.setCurrentText(keys["arkCrouch"])
            ui.arkDropItem.setCurrentText(keys["arkDropItem"])
            ui.arkTribeLog.setCurrentText(keys["arkTribeLog"])
            ui.arkHotbar0.setCurrentText(keys["arkHotbar0"])
            ui.arkHotbar1.setCurrentText(keys["arkHotbar1"])
            ui.arkHotbar2.setCurrentText(keys["arkHotbar2"])
            ui.arkHotbar3.setCurrentText(keys["arkHotbar3"])
            ui.arkHotbar4.setCurrentText(keys["arkHotbar4"])
            ui.arkHotbar5.setCurrentText(keys["arkHotbar5"])
            ui.arkHotbar6.setCurrentText(keys["arkHotbar6"])
            ui.arkHotbar7.setCurrentText(keys["arkHotbar7"])
            ui.arkHotbar8.setCurrentText(keys["arkHotbar8"])
            ui.arkHotbar9.setCurrentText(keys["arkHotbar9"])
            ui.arkInventory.setCurrentText(keys["arkInventory"])
            ui.arkProne.setCurrentText(keys["arkProne"])
            ui.arkTargetInventory.setCurrentText(keys["arkTargetInventory"])
            ui.arkToggleHUD.setCurrentText(keys["arkToggleHUD"])
            ui.arkUse.setCurrentText(keys["arkUse"])
    except Exception as e:
        # Something went wrong loading the keybinds from keybinds.json - let the user know
        ctypes.windll.user32.MessageBoxW(0, "ERROR: Unable to open media/keybinds.json\n\nWithout this file any changes to Keybinds will be ignored. You must use default Ark keybinds until this issue is fixed.", "Keybinds Error", 0)
        print("ERROR: loadKeybinds()")
        print(e)

def updateUIConfig(ConfigName):
    global settings
    global saveChanges
    
    # Stop any changes being saved during this process
    saveChanges = False
    
    #update UI based on location name
    try:
        for item in settings["locations"]:
            if item["name"] == ConfigName:

                ## update dropdown lists first
                if item["aberrationMode"]:
                    ui.mapLocationList.setCurrentText("Aberration")
                elif item["dropGen2Suits"]:
                    ui.mapLocationList.setCurrentText("Gen2")
                else:
                    ui.mapLocationList.setCurrentText("Other")

                ui.gachaLoadMethodList.setCurrentText(item["loadGachaMethod"])
                ui.turnDirectionList.setCurrentText(item["turnDirection"])
                ui.pickupMethodList.setCurrentText(item["pickupMethod"])
                ui.dedisAmountList.setCurrentText(str(item["numDedis"]))
                ui.suicideMethodList.setCurrentText(item["suicideMethod"])
                ui.gameLauncherList.setCurrentText(item["gameLauncher"])
                ui.polyVaultList.setCurrentText(item["polyVaults"])

                if item["singlePlayer"]:
                    ui.checkbox_isSingleplayer.setChecked(True)
                else:
                    ui.checkbox_isSingleplayer.setChecked(False)

                if item["openTribeLog"]:
                    ui.checkboxTribeLogs.setChecked(True)
                else:
                    ui.checkboxTribeLogs.setChecked(False)

                #set values to Spin box
                ui.inputBedX.setValue(int(item["bedX"]))
                ui.inputBedY.setValue(int(item["bedY"]))
                ui.inputSeedBeds.setValue(int(item["seedBeds"]))
                ui.inputCrystalBeds.setValue(int(item["crystalBeds"]))
                ui.inputPickupInterval.setValue(int(item["crystalInterval"]))
                ui.inputSuicideFrequency.setValue(int(item["suicideFrequency"]))
                ui.inputLogInterval.setValue(int(item["showLogInterval"]))
                ui.inputSaveTime.setValue(int(item["saveTime"]))

                # set values to text boxes
                ui.inputCrystalBedPrefix.setText(item["crystalBedPrefix"])
                ui.inputSeedPrefix.setText(item["seedBedPrefix"])
                ui.inputSuicideBedPrefix.setText(item["suicideBed"])
                dropItems = ", ".join(item["dropItems"])
                keepItems = ", ".join(item["keepItems"])
                ui.inputItemDrop.setText(dropItems)
                ui.inputItemKeep.setText(keepItems)
                ui.inputServerName.setText(item["serverName"])
                ui.inputDiscordName.setText(item["accountName"])
                ui.inputGachaWebhook.setText(item["webhookGacha"])
                ui.inputServerQuery.setText(item["serverSearch"])
                ui.inputAlertWebhook.setText(item["webhookAlert"])
                ui.inputTribeWebhook.setText(item["webhookTribeLog"])
                ui.inputTag0.setText(item["tagLevel0"])
                ui.inputTag1.setText(item["tagLevel1"])
                ui.inputTag2.setText(item["tagLevel2"])
                ui.inputTag3.setText(item["tagLevel3"])
                ui.inputTag4.setText(item["tagLevel4"])
                ui.inputTag5.setText(item["tagLevel5"])
    except Exception as e:
        print("ERROR: updateUIConfig()")
        print(e)

    # Resume any changes being saved
    saveChanges = True

def loadSettings():
    try:
        global settings
        #clear old list and create settings file if missing
        ui.baseLocationList.clear()
        if not os.path.exists("settings.json"):
            settings = {}
            settings["locations"] = []
            with open("settings.json", "w") as f:
                f.write(json.dumps(settings, indent=4, sort_keys=True))

        with open('settings.json') as json_file:
            settings = json.load(json_file)
    ##Start with populating all Lists
    #load base locations list
        if len(settings["locations"]) > 0:
            for items in settings["locations"]:
                if items["name"]:
                    ui.baseLocationList.addItem((items["name"]))
            ui.baseLocationList.setCurrentIndex(0)
            ui.baseLocationList.currentIndexChanged.connect(lambda: updateUIConfig(ui.baseLocationList.currentText()))
            #ui.baseLocationList.currentIndexChanged.connect(reloadUI)
    except Exception as e:
        msgBox("Settings Not Found")
        print("ERROR: loadSettings()")
        print(e)


def duplicateLocation(location):
    for i in range(len(settings["locations"])):
        if settings["locations"][i]["name"] == location:
            return True
    return False

def addLocation(self):
    loc, ok = QtWidgets.QInputDialog.getText(self, 'Add Location', 'Give this new Tower a name\n\nFor example, Tower 1 (Spider Cave) or Green Ob')
    if ok:
        if loc is not None and loc != "":
            if duplicateLocation(loc):
                QMessageBox.about(self, "Location Not Added", "This new location couldn't be created.\n\nLocation already exists with this name.\n\nPlease switch to that location with the drop down at the top right.\nOr delete that location and try again.\nLocation names must be unique.")
            else:
                global settings
                if settings:
                    settings["locations"].append({
                    "saveTime": 12,
                    "aberrationMode": False,
                    "accountName": "Gacha Bot",
                    "bedX": 795,
                    "bedY": 537,
                    "crystalBedPrefix": "crystal",
                    "crystalBeds": 1,
                    "crystalInterval": 600,
                    "dropGen2Suits": False,
                    "dropItems": [
                        "prim",
                        "ram",
                        "app"
                    ],
                    "gameLauncher": "Steam",
                    "keepItems": [
                        "riot",
                        "fab",
                        "pump",
                        "ass",
                        "mining"
                    ],
                    "loadGachaMethod": "YTrap",
                    "name": loc,
                    "numDedis": 4,
                    "openTribeLog": True,
                    "pickupMethod": "F Spam",
                    "polyVaults": "Above",
                    "seedBedPrefix": "seed",
                    "seedBeds": 24,
                    "serverName": "Main Server",
                    "serverSearch": "",
                    "showLogInterval": 300,
                    "singlePlayer": False,
                    "suicideBed": "Suicide Bed",
                    "afkBed": "AFK Bed",
                    "suicideFrequency": 1,
                    "suicideMethod": "Suicide",
                    "tagLevel0": "",
                    "tagLevel1": "",
                    "tagLevel2": "",
                    "tagLevel3": "@here",
                    "tagLevel4": "@everyone",
                    "tagLevel5": "",
                    "turnDirection": "Right",
                    "webhookAlert": "",
                    "webhookGacha": "",
                    "webhookTribeLog": ""
                    })
                    with open("settings.json", "w") as f:
                        f.write(json.dumps(settings, indent=4, sort_keys=True))

                    reloadUI()
                    # Select this new location to be displayed
                    ui.baseLocationList.setCurrentIndex(ui.baseLocationList.count() - 1)
                    #reloadUI()
                    
def renameLocation(self):
    loc, ok = QtWidgets.QInputDialog.getText(self, 'Rename Location', 'Give this Tower a different name\n\nFor example, Tower 1 (Spider Cave) or Green Ob')
    if ok:
        if loc is not None and loc != "":
            if duplicateLocation(loc):
                QMessageBox.about(self, "Location Not Renamed", "This location couldn't be renamed.\n\nLocation already exists with this name.\n\nPlease switch to that location with the drop down at the top right.\nOr delete that location and try again.\nLocation names must be unique.")
            else:
                global settings
                for i in range(len(settings["locations"])):
                    if settings["locations"][i]["name"] == ui.baseLocationList.currentText():
                        settings["locations"][i]["name"] = loc
                        #ui.baseLocationList.setCurrentIndex(loc)
            
                    with open("settings.json", "w") as f:
                        f.write(json.dumps(settings, indent=4, sort_keys=True))

                    reloadUI()

def deleteLocation():
    if (len(settings["locations"]) > 0):
        deleteLocationChoice = ctypes.windll.user32.MessageBoxW(0, "Are you sure you want to delete the \"" + ui.baseLocationList.currentText() + "\" location?\n\nThis cannot be undone.", "Delete Location", 4)
        if deleteLocationChoice == 6:
            count = 0
            for i in settings["locations"]:
                if (i["name"] == ui.baseLocationList.currentText()):
                    del settings["locations"][count]
                    with open("settings.json", "w") as f:
                        f.write(json.dumps(settings, indent=4, sort_keys=True))
                    reloadUI()
                    break
                count += 1
    else:
        msgBox("No Locations to Delete")

def reloadUI():
    loadSettings()
    updateUIConfig(ui.baseLocationList.currentText())

def connectTextChangesToSave():
    # setup auto save on value changes
    #   save drop down menus
    ui.mapLocationList.currentIndexChanged.connect(saveSettingsAll)
    ui.gachaLoadMethodList.currentIndexChanged.connect(saveSettingsAll)
    ui.turnDirectionList.currentIndexChanged.connect(saveSettingsAll)
    ui.pickupMethodList.currentIndexChanged.connect(saveSettingsAll)
    ui.dedisAmountList.currentIndexChanged.connect(saveSettingsAll)
    ui.polyVaultList.currentIndexChanged.connect(saveSettingsAll)
    ui.suicideMethodList.currentIndexChanged.connect(saveSettingsAll)
    ui.gameLauncherList.currentIndexChanged.connect(saveSettingsAll)
    ui.arkCrouch.currentIndexChanged.connect(saveSettingsAll)
    ui.arkProne.currentIndexChanged.connect(saveSettingsAll)
    ui.arkUse.currentIndexChanged.connect(saveSettingsAll)
    ui.arkInventory.currentIndexChanged.connect(saveSettingsAll)
    ui.arkTargetInventory.currentIndexChanged.connect(saveSettingsAll)
    ui.arkDropItem.currentIndexChanged.connect(saveSettingsAll)
    ui.arkToggleHUD.currentIndexChanged.connect(saveSettingsAll)
    ui.arkConsole.currentIndexChanged.connect(saveSettingsAll)
    ui.arkTribeLog.currentIndexChanged.connect(saveSettingsAll)
    ui.arkHotbar1.currentIndexChanged.connect(saveSettingsAll)
    ui.arkHotbar2.currentIndexChanged.connect(saveSettingsAll)
    ui.arkHotbar3.currentIndexChanged.connect(saveSettingsAll)
    ui.arkHotbar4.currentIndexChanged.connect(saveSettingsAll)
    ui.arkHotbar5.currentIndexChanged.connect(saveSettingsAll)
    ui.arkHotbar6.currentIndexChanged.connect(saveSettingsAll)
    ui.arkHotbar7.currentIndexChanged.connect(saveSettingsAll)
    ui.arkHotbar8.currentIndexChanged.connect(saveSettingsAll)
    ui.arkHotbar9.currentIndexChanged.connect(saveSettingsAll)
    ui.arkHotbar0.currentIndexChanged.connect(saveSettingsAll)
    #   save text boxes
    ui.inputBedX.textChanged.connect(saveSettingsAll)
    ui.inputBedY.textChanged.connect(saveSettingsAll)
    ui.inputSeedPrefix.textChanged.connect(saveSettingsAll)
    ui.inputSeedBeds.textChanged.connect(saveSettingsAll)
    ui.inputCrystalBedPrefix.textChanged.connect(saveSettingsAll)
    ui.inputPickupInterval.textChanged.connect(saveSettingsAll)
    ui.inputCrystalBeds.textChanged.connect(saveSettingsAll)
    ui.inputSaveTime.textChanged.connect(saveSettingsAll)
    ui.inputItemDrop.textChanged.connect(saveSettingsAll)
    ui.inputItemKeep.textChanged.connect(saveSettingsAll)
    ui.inputSuicideFrequency.textChanged.connect(saveSettingsAll)
    ui.inputSuicideBedPrefix.textChanged.connect(saveSettingsAll)
    ui.inputLogInterval.textChanged.connect(saveSettingsAll)
    ui.inputServerName.textChanged.connect(saveSettingsAll)
    ui.inputDiscordName.textChanged.connect(saveSettingsAll)
    ui.inputServerQuery.textChanged.connect(saveSettingsAll)
    ui.inputGachaWebhook.textChanged.connect(saveSettingsAll)
    ui.inputTribeWebhook.textChanged.connect(saveSettingsAll)
    ui.inputAlertWebhook.textChanged.connect(saveSettingsAll)
    ui.inputTag0.textChanged.connect(saveSettingsAll)
    ui.inputTag1.textChanged.connect(saveSettingsAll)
    ui.inputTag2.textChanged.connect(saveSettingsAll)
    ui.inputTag3.textChanged.connect(saveSettingsAll)
    ui.inputTag4.textChanged.connect(saveSettingsAll)
    ui.inputTag5.textChanged.connect(saveSettingsAll)
    #   save check boxes
    ui.checkbox_isSingleplayer.stateChanged.connect(saveSettingsAll)
    ui.checkboxTribeLogs.stateChanged.connect(saveSettingsAll)
    #ui.mapLocationList.textChanged.connect(saveSettingsAll)

def toggleUIOptions():
    # Toggle UI options based on choices made
    if ui.gachaLoadMethodList.currentText() == 'Metal':
        ui.turnDirectionList.setDisabled(True)
        ui.inputSeedPrefix.setEnabled(True)
        ui.inputSeedBeds.setEnabled(True)
    if ui.gachaLoadMethodList.currentText() == 'YTrap':
        ui.turnDirectionList.setEnabled(True)
        ui.inputSeedPrefix.setEnabled(True)
        ui.inputSeedBeds.setEnabled(True)
    if ui.gachaLoadMethodList.currentText() == 'None':
        ui.turnDirectionList.setDisabled(True)
        ui.inputSeedPrefix.setDisabled(True)
        ui.inputSeedBeds.setDisabled(True)

    if ui.suicideMethodList.currentText() == 'Suicide':
        #ui.inputSuicideFrequency.setEnabled(True)
        ui.labelCrystalbedprefix_11.setText("Suicide Bed Name")
        ui.labelseedBeds_4.setText("Suicide Frequency")
    if ui.suicideMethodList.currentText() == 'Tek Pod':
        #ui.inputSuicideFrequency.setDisabled(True)
        ui.labelCrystalbedprefix_11.setText("Tek Pod Name")
        ui.labelseedBeds_4.setText("Tek Pod Frequency")

if __name__ == "__main__":
    listener = Listener(on_press=onKeyPress, on_release=onKeyRelease)
    listener.start()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_gachaLogBotUI()
    ui.setupUi(MainWindow)

    # Add the icon
    MainWindow.setWindowIcon(QtGui.QIcon('media/icon.png'))
    
    # Update the version number
    MainWindow.setWindowTitle("OpenElement Gacha Bot " + version)
    ui.label_version.setText("Version " + version)
    ui.label_version.setAlignment(QtCore.Qt.AlignRight)
    ui.label_about_version.setText(version)
    ui.label_about_updated.setText(lastUpdatedDate)

    # Calling Function to load defaults settings in UI
    LoadUIStaticValues()
    loadKeybinds()
    loadSettings()
    updateUIConfig(ui.baseLocationList.currentText())
    toggleUIOptions()

    # Attempt to update bot status
    timer = QtCore.QTimer()
    timer.timeout.connect(updateStatus)
    timer.start(2000)

    # Use connect so that UI changes are saved
    connectTextChangesToSave()

    #show the UI
    MainWindow.show()
    sys.exit(app.exec_())
