import json         # required to read the config file
import time         # required to sleep between monitoring checks
import cv2          # required to compare images
import numpy as np  # required for image manipulation
import os           # required to check if a file exists
import pyautogui    # required to get screenshots
import requests     # required for posting to Discord via Webhooks
import webbrowser   # required to launch Ark via browser link
import pytesseract  # required to OCR the tribe log
import re           # required for regex searches
import win32gui     # required to check if Ark is running

# All the settings for this location - passed from main.py
settings = {}

# Allows arkMonitoring to be used in a thread
terminated = False
paused = False

# Track time since last task started
timeLastTaskStarted = 0
timeLastTaskName = ""

# Track progression through the notification process
outageLevel0 = False
outageLevel1 = False
outageLevel2 = False
outageLevel3 = False

#passing this function True will cause most functions in this script to throw an exception
#useful to terminate a thread in a multithreaded environment
def terminate(t):
    global terminated
    terminated = t

#passing this function True will cause the bot to halt until it is passed False again
#note that terminate(True) will still kill the bot
def pause(p):
    global paused
    
    # Unpausing so reset variables
    if(p == False):
        trackTaskStarted("Resumed Ark Monitoring")
    
    paused = p

#returns the paused state
def getPaused():
    global paused
    return paused

#internal functino, don't use it
#throws an exception if terminated is True
def checkTerminated():
    global paused
    global terminated

    if(terminated):
        raise Exception("Monitoring thread terminated.")

    #if paused, halt but also die if terminated 
    while(paused):
        time.sleep(0.1)
        if(terminated):
            raise Exception("Monitoring thread terminated.")

# Screenshot the whole screen
def screenshotScreen():
    tribeLog = pyautogui.screenshot()
    tribeLog.save(r'screenshots\screen-latest.png')
    postScreenToDiscord()

# Post image to Discord
def postScreenToDiscord():
    global settings
    
    url = settings["webhookGacha"]
    
    if(url == ""):
        #print("Monitoring: Screenshot not posted to Discord as Webhook is blank.")
        return

    message = ""
    message = addDiscordTag(message)

    data = {
        "content": message,
        "avatar_url": "https://i.imgur.com/cMBnUQo.png"
    }
    
    files = {
        "file" : ("./screenshots/screen-latest.png", open("./screenshots/screen-latest.png", 'rb'))
    }

    result = requests.post(url, data = data, files=files)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postScreenToDiscord() had an error:")
        print(err)

# Screenshot the current tribe log
def screenshotTribeLog():
    tribeLog = pyautogui.screenshot(region=(1342, 183, 438, 815))
    tribeLog.save('screenshots/tribelog-latest.png')
    tribePlayers = pyautogui.screenshot(region=(889, 197, 346, 30))
    tribePlayers = tribePlayers.resize((438,38))
    tribeLog.paste(tribePlayers, (0,777))
    tribeLog.save('screenshots/tribelogplayers-latest.png')
    checkTribeLogEvents()

def checkTribeLogEvents():
    global settings
    
    checkTribeLogEventsImageTemplate()
    return

def prepareTesseractImage(image, brightness = 150):
    # Make the image larger
    scale_percent = 5 # how much to enlarge the image
    image = cv2.resize(image, (int(image.shape[1] * scale_percent), int(image.shape[0] * scale_percent)), interpolation = cv2.INTER_LINEAR)

    # Convert green of tek sensors to white
    #background = np.where(image == (63, 127, 0))
    #image[background[0], background[1], :] = [255, 255, 255]
    # Note: While this kind of works it is NOT optimal and makes the OCR significantly worse

    # Make the image much darker to remove the background (will go mostly black)
    M = np.ones(image.shape, dtype="uint8") * brightness
    image = cv2.subtract(image, M)

    # Set anywhere that isn't background (i.e. the text) to solid white
    background = np.where(image != 0)
    image[background[0], background[1], :] = [255, 255, 255]

    # Convert anywhere with text to a solid white
    background = np.where(image != 0)
    image[background[0], background[1], :] = [255, 255, 255]

    # Invert the image (now white background with black text)
    image = 255 - image
    
    # Return the prepared version of the tribe log
    return image

def tesseractAddSpaces(result, message):
    result = result.replace(message, " " + message + " ")
    result = result.replace("  " + message, " " + message)
    result = result.replace(message + "  ", message + " ")
    result = result.replace(message + " !", message + "!")
    return result

