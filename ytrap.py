import random

import pyautogui
import ark
import json
import time
import cv2
import numpy as np
import screen
import arkMonitoring


crystal_template = cv2.imread("templates/gacha_crystal.png", cv2.IMREAD_GRAYSCALE)
gen2suit_template = cv2.imread("templates/gen2suit.png", cv2.IMREAD_GRAYSCALE)
deposit_all_template = cv2.imread("templates/deposit_all.png", cv2.IMREAD_COLOR)
tooltips_template = cv2.imread("templates/tool_tips_enabled.png", cv2.IMREAD_GRAYSCALE)
added_template = cv2.imread("templates/added_template.png", cv2.IMREAD_GRAYSCALE)
vault_full_template = cv2.imread("templates/vault_full.png", cv2.IMREAD_GRAYSCALE)

lower_cyan = np.array([90,255,255])
upper_cyan = np.array([110,255,255])

hsv = cv2.cvtColor(deposit_all_template, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
masked_template = cv2.bitwise_and(deposit_all_template, deposit_all_template, mask= mask)
deposit_all_gray_template = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)
metal_template = cv2.imread("templates/inv_metal.jpg", cv2.IMREAD_GRAYSCALE)

beds = {}

keys = ark.getKeybinds()

lapCounter = 0
seedLapCounter = 0
skipMetal = False
inTekPod = False
fillCropsInterval = 28800
fillCropsLastFilled = 0
fillCropsLap = 0
tribeLogOpenInterval = 0    # How often the tribe log should be opened
tribeLogLastOpened = 0      # Tracks when the tribe log was last opened
tribeLogIsOpen = False      # Tracks whether the tribe log is currently opened for tek pod
popcornCount = 20            # How much metal to popcorn at each seed bed

suicideBed = ""

ark.setParams(1.45, 1.45, 10)
statusText = ""

def setStatusText(txt):
    global statusText
    statusText = txt

def setBeds(b):
    beds = b

def disableToolTips():
    roi = screen.getScreen()[164:210,623:668]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, tooltips_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 4000000):
        pyautogui.press('g')

def checkMetal():
    roi = screen.getScreen()[230:325, 210:305]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(gray_roi, metal_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if(max_val > 4500000):
        return True
    return False

def checkVaultFull():
    roi = screen.getScreen()[505:517,1092:1129]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, vault_full_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 480000):
        return True
    return False
"""
    else:
        # To help debug
        # arkMonitoring.screenshotScreen()
        # errorMessage = "Checked poly vault for being full. max_val is: " + str(max_val)
        # arkMonitoring.postMessageToDiscord(errorMessage, 0)
"""

def canDeposit():
    roi = screen.getScreen()
    screen_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(screen_hsv, lower_cyan, upper_cyan)
    masked_screen = cv2.bitwise_and(roi, roi, mask= mask)
    gray_screen = cv2.cvtColor(masked_screen, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, deposit_all_gray_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 10000000):
        return True
    return False


def checkWeWearingSuit():
    roi = screen.getScreen()[150:440,740:1170]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, gen2suit_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 1000000):
        return True
    return False


def checkWeHoldingSuit():
    roi = screen.getScreen()[230:330,110:680]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, gen2suit_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 1000000):
        return True
    return False

def checkWeGotRowOfCrystals():
    roi = screen.getScreen()[323:423,111:213]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, crystal_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if(max_val > 5500000):
        return True
    return False

def checkWeGotCrystals():
    roi = screen.getScreen()[230:330,120:210]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, crystal_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 5500000):
        return True
    return False