def parseTesseractText(result):
    # Use replace to make results more human readable
    result = result.replace("\n", "")
    result = result.replace("Dav ", "Day ")
    result = result.replace("Day,", "Day")
    result = result.replace("Day", "\nDay")
    result = re.sub("Day (\d+).", r"Day \1,", result)
    result = result.replace("destroved", "destroyed")
    result = result.replace("bv", "by")
    result = tesseractAddSpaces(result, "triggered")
    result = result.replace("eneny", "enemy")
    result = result.replace("ememyv", "enemy")
    result = result.replace("anenemy", "an enemy")
    result = result.replace("enemy dio", "enemy dino")
    result = result.replace("enemy ding", "enemy dino")
    result = result.replace("byah", "by an")
    result = result.replace("byan", "by an")
    result = result.replace("Sutwiwor", "survivor")
    result = result.replace("‘", "'")
    result = result.replace("’", "'")
    result = result.replace("\"", "'")
    result = result.replace("{", "(")
    result = result.replace("}", ")")
    result = result.replace(")))", ")!")
    result = tesseractAddSpaces(result, "was")
    result = tesseractAddSpaces(result, "killed")
    result = tesseractAddSpaces(result, "Adolescent")
    result = tesseractAddSpaces(result, "-")
    result = result.replace("Starved", "starved")
    result = tesseractAddSpaces(result, "starved")
    result = result.replace("LvI", "Lvl")
    result = result.replace("Lvi", "Lvl")
    result = result.replace("Lvl", " Lvl ")
    result = result.replace("  Lvl", " Lvl")
    result = result.replace("Lvl  ", "Lvl ")
    result = result.replace("[Clonel", "[Clone]")
    result = tesseractAddSpaces(result, "[Clone]")
    result = result.replace("Charae", "Charge")
    result = result.replace("Charoe", "Charge")
    result = result.replace("Chasae", "Charge")
    result = result.replace("decav", "decay")
    result = result.replace("destroyedl", "destroyed!")
    result = result.replace("Steaosaurus", "Stegosaurus")
    result = result.replace("Steaqosaurus", "Stegosaurus")
    result = result.replace("Stedaosaurus", "Stegosaurus")
    result = result.replace("Astradelohis", "Astrodelphis")
    result = result.replace("Astrodelohis", "Astrodelphis")
    result = result.replace("Astrodelbhis", "Astrodelphis")
    result = result.replace("Giaanotosaurus", "Giganotosaurus")
    result = result.replace("iTek", "(Tek")
    result = result.replace("Ceilina", "Ceiling")
    result = tesseractAddSpaces(result, "Ceiling")
    result = result.replace("Trianale", "Triangle")
    result = tesseractAddSpaces(result, "Triangle")
    result = result.replace("Manaaarmr", "Managarmr")
    result = result.replace("  (", "(")
    result = result.replace(" (", "(")
    result = result.replace("(", " (")
    result = result.replace("'l", "'!")
    result = result.replace("“", "")
    result = result.replace("''", "'")
    result = result.replace("auto - decay", "auto-decay")
    result = result.replace("MetalDouble", "Metal Double")
    result = result.replace("TekDouble", "Tek Double")
    result = result[:result.rfind('\n')]
    result = result.replace("\n", "", 1)
    
    return result

def checkTribeLogEventsImageTemplate():
    tribeLog_entry_y = 9999
    threshold = 0.9
    alert_triggered = False
    alert_destroyed = False
    alert_triggered_y = 9999
    alert_destroyed_y = 9999

    tribeLog = cv2.imread('screenshots/tribelogplayers-latest.png', cv2.IMREAD_UNCHANGED)
    # Try to open the daytime png and make it if necessary
    if(os.path.exists('screenshots/tribelog-daytime.png')):
        tribeLog_daytime_old = cv2.imread('screenshots/tribelog-daytime.png', cv2.IMREAD_UNCHANGED)
    else:
        cv2.imwrite('screenshots/tribelog-daytime.png', np.zeros((10,160,3), dtype=np.uint8))
        tribeLog_daytime_old = cv2.imread('screenshots/tribelog-daytime.png', cv2.IMREAD_UNCHANGED)
    template_triggered = cv2.imread('templates/tribelog-triggered.png', cv2.IMREAD_UNCHANGED)
    template_destroyed = cv2.imread('templates/tribelog-destroyed.png', cv2.IMREAD_UNCHANGED)

    result_triggered = cv2.matchTemplate(tribeLog, template_triggered, cv2.TM_CCOEFF_NORMED)
    result_destroyed = cv2.matchTemplate(tribeLog, template_destroyed, cv2.TM_CCOEFF_NORMED)

    result_destroyed_locations = np.where( result_destroyed >= threshold)
    for result in zip(*result_destroyed_locations[::-1]):
        alert_destroyed = True
        if(result[1] < tribeLog_entry_y):
            tribeLog_entry_y = result[1]
            alert_destroyed_y = result[1]

    result_triggered_locations = np.where( result_triggered >= threshold)
    for result in zip(*result_triggered_locations[::-1]):
        alert_triggered = True
        if(result[1] < tribeLog_entry_y):
            tribeLog_entry_y = result[1]
            alert_triggered_y = result[1]

    # It will only be under 9999 if one of the templates was detected
    if(tribeLog_entry_y < 9999):
        # Get a crop of the day/time at this Y coord
        tribeLog_daytime_new = tribeLog[tribeLog_entry_y:tribeLog_entry_y + 10, 0:160]

        # Check if tribeLog_daytime_new matches tribeLog_daytime_old
        result_tribeLog_daytime = cv2.matchTemplate(tribeLog_daytime_old, tribeLog_daytime_new, cv2.TM_CCOEFF_NORMED)
        result_tribeLog_daytime_locations = np.where( result_tribeLog_daytime >= threshold)
        result_tribeLog_daytime_match = False
        for result in zip(*result_tribeLog_daytime_locations[::-1]):
            result_tribeLog_daytime_match = True

        if(result_tribeLog_daytime_match == False):
            # Something triggered!
            if(alert_triggered or alert_destroyed):
                if(alert_triggered_y > alert_destroyed_y):
                    postAlertToDiscord("Something Destroyed!",4)
                else:
                    postAlertToDiscord("Tek Sensor Triggered!",3)
            # Save this daytime info for future checks
            cv2.imwrite('screenshots/tribelog-daytime.png', tribeLog_daytime_new)

    # Also post tribe log to Discord as normal
    postTribeLogToDiscord()

# Post tribe log to Discord
def postTribeLogToDiscord():
    global settings
    
    url = settings["webhookTribeLog"]

    if(url == ""):
        #print("Monitoring: Tribe log not posted to Discord as Webhook is blank.")
        return

    message = "Latest tribe logs"
    message = addDiscordTag(message)

    data = {
        "content": message,
        "avatar_url": "https://i.imgur.com/cMBnUQo.png"
    }
    
    files = {
        "file" : ("./screenshots/tribelog-latest.png", open("./screenshots/tribelogplayers-latest.png", 'rb'))
    }

    result = requests.post(url, data = data, files=files)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postTribeLogToDiscord() had an error:")
        print(err)

# Post tribe log to Discord
def postAlertToDiscord(message = "Alert", priority = 0):
    global settings
    
    url = settings["webhookAlert"]

    if(url == ""):
        #print("Monitoring: Alert not posted to Discord as Webhook is blank.")
        return

    message = addDiscordTag(message, priority)

    data = {
        "content": message,
        "avatar_url": "https://i.imgur.com/cMBnUQo.png"
    }
    
    files = {
        "file" : ("./screenshots/tribelog-latest.png", open("./screenshots/tribelogplayers-latest.png", 'rb'))
    }

    result = requests.post(url, data = data, files=files)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postAlertToDiscord() had an error:")
        print(err)