def waitForAddedGraphic():
    counter = 0
    while(counter < 10):
        roi = screen.getScreen()[1030:1070, 37:142]
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(gray_roi, added_template, cv2.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if(max_val > 3000000):
            return True

        time.sleep(0.1)
        counter += 1
    return False


def dropGen2Suit(popcorn = False):
    pyautogui.press(keys["arkInventory"])
    time.sleep(2.0)
    while(ark.inventoryIsOpen() == False):
        pyautogui.press(keys["arkInventory"])
        ark.sleep(2.0)
    
    while(checkWeWearingSuit()):
        pyautogui.moveTo(800, 200)
        pyautogui.dragTo(450, 275, 0.2)

        pyautogui.moveTo(800, 300)
        pyautogui.dragTo(450, 275, 0.2)

        pyautogui.moveTo(800, 400)
        pyautogui.dragTo(450, 275, 0.2)

        pyautogui.moveTo(1100, 200)
        pyautogui.dragTo(450, 275, 0.2)

        pyautogui.moveTo(1100, 400)
        pyautogui.dragTo(450, 275, 0.2)
        pyautogui.moveTo(800, 200)

        ark.sleep(2.0)

    
    if(popcorn):
        ark.searchMyStacks("fed")
        pyautogui.moveTo(165, 280)
        pyautogui.click()
        while(checkWeHoldingSuit()):
            pyautogui.press(keys["arkDropItem"])
    else:
        ark.dropItems("fed")
        ark.dropItems("")

    ark.closeInventory()


def loadGacha(gachaseed):
    global seedLapCounter
    global fillCropsInterval
    global fillCropsLastFilled
    global fillCropsLap
    
    if((beds["aberrationMode"] == False)):
        fillCropsTimeSinceFilled = time.time() - fillCropsLastFilled
        if(fillCropsTimeSinceFilled > fillCropsInterval):
            fillCropsLap = seedLapCounter
            fillCropsLastFilled = time.time()

        if(seedLapCounter == fillCropsLap):
            ableToFillCrops = False
            
            for i in range(6):
                if(ark.openInventory() == True):
                    ableToFillCrops = True
                    break
            if(ark.inventoryIsOpen() == False):
                ableToFillCrops = False

            # Check inventory is open before trying to collect pellets
            if(ableToFillCrops == True):
                ark.takeAll("ll")
                ark.searchMyStacks("ll")
                if(beds["turnDirection"] == "360"):
                    ark.tTransferTo(10)
                else:
                    ark.tTransferTo(5)
                ark.closeInventory()

    if(beds["turnDirection"] == "360"):
        ark.step('right', 1.0)
        ark.harvestCropStack("trap")
        pyautogui.press(keys["arkCrouch"])

        ark.lookUp()
        ark.lookDown()

        ark.step('right', 1.0)
        ark.harvestCropStack("trap", 1.2)
        pyautogui.press(keys["arkCrouch"])

        ark.lookUp()
        ark.lookDown()
        ark.step('right', 1.0)
        ark.harvestCropStack("trap")
        pyautogui.press(keys["arkCrouch"])

        ark.step('right', 1.0)

    else:
        if(beds["turnDirection"] == "Left"):
            ark.step('left', 1.0)
        else:
            ark.step('right', 1.0)
    
        ark.harvestCropStack("trap")
        pyautogui.press(keys["arkCrouch"])
        if(beds["turnDirection"] == "Left"):
            ark.step('left', 1.0)
        else:
            ark.step('right', 1.0)
    
        ark.lookDown()
        ark.step('up', 0.1)
        ark.harvestCropStack("trap", 1.2)
        pyautogui.press(keys["arkCrouch"])
        if(beds["turnDirection"] == "Left"):
            ark.step('right', 2.0)
        else:
            ark.step('left', 2.0)
    
    ark.lookUp()
    ark.lookDown()

    # Try to open the gacha inventory for 10 seconds
    for i in range(5):
        if(ark.openInventory() == True):
            ark.takeAll("ll")
            ark.transferAll("trap")
            ark.transferAll()
            ark.dropItems("")
            ark.closeInventory()
            return
        else:
            ark.sleep(2)

    # Stand up if can't access the gacha after 10 seconds
    pyautogui.press(keys["arkCrouch"])

    # Try to open the gacha inventory for another 10 seconds
    for i in range(5):
        if(ark.openInventory() == True):
            ark.takeAll("ll")
            ark.transferAll("trap")
            ark.transferAll()
            ark.dropItems("")
            ark.closeInventory()
            return
        else:
            ark.sleep(2)
    
    arkMonitoring.screenshotScreen()
    errorMessage = "Failed to access gacha inventory at " + gachaseed
    arkMonitoring.postMessageToDiscord(errorMessage, 2)

    pyautogui.press(keys["arkInventory"])
    time.sleep(2.0)
    while(ark.inventoryIsOpen() == False):
        pyautogui.press(keys["arkInventory"])
        ark.sleep(2.0)
    
    ark.searchMyStacks("trap")
    pyautogui.moveTo(165, 280)
    pyautogui.click()
    for i in range(40):
        pyautogui.press(keys["arkDropItem"])
        ark.sleep(0.5)
    ark.dropItems("")
    ark.closeInventory()

    
def pickupWithFSpam():
    pyautogui.press(keys["arkCrouch"])
    ark.lookDown()
    ark.step('s', 3.0)
    for i in range(12):
        pyautogui.press(keys["arkTargetInventory"])
        ark.sleep(0.2)
        ark.step('w', 0.1)
    ark.step('w', 1.0)

    pyautogui.press(keys["arkTargetInventory"])
        
def pickupWithWhip():
    pyautogui.press(keys["arkCrouch"])
    if(beds["polyVaults"] == "Left" or beds["polyVaults"] == "Both Sides" ):
        ark.step('left', 0.9)
    elif(beds["polyVaults"] == "Right"):
        ark.step('right', 0.9)
    else:
        ark.lookUp()

    if(ark.openInventory()):
        ark.takeAll("broken")
        ark.searchStructureStacks("whip")
        pyautogui.moveTo(1295, 283)
        pyautogui.dragTo(690, 1050, 0.5, button='left')
        waitForAddedGraphic()
        ark.closeInventory()

        if (beds["polyVaults"] == "Left" or beds["polyVaults"] == "Both Sides"):
            ark.step('right', 1.1)
        elif (beds["polyVaults"] == "Right"):
            ark.step('left', 1.1)
        else:
            ark.lookDown()

        ark.step('right', 2.1)
        pyautogui.press(keys["arkHotbar1"])
        ark.sleep(2.0)
        pyautogui.click()
        ark.sleep(5.0)
        pyautogui.click()
        ark.sleep(2.0)
        pyautogui.press(keys["arkHotbar1"])
        ark.step('left', 2.1)
        ark.lookDown()
    else:
        if (beds["polyVaults"] == "Left" or beds["polyVaults"] == "Both Sides"):
            ark.step('right', 1.2)
        elif (beds["polyVaults"] == "Right"):
            ark.step('left', 1.2)
        else:
            ark.lookDown()
        pyautogui.press(keys["arkCrouch"])
        pickupWithFSpam()

   
def depositInDedi():   
    for i in range(8):
        pyautogui.press(keys["arkUse"])
        ark.sleep(0.2)
        while(ark.getBedScreenCoords() != None):
            pyautogui.press('esc')
            ark.sleep(2.0)

def depositPolyGear(initialPolyDeposit = False, finalPolyDeposit = False):
    global beds
    
    itemsToBeDropped = True
    
    if (ark.openInventory()):

        # Only transfer the whip if whip pickup method selected
        if (beds["pickupMethod"] == "Whip"):
            time.sleep(0.5)
            pyautogui.moveTo(690, 1050)
            pyautogui.click()
            pyautogui.press('t')
            time.sleep(0.5)
            ark.transferAll("whip")

        """
        if(checkVaultFull()):
            arkMonitoring.screenshotScreen()
            errorMessage = "Please empty the gacha vault! No room left in the vault for more gacha items."
            arkMonitoring.postMessageToDiscord(errorMessage, 1)
        else:
            for item in beds["dropItems"]:
                ark.dropItems(item)
            for item in beds["keepItems"]:
                ark.transferAll(item)
        """

        # Skip keeping the poly gear if it is disabled
        if(beds["polyVaults"] != "Disable"):
            # Drop the unwanted items the first time only
            if(initialPolyDeposit == True):
                for item in beds["dropItems"]:
                    ark.dropItems(item)
                itemsToBeDropped = False

            # Keep the poly items specified in the config
            for item in beds["keepItems"]:
                ark.transferAll(item)

        # Drop all when this is the last poly vault
        if(finalPolyDeposit == True):
            ark.dropItems("")

        ark.closeInventory()
    
    return itemsToBeDropped

def whipCrystals():
    for i in range(beds["crystalBeds"]):
        runTime = time.time()
        arkMonitoring.trackTaskStarted("Collecting at gachacrystal" + str(i).zfill(2))
        setStatusText("Picking up crystals")
        ark.bedSpawn(beds["crystalBedPrefix"] + str(i).zfill(2), beds["bedX"], beds["bedY"], beds["singlePlayer"])
        openTribeLog()

        if(beds["pickupMethod"] == "Whip"):
            pickupWithWhip()
        else:
            pickupWithFSpam()

        pyautogui.press(keys["arkCrouch"])
        ark.step('up', 0.9)
    
        canDepositAttempts = 0
        while(canDeposit() == False):
            ark.step('w', 0.4)
            ark.sleep(0.2)
            if(canDepositAttempts == 25):
                ark.step('d', 0.02)
            elif(canDepositAttempts > 30):
                break
            canDepositAttempts += 1

        # To account for server save pause here to make sure the bot is still at the dedis
        try:
            # make sure beds["saveTime"] is numeric
            test = beds["saveTime"] + 1
            # sleep for the specified amount of time
            ark.sleep(beds["saveTime"])
        except TypeError:
            # otherwise if it isn't set or not numeric just sleep for a default of 5 seconds
            ark.sleep(5)

        canDepositAttempts = 0
        while(canDeposit() == False):
            ark.step('w', 0.4)
            ark.sleep(0.2)
            if(canDepositAttempts == 25):
                ark.step('d', 0.02)
            elif(canDepositAttempts > 30):
                break
            canDepositAttempts += 1

        pyautogui.press(keys["arkInventory"])
        ark.sleep(2.0)
        while(ark.inventoryIsOpen() == False):
            pyautogui.press(keys["arkInventory"])
            ark.sleep(2.0)

        disableToolTips()
        
        ark.searchMyStacks("gacha")
        pyautogui.moveTo(167, 280, 0.1)
        pyautogui.click()
        ark.sleep(1.0)
    
        crystalOpenAttempts = 0
        crystalHotbarOpens = 0
        while(checkWeGotRowOfCrystals()):
            ark.crystalHotBarUse()
            ark.sleep(0.3)
            # Make sure we don't get stuck here forever
            crystalOpenAttempts += 1
            # Count how many times we opened crystals
            crystalHotbarOpens += 1
            if(crystalOpenAttempts == 60):
                errorMessage = "Bot wasn't able to open gacha crystals within normal amount of attempts. It might be stuck! Trying to manually put the crystals on the hotbar."
                arkMonitoring.postMessageToDiscord(errorMessage, 0)
                arkMonitoring.trackTaskStarted("Putting gacha crystals onto hotbar")
                ark.crystalHotBarSetup()
                # Reset opens to zero as nothing opened yet
                crystalHotbarOpens = 0
            elif(crystalOpenAttempts > 120):
                # welp, time to giveup I guess
                # Reset opens to zero as nothing probably opened
                crystalHotbarOpens = 0
                break

        ark.crystalHotBarUse()
        ark.crystalHotBarUse()
        crystalHotbarOpens += 1

        ark.closeInventory()
            
        if(beds["numDedis"] == 2):
            depositInDedi()
            ark.step('up', 0.6)
            depositInDedi()
    
        if(beds["numDedis"] == 4):
            ark.step("right", 0.3)
            depositInDedi()
            ark.step("up", 0.7)
            depositInDedi() 

            ark.step("left", 0.6)
            depositInDedi()
            ark.step("down", 0.7)
            depositInDedi()
            
        if beds["polyVaults"] != "Disable":
            ark.step("up", 0.6)

        # Keep track of whether poly items are dropped yet or not
        # This is important when 2+ vaults and the first might not be accessed
        itemsToBeDropped = True
        if (beds["polyVaults"] == "Left"):
            ark.step('left', 0.9)
            depositPolyGear(True, True)
        elif (beds["polyVaults"] == "Right"):
            if(beds["numDedis"] == 4):
                ark.step('right', 0.3)
            ark.step('right', 0.9)
            depositPolyGear(True, True)
        elif (beds["polyVaults"] == "Both Sides"):
            ark.step('left', 0.9)
            itemsToBeDropped = depositPolyGear(True, False)
            ark.step('right', 2.4)
            depositPolyGear(itemsToBeDropped, True)
        elif (beds["polyVaults"] == "360"):
            ark.lookUp()
            itemsToBeDropped = depositPolyGear(True, False)
            ark.lookDown()
            ark.step('left', 0.9)
            itemsToBeDropped = depositPolyGear(itemsToBeDropped, False)
            ark.step('right', 2.4)
            depositPolyGear(itemsToBeDropped, True)
        elif (beds["polyVaults"] == "Above"):
            ark.lookUp()
            depositPolyGear(True, True)

        ark.lookDown()

        if(beds["dropGen2Suits"]):
            dropGen2Suit(False)
        pyautogui.press(keys["arkProne"])
        while(ark.accessBed() == False):
            ark.sleep(10)
        runTime = time.time() - runTime
        runTimeMessage = "Time taken at gachacrystal" + str(i).zfill(2) + " was " + str(int(round(runTime))) + " seconds.\nOpened approximately " + str((crystalHotbarOpens * 9)) + " crystals."
        if(runTime < 60 or runTime > 160):
            runTimeMessage += "\n**Might be an issue with this crystal area due to time taken!**"
            arkMonitoring.postMessageToDiscord(runTimeMessage, 0)
        else:
            arkMonitoring.postMessageToDiscord(runTimeMessage, 0)
               
    
def openTribeLog():
    global tribeLogOpenInterval
    global tribeLogLastOpened

    if(beds["openTribeLog"]):
        tribeLogTimeSinceOpened = time.time() - tribeLogLastOpened
        if(tribeLogTimeSinceOpened > tribeLogOpenInterval):
            ark.openTribeLog()
            ark.sleep(1)
            arkMonitoring.screenshotTribeLog()
            ark.sleep(1)
            ark.closeTribeLog()
            ark.sleep(2)
            tribeLogLastOpened = time.time()

def openTribeLogTekPod():
    global tribeLogOpenInterval
    global tribeLogLastOpened
    global tribeLogIsOpen

    if(beds["openTribeLog"]):
        # Open the tribe log in tek pod, regardless of timer
        if(tribeLogIsOpen == False):
            ark.openTribeLog()
            tribeLogIsOpen = True

        # Only screenshot the tribe log if enough time has passed based on the settings
        tribeLogTimeSinceOpened = time.time() - tribeLogLastOpened
        if(tribeLogTimeSinceOpened > tribeLogOpenInterval):
            arkMonitoring.screenshotTribeLog()
            ark.sleep(1)
            tribeLogLastOpened = time.time()

def closeTribeLogTekPod():
    global tribeLogLastOpened
    global tribeLogIsOpen
    
    if(tribeLogIsOpen):
        #tribeLogLastOpened = time.time()
        ark.closeTribeLog()
        tribeLogIsOpen = False
        ark.sleep(2)

def suicideAndRespawn(alreadyAccessingBed = True, trackTask = True):
    global beds

    attempts = 0
    if(alreadyAccessingBed == False):
        ark.checkTerminated()
        ark.lookDown()
        if beds["suicideMethod"] != "Tek Pod":
            pyautogui.press(keys["arkProne"])
        elif (beds["suicideMethod"] != "Tek Pod") and (attempts > 5):
            pyautogui.press(keys["arkProne"])
            attempts = 0
        while(ark.accessBed() == False):
            ark.sleep(10)
        attempts = attempts + 1

    runTime = time.time()
    if(trackTask): # Track this by default - optional for when suiciding is being done to unstuck the bot
        arkMonitoring.trackTaskStarted("Suiciding")
    ark.bedSpawn(beds["suicideBed"], beds["bedX"], beds["bedY"])
    
    if(beds["suicideMethod"] == "Tek Pod"):
        # Use the tek pod to recharge food/water
        ark.tekPodEnter()
        openTribeLogTekPod()
        ark.sleep(60)
        closeTribeLogTekPod()
        ark.tekPodLeave()

    while(ark.getBedScreenCoords() == None):
        ark.sleep(0.5)

    runTime = time.time() - runTime
    if beds["suicideMethod"] == "Tek Pod":
        runTimeMessage = "Time taken in tek pod was " + str(int(round(runTime))) + " seconds."
        arkMonitoring.postMessageToDiscord(runTimeMessage, 0)
    else:
        runTimeMessage = "Time taken suiciding was " + str(int(round(runTime))) + " seconds."
        arkMonitoring.postMessageToDiscord(runTimeMessage, 0)

def botUnstuck():
    arkMonitoring.postMessageToDiscord("Bot attempting to unstuck itself...", 0)
    print("DEBUG botUnstuck(): Trying to unstuck the bot")
    ark.terminate(True)         # terminate will stop whatever the bot was doing
    time.sleep(10)              # wait for the bot to finish
    ark.terminate(False)        # set terminate to False so the commands work
    print("DEBUG botUnstuck(): Checking if can open console")
    if ark.openConsole():       # see if we can open the console
        print("DEBUG botUnstuck(): Console could be opened")
        ark.closeConsole()          # close the console
        ark.sleep(2)

        print("DEBUG botUnstuck(): Dropping all to fast travel")
        # Drop all so when we fast travel it doesn't leave a 30min bag
        pyautogui.press(keys["arkInventory"])
        time.sleep(2.0)

        print("DEBUG botUnstuck(): Checking if Inventory is open")
        while(ark.inventoryIsOpen() == False):
            ark.checkTerminated()
            pyautogui.press(keys["arkInventory"])
            ark.sleep(2.0)
        ark.dropItems("")
        ark.closeInventory()

        print("DEBUG botUnstuck(): Suiciding and respawning")
        # Suicide and respawn
        suicideAndRespawn(False, True)
        ark.sleep(20)
        ark.terminate(True)
        print("DEBUG botUnstuck(): Bot is unstuck and restarted automagically")
        return True
    else:
        print("DEBUG botUnstuck(): Unable to open the console")
        # Couldn't open the console
        detectedArkScreen = arkMonitoring.checkArkScreen()
        print("DEBUG botUnstuck(): Checking for ark screen with result: " + detectedArkScreen)
        # Is ark running?
        if arkMonitoring.checkArkRunning():
            print("DEBUG botUnstuck(): Ark detected as running")
            # Ark running? Let's connect
            if detectedArkScreen == "mainmenu":
                print("DEBUG botUnstuck(): Detected main menu - opening session list")
                arkMonitoring.arkOpenSessionList()
                print("DEBUG botUnstuck(): Detected session list - searching for server")
                arkMonitoring.arkSearchForServer()
                print("DEBUG botUnstuck(): Server found - trying to join")
                arkMonitoring.arkJoinServer()
                print("DEBUG botUnstuck(): arkJoinServer was successful...")
            elif detectedArkScreen == "sessionlist":
                print("DEBUG botUnstuck(): Detected sessionlist instead of mainmenu")
                # do stuff from session list
                arkMonitoring.arkSearchForServer()
                arkMonitoring.arkJoinServer()
        else:
            print("DEBUG botUnstuck(): Ark was not detected as running... so time to launch it")
            # Ark isn't running so time to launch it...
            arkMonitoring.launchArk()

        print("DEBUG botUnstuck(): Waiting 60 seconds for the tower to render")
        # Wait at least 60 seconds for the tower to load in fully
        ark.sleep(60)

        print("DEBUG botUnstuck(): Try to open the console to see if we loaded in")
        if ark.openConsole():  # see if we can open the console
            print("DEBUG botUnstuck(): Console could be opened after reconnecting")
            ark.closeConsole()  # close the console
            ark.sleep(2)

            # Open inventory to drop all
            pyautogui.press(keys["arkInventory"])
            time.sleep(2.0)
            while(ark.inventoryIsOpen() == False):
                ark.checkTerminated()
                pyautogui.press(keys["arkInventory"])
                ark.sleep(2.0)
            ark.dropItems("")
            ark.closeInventory()

            # Suicide and respawn
            suicideAndRespawn(False, True)
            ark.sleep(20)
            ark.terminate(True)

            print("DEBUG botUnstuck(): Returning because bot detected as reconnected")
            return True

        # Well, we tried. Print an error and give up
        print("DEBUG botUnstuck(): Everything that was tried to reconnect failed - time to quit")
        errorMessage = "Bot couldn't be unstuck automagically."
        arkMonitoring.postMessageToDiscord(errorMessage, 1)
        ark.terminate(True)
        return False



def getStatus():
    return statusText
    
def stop():
    ark.terminate(True)
    arkMonitoring.postMessageToDiscord("OpenElement has been stopped.", 0)


def crystalStationPickup():
    global lapCounter
    global inTekPod
    #if (duration > beds["crystalInterval"]):
    if (inTekPod == True):
        closeTribeLogTekPod()
        ark.tekPodLeave()
        inTekPod = False

    whipCrystals()
    """lapCounter += 1
    if (lapCounter >= beds["suicideFrequency"]):
        lapCounter = 0
        setStatusText("Suiciding . . .")
        suicideAndRespawn()"""

def loadMetal(bed):
    global popcornCount

    time.sleep(2)
    pyautogui.press(keys["arkCrouch"])
    time.sleep(1)
    if ark.openInventory(20):
        c = 0
        while not checkMetal():
            ark.takeAll()
            ark.sleep(1)
            c += 1
            if c > 20:
                ## possibly no metal found dedi is empty?
                arkMonitoring.postMessageToDiscord("No metal found in - " + str(beds["seedBedPrefix"]) + str(bed).zfill(2), 5)
                ark.closeInventory()
                return False

        if checkMetal():
            for i in range(int(popcornCount /  2)):
                pyautogui.moveTo(250, 275)
                time.sleep(0.2)
                pyautogui.press(keys["arkDropItem"])
                time.sleep(0.1)
                pyautogui.moveTo(350, 275)
                time.sleep(0.2)
                pyautogui.press(keys["arkDropItem"])
                time.sleep(0.1)
        #put back metal into dedi
            while checkMetal():
                ark.transferAll()
                ark.sleep(1)

        ark.closeInventory()
        if popcornCount > 100:
            ark.sleep(120) #need to wait for gachas to pick
        else:
            ark.sleep(30)
    else:
        arkMonitoring.postMessageToDiscord("Error Opening dedi at " + str(beds["seedBedPrefix"]) + str(bed).zfill(2), 5)
        arkMonitoring.screenshotScreen()
        return False
    """ark.lookDown()
    pyautogui.press(keys["arkProne"])
    while (ark.accessBed() == False):
        ark.sleep(10)"""

def restUntilNextTask():
    global beds
    global inTekPod
    
    if beds["suicideMethod"] == "Tek Pod":
        # Check if they are in a tek pod or not
        if(inTekPod == False):
            setStatusText("Sleeping in Pod")
            arkMonitoring.trackTaskStarted("Lying in Tek Pod")
            arkMonitoring.postMessageToDiscord("Going to Sleep in Tek Pod", 0)
            ark.bedSpawn(beds["suicideBed"], beds["bedX"], beds["bedY"])
            ark.tekPodEnter()
            openTribeLogTekPod()
            inTekPod = True
            time.sleep(5)
        else:
            # Make sure either tek pod XP icon visible or tribe logs open
            if(ark.checkTekPodEntered() or ark.tribelogIsOpen()):
                arkMonitoring.trackTaskStarted("Lying in Tek Pod")
                openTribeLogTekPod()
                ark.sleep(10)
            # If this fails then monitoring will kick in after 5min
    elif beds["suicideMethod"] == "Suicide with AFK Bed":
        # Check if they are in the afk box or not
        if(inTekPod == False):
            setStatusText("AFKing in Box")
            arkMonitoring.trackTaskStarted("AFKing in Box")
            arkMonitoring.postMessageToDiscord("AFKing in Box", 0)
            ark.bedSpawn(beds["afkBed"], beds["bedX"], beds["bedY"])
            openTribeLogTekPod()
            inTekPod = True
            time.sleep(5)
        else:
            # Make sure either tek pod XP icon visible or tribe logs open
            if(ark.checkTekPodEntered() or ark.tribelogIsOpen()):
                arkMonitoring.trackTaskStarted("Lying in Tek Pod")
                openTribeLogTekPod()
                ark.sleep(10)
            # If this fails then monitoring will kick in after 5min

def start(b):
    global beds
    global lapCounter
    global seedLapCounter
    global tribeLogOpenInterval
    global skipMetal
    global inTekPod
    global keys

    inTekPod = False
    beds = b
    tribeLogOpenInterval = beds["showLogInterval"]
    ark.pause(False)
    ark.terminate(False)
    ark.setFirstRun(True)
    setStatusText("Starting. F2 to stop. Alt tab back into the game NOW.")
    arkMonitoring.postMessageToDiscord("OpenElement is starting...", 0)
    
    # Load custom keybinds from keybinds.json
    ark.updateKeys()
    keys = ark.getKeybinds()
    
    try:
        ark.sleep(8)
        setStatusText("spawning in...")
        start = time.time()
        metalClock = time.time()
        while(True):
            lapTime = time.time()

            if beds["loadGachaMethod"] == "Metal":
                duration = time.time() - start
                if (duration > beds["crystalInterval"]):
                    crystalStationPickup()
                    start = time.time()

                #setup metal refill checks here
                popcornTime = 5000
                refillTime = time.time() - metalClock
                if refillTime > popcornTime:
                    skipMetal = False
                    metalClock = time.time()

                if not skipMetal:
                    for i in range(beds["seedBeds"]):
                        runTime = time.time()
                        if (inTekPod == True):
                            closeTribeLogTekPod()
                            ark.tekPodLeave()
                            inTekPod = False

                        arkMonitoring.trackTaskStarted("Filling Metal at Gacha" + str(i).zfill(2))
                        setStatusText("Filling Metal at " + beds["seedBedPrefix"] + str(i).zfill(2))
                        ark.bedSpawn(beds["seedBedPrefix"] + str(i).zfill(2), beds["bedX"], beds["bedY"], beds["singlePlayer"])

                        loadMetal(i)
                        if (beds["dropGen2Suits"]):
                            dropGen2Suit(False)
                        ark.lookDown()
                        pyautogui.press(keys["arkProne"])
                        while (ark.accessBed() == False):
                            ark.sleep(10)
                        runTime = time.time() - runTime
                        runTimeMessage = "Time taken at " + beds["seedBedPrefix"] + str(i).zfill(2) + " was " + str(
                            int(round(runTime))) + " seconds."
                        # Add extra time for 360 crop plot design
                        extraTime = 120
                        if (beds["turnDirection"] == "360"):
                            extraTime += 30
                        #if (runTime > (180 + extraTime) or runTime < (10 + extraTime)):
                        if (runTime > (180 + extraTime)):
                            runTimeMessage += " **Likely an issue with this station!**"
                            arkMonitoring.postMessageToDiscord(runTimeMessage, 0)
                        else:
                            arkMonitoring.postMessageToDiscord(runTimeMessage, 0)

                        ##pickup crystals
                        if ((time.time() - start) > beds["crystalInterval"]):
                            crystalStationPickup()
                            start = time.time()
                            lapCounter += 1
                            if (lapCounter >= beds["suicideFrequency"]):
                                lapCounter = 0
                                setStatusText("Suiciding . . .")
                                suicideAndRespawn()

                        if i == beds["seedBeds"]-1:
                            skipMetal = True

                restUntilNextTask()


            elif beds["loadGachaMethod"] == "YTrap":
                for i in range(beds["seedBeds"]):
                    duration = time.time() - start
                    if(duration > beds["crystalInterval"]):
                        if(inTekPod == True):
                            closeTribeLogTekPod()
                            ark.tekPodLeave()
                            inTekPod = False
                        start = time.time()
                        whipCrystals()
                        lapCounter += 1
                        if(lapCounter >= beds["suicideFrequency"]):
                            lapCounter = 0
                            setStatusText("Suiciding . . .")
                            suicideAndRespawn()

                    runTime = time.time()
                    arkMonitoring.trackTaskStarted("Seeding at gachaseed" + str(i).zfill(2))
                    setStatusText("Seeding at gachaseed" + str(i).zfill(2))
                    ark.bedSpawn(beds["seedBedPrefix"] + str(i).zfill(2), beds["bedX"], beds["bedY"], beds["singlePlayer"])
                    openTribeLog()
                    loadGacha("gachaseed" + str(i).zfill(2))
                    if(beds["dropGen2Suits"]):
                        dropGen2Suit(False)
                    ark.lookDown()
                    pyautogui.press(keys["arkProne"])
                    while(ark.accessBed() == False):
                        ark.sleep(10)
                    runTime = time.time() - runTime
                    runTimeMessage = "Time taken at gachaseed" + str(i).zfill(2) + " was " + str(int(round(runTime))) + " seconds."
                    # Add extra time for 360 crop plot design
                    extraTime = 0
                    if(beds["turnDirection"] == "360"):
                        extraTime = 30
                    if(runTime > (180 + extraTime) or runTime < (100 + extraTime)):
                        runTimeMessage += " **Likely an issue with this station!**"
                        arkMonitoring.postMessageToDiscord(runTimeMessage, 0)
                    else:
                        arkMonitoring.postMessageToDiscord(runTimeMessage, 0)

                seedLapCounter += 1

                lapTime = time.time() - lapTime
                lapTimeMinutes = lapTime / 60
                lapTimeStationAvg = lapTime / int(beds["seedBeds"])
                lapMessage = " **Lap #" + str(seedLapCounter) + " completed!** This lap of the full tower was " + str(int(round(lapTime))) + " seconds (" + str(int(round(lapTimeMinutes))) + " minutes).\nThis is an average of **" + str(int(round(lapTimeStationAvg))) + " seconds** per each of the " + str(beds["seedBeds"]) + " seed beds."
                arkMonitoring.postMessageToDiscord(lapMessage, 0)

            elif beds["loadGachaMethod"] == "None":
                duration = time.time() - start
                if beds["crystalBeds"] > 0 and (duration > beds["crystalInterval"] or ark.getFirstRun()):
                    if(inTekPod == True):
                        closeTribeLogTekPod()
                        ark.tekPodLeave()
                        inTekPod = False
                    start = time.time()
                    whipCrystals()
                    lapCounter += 1
                
                restUntilNextTask()

            time.sleep(0.1)
    except Exception as e:
        setStatusText("Ready. Press F1 to start.")
        print("YTrap thread terminated.")
        print(str(e))
        errorMessage = "YTrap thread terminated!"
        arkMonitoring.postMessageToDiscord(errorMessage, 1)