# Post text message to Discord
def postMessageToDiscord(message, priority = 0):
    global settings
    
    url = settings["webhookGacha"]

    if(url == ""):
        print("Monitoring: " + message + " (Priority " + str(priority) + ")")
        return

    message = addDiscordTag(message, priority)

    data = {
        "content": message,
        "avatar_url": "https://i.imgur.com/cMBnUQo.png"
    }

    result = requests.post(url, data = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postMessageToDiscord() had an error:")
        print(err)

# Used to tag people with each message according to settings.json
def addDiscordTag(message, priority = 0):
    global settings
    
    if(priority == 5):
        message = message + " " + settings["tagLevel5"]
    elif(priority == 4):
        message = message + " " + settings["tagLevel4"]
    elif(priority == 3):
        message = message + " " + settings["tagLevel3"]
    elif(priority == 2):
        message = message + " " + settings["tagLevel2"]
    elif(priority == 1):
        message = message + " " + settings["tagLevel1"]
    else:
        message = message + " " + settings["tagLevel0"]

    # Add footer to Discord message
    message = message + "\nServer: " + settings["serverName"] + " on [" + settings["accountName"] + "] Account"
    
    return message

# Tracks that a new task has been started for the purpose of detecting downtime
def trackTaskStarted(name):
    global timeLastTaskStarted
    global timeLastTaskName
    global outageLevel0
    global outageLevel1
    global outageLevel2
    global outageLevel3
    
    # set the started time to now
    timeLastTaskStarted = time.time()
    
    # set the task name to the name provided
    timeLastTaskName = name
    
    # reset the outage levels to signify nothing reported
    outageLevel0 = False
    outageLevel1 = False
    outageLevel2 = False
    outageLevel3 = False

# Needed to find if Ark is running
def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

# Checks if Ark is currently running
def checkArkRunning():
    top_windows = []
    win32gui.EnumWindows(windowEnumerationHandler, top_windows)
    arkFound = False
    for i in top_windows:
        if "ARK: Survival Evolved" in i[1]:
            arkFound = True

    return arkFound

# Useful for clicking the menus when connecting to an Ark Server
def arkClickUI(x, y, delay):
    pyautogui.moveTo(x, y, duration=0.1)
    pyautogui.click()
    time.sleep(delay)

# Uses pixel color to detect what is visible on screen
def checkArkScreen():
    # Pixel coordinates for text
    gameTextExit = pyautogui.pixel(49,824)
    gameTextSession = pyautogui.pixel(148,138)
    
    if(gameTextExit == (135, 233, 255)) or (gameTextExit == (140, 234, 255)):
        return "mainmenu"
    elif(gameTextSession == (136, 233, 255)):
        return "sessionlist"
    else:
        return "unknown"

# Launches Ark based on the gameLauncher specified in the config
def arkLaunch():
    global settings
    
    trackTaskStarted("Connecting: Launching Ark")

    # Launch Ark
    if(settings["gameLauncher"] == "Steam"):
        # Steam Launch Ark:
        webbrowser.open_new("steam://rungameid/346110")
    elif(settings["gameLauncher"] == "Epic"):
        # Epic Games Launch Ark:
        webbrowser.open_new("com.epicgames.launcher://apps/ark%3A743e47ee84ac49a1a49f4781da70e0d0%3Aaafc587fbf654758802c8e41e4fb3255?action=launch")
    time.sleep(15)

# From the Ark Main Menu open the session list
def arkOpenSessionList():
    global settings

    trackTaskStarted("Connecting: Opening Ark session list")

    # Wait for color of E in EXIT
    count = 0
    while (checkArkScreen() != "mainmenu"):
        time.sleep(1)
        count += 1
        if (count > 100):
            print("---- ERROR: arkSearchForServer() had an error:")
            print("Couldn't detect Ark main menu")
            count = 0

    # Wait for join button on epic
    if (settings["gameLauncher"] == "Epic"):
        time.sleep(5)

    # Click Join Ark
    pyautogui.moveTo(103, 523)
    pyautogui.click()


# From the Ark Main Menu searches for the server to join
def arkSearchForServer():
    global settings
    
    trackTaskStarted("Connecting: Searching for server")
    
    # Get color of E in SESSION LIST
    count = 0
    while(checkArkScreen() != "sessionlist"):
        time.sleep(1)
        count += 1
        if(count > 100):
            print("---- ERROR: arkSearchForServer() had an error:")
            print("Couldn't detect Session List page")
            break

    time.sleep(0.5)

    # Click MAP drop down
    arkClickUI(914, 136, 1.5)

    # Click ALL MAPS from MAP drop down
    arkClickUI(914, 158, 1.5)

    # Click NAME FILTER search box
    arkClickUI(590, 140, 1.5)

    # Search for server name
    pyautogui.keyDown('ctrl')
    pyautogui.press('a')
    pyautogui.keyUp('ctrl')
    pyautogui.press('backspace')
    pyautogui.typewrite(settings["serverSearch"] + " ", interval=0.05)
    time.sleep(1.5)

    # Click SESSION FILTER drop down
    arkClickUI(330, 950, 1.5)

    # Click OFFICIAL from SESSION FILTER drop down
    if(settings["gameLauncher"] == "Epic"):
        arkClickUI(330, 864, 1.5)
    else:
        arkClickUI(330, 819, 1.5)
    
    # Wait
    time.sleep(5)

# From the Ark Session List clicks refresh/join until connected
def arkJoinServer():
    # Get color of E in SESSION LIST
    while(checkArkScreen() == "sessionlist"):
        # Click REFRESH button
        arkClickUI(1229, 943, 2)

        # Wait
        time.sleep(3)

        # Click on the top server in the list
        arkClickUI(338, 242, 1.5)
        arkClickUI(338, 242, 0)
        time.sleep(1)

        # Click the JOIN button
        arkClickUI(1000, 940, 1.5)

        # Wait
        time.sleep(5)

        # Click on the top server in the list
        arkClickUI(338, 242, 1.5)
        arkClickUI(338, 242, 0)
        time.sleep(1)

        # Click the JOIN button
        arkClickUI(1000, 940, 1.5)

        # Wait
        time.sleep(5)

# A function that connects to the ark server
def launchArk():
    arkLaunch()
    arkOpenSessionList()
    arkSearchForServer()
    arkJoinServer()

# Stops the monitoring thread
def stop():
    terminate(True)

# Main thread for monitoring the health of the gacha bot
def start(locationSettings):
    global settings
    global timeLastTaskStarted
    global timeLastTaskName
    global outageLevel0
    global outageLevel1
    global outageLevel2
    global outageLevel3

    settings = locationSettings

    pause(False)
    terminate(False)

    try:
        trackTaskStarted("Started Ark Monitoring")
        while(True):
            # Make sure the bot isn't paused
            checkTerminated()
            
            # Add extra time for 360 crop plot design
            extraTime = 0
            if(settings["turnDirection"] == "360"):
                extraTime = 30
            if settings["loadGachaMethod"] == "Metal":
                extraTime += 240
            
            # Bot hasn't gone to a new task for 4min...
            if( outageLevel0 == False and ((time.time() - timeLastTaskStarted) > (240 + extraTime)) ):
                screenshotScreen()
                errorMessage = "**MONITORING:** Possible crash?!? It has been over 4min since starting the task: " + timeLastTaskName
                postMessageToDiscord(errorMessage, 1)
                outageLevel0 = True
            # Bot hasn't gone to a new task for 5min...
            if( outageLevel1 == False and ((time.time() - timeLastTaskStarted) > (300 + extraTime)) ):
                screenshotScreen()
                errorMessage = "**MONITORING:** Likely crash detected! It has been over 5min since starting the task: " + timeLastTaskName + "\n**PLEASE CHECK ON THE BOT!**"
                postMessageToDiscord(errorMessage, 1)
                errorMessage = "**MONITORING:** Attempting to unstuck the bot..."
                postMessageToDiscord(errorMessage, 0)
                pyautogui.press('F4')
                outageLevel1 = True
            # Bot hasn't gone to a new task for 7min...
            if( outageLevel2 == False and ((time.time() - timeLastTaskStarted) > (420 + extraTime)) ):
                screenshotScreen()
                errorMessage = "**MONITORING:** Crash detected! It has been over 7min since starting the task: " + timeLastTaskName + "\n**PLEASE CHECK ON THE BOT!**"
                postMessageToDiscord(errorMessage, 2)
                outageLevel2 = True
            # Bot hasn't gone to a new task for 10min...
            if( outageLevel3 == False and ((time.time() - timeLastTaskStarted) > (600 + extraTime)) ):
                screenshotScreen()
                errorMessage = "**MONITORING: CRASH DETECTED!** Bot has been stopped. It has been over 10min since starting the task: " + timeLastTaskName + "\nBot will require a manual restart."
                postMessageToDiscord(errorMessage, 1)
                pyautogui.press('F2')
                outageLevel3 = True
            # Now wait 15 seconds before we check the bot again...
            time.sleep(15)
    except Exception as e:
        print("Monitoring thread terminated.")
        errorMessage = "Monitoring thread terminated!"
        postMessageToDiscord(errorMessage, 0)
        print(str(e))