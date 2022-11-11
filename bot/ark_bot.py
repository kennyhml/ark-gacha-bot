"""
This is an API for ark GUI related functions.

"""

import json
import os
import time

import pyautogui as pg
import pydirectinput as input
from dacite import from_dict
import discord

from ark.window import ArkWindow
from bot.settings import Keybinds, DiscordSettings


class TerminatedException(Exception):
    """Raised when the script is terminated by keypress"""


class ArkBot(ArkWindow):

    """Main ArkBot class
    ----------------------------
    Responsible for handling mouse movements and clicks in the ark window
    as well as loading the configs.
    """

    __verion__ = "3.0"
    _paused = False
    _running = True
    default_avatar = "https://steamuserimages-a.akamaihd.net/ugc/883133594330098188/6F62B1436FB2C7F26F028ACCA931CB5AE7C3F4F3/?imw=512&&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=false"

    def __init__(self) -> None:
        super().__init__()
        with open("settings/keybinds.json") as f:
            self.keybinds: Keybinds = from_dict(Keybinds, json.load(f))

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, state: bool):
        self._running = state

    @property
    def paused(self):
        return self._paused

    @paused.setter
    def paused(self, state: bool):
        self._paused = state

    def check_status(self):
        if not self._running:
            raise TerminatedException

        while self._paused:
            time.sleep(0.1)
            if not self._running:
                raise TerminatedException

    def sleep(self, duration):
        # print("Sleeping", duration)
        self.check_status()
        time.sleep(duration)

    def move_to(self, x: None, y=None, convert=True):
        """Scales passed coordinates by default.

        Parameters
        -----------
        x, y: :class:`int` | `tuple`
            The coordinates to move to, normalized
        convert: :class:`bool`
            Convert the coordinate to the current resolution
        """
        self.check_status()
        x, y = pg._normalizeXYArgs(x, y)

        # we may not need to convert if the point comes from a template match
        if convert:
            x, y = self.convert_point(x, y)

        pg.moveTo(x, y)

    def click(self, button):
        """Wrapper for pyautoguis click method to check run status"""
        self.check_status()
        pg.click(button=button)

    def press(self, key):
        """Wrapper for pyautoguis press method to check run status"""
        self.check_status()
        input.press(key)

    def click_at(self, x=None, y=None, button: str = "left", delay: float = 0.1):
        """Moves to a given location and clicks with the mouse.

        Parameters:
        ----------
        pos: :class:`tuple`
            The (x,y) coordinates of the point

        button: :class:`str`
            The button to press
        """
        x, y = pg._normalizeXYArgs(x, y)
        self.move_to(self.convert_point(x, y))
        self.sleep(delay)
        pg.click(button=button)
        self.sleep(0.1)

    def set_clipboard(self, text):
        """Puts the passed text into the clipboard to allow for pasting"""
        command = "echo | set /p nul=" + text.strip() + "| clip"
        os.system(command)

    def typewrite(self, message) -> None:
        for c in message:
            input.press(c, _pause=False)

    def send_to_discord(
        self,
        webhook: discord.Webhook,
        message: str,
        file: str = None,
        name: str = "Ark Bot",
        avatar: str = default_avatar,
    ) -> None:
        """Sends the given message to the given webhook.

        Parameters:
        -----------
        webhook :class:`Webhook`:
            A discord.Webhook object to send the message to

        message :class:`str`:
            The message to send to discord

        name :class:`str`:
            The appearance name of the webhook bot, Ark Bot by default

        avatar :class:`str`:
            The url of the "profile picture" of the webhook bot, Ark Logo by default

        """
        try:
            if file:
                file = discord.File(file)
            webhook.send(content=message, username=name, avatar_url=avatar, file=file)
        except Exception as e:
            print(f"Failed to post to discord!\n{e}")


"""
inventory_template = cv2.imread("templates/inventory_template.png", cv2.IMREAD_COLOR)
invHsvLower = np.array([86, 117, 255])
invHsvUpper = np.array([106, 137, 255])
hsv = cv2.cvtColor(inventory_template, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, invHsvLower, invHsvUpper)
masked_template = cv2.bitwise_and(inventory_template, inventory_template, mask=mask)
inventory_template = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)


rr_inventory = cv2.imread("templates/receiving_remote_inventory.png", cv2.IMREAD_COLOR)
hsv = cv2.cvtColor(rr_inventory, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, invHsvLower, invHsvUpper)
masked_template = cv2.bitwise_and(rr_inventory, rr_inventory, mask=mask)
rr_inventory = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

tribelog_template = cv2.imread("templates/tribe_log.png", cv2.IMREAD_COLOR)

img = cv2.imread("templates/bed_button_corner.png", cv2.IMREAD_GRAYSCALE)
bed_button_edge = cv2.Canny(img, 100, 200)

tekPodXPBuff = cv2.imread("templates/tek_pod_xp_buff.png", cv2.IMREAD_COLOR)
tekPodXPBuff = cv2.Canny(tekPodXPBuff, 100, 200)

lookUpDelay = 3
lookDownDelay = 1.75

setFps = 25
firstRun = True
terminated = False
paused = False

hsvLower = np.array([86, 109, 255])
hsvUpper = np.array([106, 129, 255])

hsv = cv2.cvtColor(tribelog_template, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, hsvLower, hsvUpper)
masked_template = cv2.bitwise_and(tribelog_template, tribelog_template, mask=mask)
tribelog_template = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)


def getKeybinds():
    keys = {
        "arkConsole": "tab",
        "arkCrouch": "c",
        "arkDropItem": "o",
        "arkHotbar0": "0",
        "arkHotbar1": "1",
        "arkHotbar2": "2",
        "arkHotbar3": "3",
        "arkHotbar4": "4",
        "arkHotbar5": "5",
        "arkHotbar6": "6",
        "arkHotbar7": "7",
        "arkHotbar8": "8",
        "arkHotbar9": "9",
        "arkInventory": "i",
        "arkProne": "x",
        "arkTargetInventory": "f",
        "arkToggleHUD": "h",
        "arkUse": "e",
        "arkTribeLog": "l",
    }

    try:
        # Open the keybinds file
        with open("media/keybinds.json", "r") as keybinds:
            keys = json.load(keybinds)
    except Exception as e:
        # Something went wrong loading the keybinds from keybinds.json - let the user know
        errorMessage = (
            "Failed to load Keybinds from keybinds.json. Using default keybinds."
        )
        arkMonitoring.postMessageToDiscord(errorMessage, 1)

    return keys


# Load the keybinds from json
keys = getKeybinds()

# A function to update keys used when the bot is started
# This makes sure the bot is using the latest keybinds
def updateKeys():
    global keys
    keys = getKeybinds()


# passing this function True will cause most functions in this script to throw an exception
# useful to terminate a thread in a multithreaded environment
def terminate(t):
    global terminated
    terminated = t


# passing this function True will cause the bot to halt until it is passed False again
# note that terminate(True) will still kill the bot
def pause(p):
    global paused
    paused = p


# returns the paused state
def getPaused():
    global paused
    return paused


# internal functino, don't use it
# throws an exception if terminated is True
def checkTerminated():
    global paused
    global terminated

    if terminated:
        raise Exception("Ark thread terminated.")

    # if paused, halt but also die if terminated
    while paused:
        time.sleep(0.1)
        if terminated:
            raise Exception("Ark thread terminated.")


# internal function, don't use. sleeps for a period of time
def sleep(s):
    checkTerminated()
    if s > 5:
        elapsed = 0
        while elapsed < s:
            time.sleep(1)
            elapsed += 1
            checkTerminated()
    else:
        time.sleep(s)
    checkTerminated()


# used to determine whether to set gamma/fps at launch or not
def setFirstRun(f):
    global firstRun
    firstRun = f


# used to determine whether to set gamma/fps at launch or not
def getFirstRun():
    global firstRun
    return firstRun


# types t.maxfps xx into the in-game console
def limitFps():
    global setFps
    checkTerminated()
    pyautogui.press(keys["arkConsole"])
    sleep(1)
    pyautogui.typewrite("t.maxfps " + str(setFps), interval=0.001)
    sleep(1)
    pyautogui.press("enter")


# type gamma 5 into the console
def setGamma():
    checkTerminated()
    pyautogui.press(keys["arkConsole"])
    sleep(1)
    pyautogui.typewrite("gamma 5", interval=0.001)
    sleep(1)
    pyautogui.press("enter")


# make sure extended HUD is disabled
def setExtendedHud():
    if checkSpawned() == False:  # HUD already disabled
        return
    else:  # HUD enabled
        pyautogui.press(keys["arkToggleHUD"])  # attempt to toggle hud
        sleep(2)
        if checkSpawned() == True:  # HUD couldn't be disabled
            errorMessage = (
                "**Failed to disable HUD!** Bot will fail to enter tek pod reliably."
            )
            arkMonitoring.postMessageToDiscord(errorMessage, 1)
        else:  # Couldn't enable HUD
            print("Disabled HUD successfully.")


# checks for when the bot is spawned
def checkSpawned():
    spawnedPixel = pyautogui.pixel(16, 50)
    if spawnedPixel == (255, 179, 63):
        return True
    return False


# sets the look up/down delays plus the FPS which affects turning speed
def setParams(up, down, fps):
    global lookUpDelay
    global lookDownDelay
    global setFps
    lookUpDelay = up
    lookDownDelay = down
    setFps = fps


# looks up 90 degrees
def lookUp():
    global lookUpDelay
    checkTerminated()
    pyautogui.keyDown("up")
    sleep(lookUpDelay)
    pyautogui.keyUp("up")


# looks down 90 degrees
def lookDown():
    global lookDownDelay
    checkTerminated()
    pyautogui.keyDown("down")
    sleep(lookDownDelay)
    pyautogui.keyUp("down")


# types a bed name into the search entry on the respawn screen
def enterBedName(name):
    checkTerminated()
    pyautogui.moveTo(336, 986, duration=0.1)
    pyautogui.click()
    pyautogui.keyDown("ctrl")
    pyautogui.press("a")
    pyautogui.keyUp("ctrl")
    pyautogui.press("backspace")
    pyautogui.typewrite(name, interval=0.001)
    sleep(0.5)


# returns true if there is a button to respawn next to the bed name entry
def checkBedButtonEdge():
    checkTerminated()
    img = screen.getGrayScreen()[950:1100, 580:620]
    img = cv2.Canny(img, 100, 200)
    res = cv2.matchTemplate(img, bed_button_edge, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > 2500000:
        return True
    return False


def detectWhiteFlash():
    roi = screen.getScreen()[700:900, 650:1920]
    res1 = np.all([roi == 255])
    return res1


def setSens():
    checkTerminated()
    pyautogui.press("esc")
    sleep(2)
    pyautogui.moveTo(960, 315)  # options
    pyautogui.click()
    sleep(2)
    pyautogui.moveTo(1810, 450)  # sens left
    pyautogui.click()
    sleep(0.3)
    pyautogui.moveTo(1810, 490)  # sens down
    pyautogui.click()
    pyautogui.moveTo(1400, 150)  # apply
    pyautogui.click()
    sleep(0.5)
    pyautogui.moveTo(1600, 150)  # save
    pyautogui.click()
    sleep(2)
    pyautogui.moveTo(960, 275)  # resume
    pyautogui.click()
    sleep(1)


# spawns on a bed named bedName at click coords x, y
# requires the player to have opened a bed to fast travel first
def bedSpawn(bedName, x, y, singlePlayer=False):
    global firstRun
    checkTerminated()
    sleep(1.5)
    enterBedName(bedName)
    sleep(0.25)
    pyautogui.moveTo(x, y)
    sleep(0.25)
    pyautogui.click()
    sleep(0.25)
    if checkBedButtonEdge:
        pyautogui.moveTo(755, 983)
        sleep(0.25)
        pyautogui.click()

        # We don't have extended HUD enabled yet - so use old method for spawning
        if firstRun == True:
            count = 0
            while detectWhiteFlash() == False:
                time.sleep(0.1)
                count += 1
                if count > 200:
                    break

            sleep(14)

            firstRun = False
            limitFps()  # Limit FPS so turning is consistent
            setGamma()  # Set gamma so template image matching is consistent
            setSens()
            pyautogui.scroll(1)  # Scroll up to enter first person
            setExtendedHud()
        else:
            count = 0
            while detectWhiteFlash() == False:
                time.sleep(0.1)
                count += 1
                if count > 200:
                    break
            sleep(13)

        if singlePlayer:
            sleep(1.0)
            lookDown()
            pyautogui.keyDown(keys["arkUse"])
            sleep(1.0)
            pyautogui.moveTo(1250, 550)
            sleep(1.0)
            pyautogui.keyUp(keys["arkUse"])
            sleep(1.0)
            pyautogui.press(keys["arkUse"])
            sleep(1.0)
            step("left", 1.0)

        pyautogui.press(keys["arkCrouch"])
        return True
    else:
        errorMessage = "**Stuck on bed screen!** Likely failed to spawn!"
        arkMonitoring.postMessageToDiscord(errorMessage, 1)
        return False


# returns true if an inventory is open
def inventoryIsOpen():  # {{{
    checkTerminated()
    roi = screen.getScreen()[90:150, 100:300]
    screen_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(screen_hsv, invHsvLower, invHsvUpper)
    masked_screen = cv2.bitwise_and(roi, roi, mask=mask)
    gray_screen = cv2.cvtColor(masked_screen, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, inventory_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val > 50000000.0:
        return True
    return False


def receivingRemoteInventory():
    checkTerminated()
    roi = screen.getScreen()[230:940, 1240:1820]
    screen_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(screen_hsv, invHsvLower, invHsvUpper)
    masked_screen = cv2.bitwise_and(roi, roi, mask=mask)
    gray_screen = cv2.cvtColor(masked_screen, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, rr_inventory, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val > 30000000.0:
        return True
    return False


# returns true if the tribe log is open
def tribelogIsOpen():
    checkTerminated()
    roi = screen.getScreen()[80:150, 1320:1510]
    screen_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(screen_hsv, hsvLower, hsvUpper)
    masked_screen = cv2.bitwise_and(roi, roi, mask=mask)
    gray_screen = cv2.cvtColor(masked_screen, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, tribelog_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > 50000000:
        return True
    return False


# closes an inventory
def closeInventory():  # {{{
    checkTerminated()
    while inventoryIsOpen() == True:
        pyautogui.moveTo(1816, 37)
        pyautogui.click()
        count = 0
        while inventoryIsOpen():
            count += 1
            if count > 20:
                break
            sleep(0.1)
    time.sleep(0.2)


def openTribeLog():
    checkTerminated()
    pyautogui.press(keys["arkTribeLog"])
    sleep(2.0)
    while tribelogIsOpen() == False:
        checkTerminated()
        pyautogui.press(keys["arkTribeLog"])
        sleep(2.0)


def closeTribeLog():
    checkTerminated()
    while tribelogIsOpen() == True:
        pyautogui.press("escape")
        count = 0
        while tribelogIsOpen():
            count += 1
            if count > 20:
                break
            sleep(0.2)


# crafts an item in a remote inventory (not the player inventory)
def craft(item, timesToPressA):
    checkTerminated()
    searchStructureStacks(item)
    pyautogui.moveTo(1290, 280)
    pyautogui.click()
    for i in range(0, timesToPressA):
        pyautogui.press("a")
        sleep(0.25)


# searches the players ivnventory
def searchMyStacks(thing):  # {{{
    checkTerminated()
    pyautogui.moveTo(144, 191)
    pyautogui.click()
    sleep(0.1)
    pyautogui.keyDown("ctrl")
    sleep(0.1)
    pyautogui.press("a")
    pyautogui.keyUp("ctrl")
    pyautogui.typewrite(thing, interval=0.001)
    sleep(0.1)


# searches a remote inventory
def searchStructureStacks(thing):
    checkTerminated()
    pyautogui.moveTo(1322, 191)
    pyautogui.click()
    sleep(0.1)
    pyautogui.keyDown("ctrl")
    sleep(0.1)
    pyautogui.press("a")
    pyautogui.keyUp("ctrl")
    pyautogui.typewrite(thing, interval=0.001)
    sleep(0.1)


def takeStacks(thing, count):  # {{{
    checkTerminated()
    searchStructureStacks(thing)
    pyautogui.moveTo(1287, 290)
    pyautogui.click()
    for i in range(count):
        pyautogui.press("t")
        sleep(1)


# }}}
def takeAll(thing=""):
    checkTerminated()
    if thing != "":
        sleep(0.1)
        pyautogui.moveTo(1285, 180)
        pyautogui.click()
        sleep(0.1)
        pyautogui.keyDown("ctrl")
        pyautogui.press("a")
        pyautogui.keyUp("ctrl")
        pyautogui.typewrite(thing, interval=0.001)
    pyautogui.moveTo(1424, 190)
    pyautogui.click()
    sleep(0.5)


def transferAll(thing=""):  # {{{
    checkTerminated()
    if thing != "":
        pyautogui.moveTo(198, 191)
        pyautogui.click()
        sleep(0.2)
        pyautogui.keyDown("ctrl")
        pyautogui.press("a")
        pyautogui.keyUp("ctrl")
        pyautogui.typewrite(thing, interval=0.001)
        sleep(0.1)
    pyautogui.moveTo(351, 186)
    pyautogui.click()
    sleep(0.1)


def transferStacks(thing, count):  # {{{
    checkTerminated()
    pyautogui.moveTo(198, 191)
    pyautogui.click()
    sleep(0.1)
    pyautogui.keyDown("ctrl")
    pyautogui.press("a")
    pyautogui.keyUp("ctrl")
    pyautogui.typewrite(thing, interval=0.001)
    sleep(0.1)
    counter = 0
    pyautogui.moveTo(170, 280)
    pyautogui.click()
    sleep(0.2)
    while counter < count:
        pyautogui.press("t")
        sleep(0.5)
        counter += 1


def openInventory(retries=20):
    checkTerminated()
    pyautogui.press(keys["arkTargetInventory"])
    sleep(0.2)
    count = 0
    while inventoryIsOpen() == False:
        checkTerminated()
        count += 1
        if count > retries:
            return False
        sleep(0.1)
    while receivingRemoteInventory():
        checkTerminated()
        time.sleep(0.5)

    return True


def tTransferTo(nRows):
    checkTerminated()
    sleep(0.5)
    pyautogui.moveTo(167, 745, 0.1)
    pyautogui.click()
    for j in range(nRows):  # transfer a few rows back to the gacha
        for i in range(6):
            pyautogui.moveTo(167 + (i * 95), 745, 0.1)
            pyautogui.press("t")
            checkTerminated()


def tTransferFrom(nRows):
    checkTerminated()
    pyautogui.moveTo(1288, 280, 0.1)
    pyautogui.click()
    for j in range(nRows):
        for i in range(6):
            pyautogui.moveTo(1288 + (i * 95), 280, 0.05)
            pyautogui.press("t")
            checkTerminated()


def getBedScreenCoords():
    checkTerminated()
    roi = screen.getScreen()

    lower_blue = np.array([90, 200, 200])
    upper_blue = np.array([100, 255, 255])

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    masked_template = cv2.bitwise_and(roi, roi, mask=mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    bed_template = cv2.imread("templates/bed_icon_template.png", cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(bed_template, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    masked_template = cv2.bitwise_and(bed_template, bed_template, mask=mask)
    bed_template = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, bed_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val > 8000000:
        return (max_loc[0] + 14, max_loc[1] + 14)
    return None


def dropItems(thing):
    checkTerminated()
    pyautogui.moveTo(198, 191)
    pyautogui.click()
    sleep(0.2)
    pyautogui.keyDown("ctrl")
    pyautogui.press("a")
    pyautogui.keyUp("ctrl")
    if thing == "":
        pyautogui.press("backspace")
    else:
        pyautogui.typewrite(thing, interval=0.001)
    sleep(0.5)
    pyautogui.moveTo(412, 190)
    pyautogui.click()


def accessBed():
    checkTerminated()
    count = 0
    while getBedScreenCoords() == None:
        lookDown()
        pyautogui.press(keys["arkUse"])
        sleep(1.5)
        if inventoryIsOpen():
            closeInventory()
        count += 1
        if count > 5:
            return False
    return True


def takeAllOverhead():
    checkTerminated()
    lookUp()
    openInventory()
    takeAll()
    closeInventory()
    lookDown()


def depositOverhead():
    checkTerminated()
    lookUp()
    pyautogui.press(keys["arkUse"])
    lookDown()


def step(key, delay):
    checkTerminated()
    pyautogui.keyDown(key)
    sleep(delay)
    pyautogui.keyUp(key)


def crystalHotBarUse():
    pyautogui.press(keys["arkHotbar2"])
    pyautogui.press(keys["arkHotbar3"])
    pyautogui.press(keys["arkHotbar4"])
    pyautogui.press(keys["arkHotbar5"])
    pyautogui.press(keys["arkHotbar6"])
    pyautogui.press(keys["arkHotbar7"])
    pyautogui.press(keys["arkHotbar8"])
    pyautogui.press(keys["arkHotbar9"])
    pyautogui.press(keys["arkHotbar0"])


def crystalHotBarSetup():
    # put crystals on hotbars by double clicking the crystals one by one
    for _ in range(0, 10):
        pyautogui.click(167, 280, clicks=2)
        sleep(2)
    # remove crystal from slot 1
    pyautogui.moveTo(690, 1046, 0.1)
    pyautogui.dragTo(400, 700, 1, button="left")


    # old method: drags the crystals down one by one
    # drags crystals from the inventory onto the bot's hotbar
    hotbarX = 749 # X position of 2 on hotbar
    for _ in range(0, 9):
        pyautogui.moveTo(167, 280, 0.1) # move mouse over the crystal
        pyautogui.dragTo(hotbarX, 1046, 0.1, button='left') # drag crystal to hotbar
        hotbarX += 60 # +60 is enough to go to next hotbar slot
        sleep(1)



def crystalHotBarUseHoldStart():
    pyautogui.keyDown(keys["arkHotbar2"])
    pyautogui.keyDown(keys["arkHotbar3"])
    pyautogui.keyDown(keys["arkHotbar4"])
    pyautogui.keyDown(keys["arkHotbar5"])
    pyautogui.keyDown(keys["arkHotbar6"])
    pyautogui.keyDown(keys["arkHotbar7"])
    pyautogui.keyDown(keys["arkHotbar8"])
    pyautogui.keyDown(keys["arkHotbar9"])
    pyautogui.keyDown(keys["arkHotbar0"])


def crystalHotBarUseHoldStop():
    pyautogui.keyUp(keys["arkHotbar2"])
    pyautogui.keyUp(keys["arkHotbar3"])
    pyautogui.keyUp(keys["arkHotbar4"])
    pyautogui.keyUp(keys["arkHotbar5"])
    pyautogui.keyUp(keys["arkHotbar6"])
    pyautogui.keyUp(keys["arkHotbar7"])
    pyautogui.keyUp(keys["arkHotbar8"])
    pyautogui.keyUp(keys["arkHotbar9"])
    pyautogui.keyUp(keys["arkHotbar0"])


def harvestCropStack(fruit, lookUpTime=1.0):
    checkTerminated()
    lookDown()
    step("up", lookUpTime)

    for i in range(4):
        if openInventory(80):
            takeAll(fruit)
            transferAll()
            sleep(0.2)
            closeInventory()
        step("up", 0.09)

    pyautogui.press(keys["arkCrouch"])
    step("down", 0.4)

    for i in range(3):
        if openInventory(80):
            takeAll(fruit)
            transferAll()
            sleep(0.2)
            closeInventory()
        step("up", 0.09)


def checkConsole():
    spawnedPixel = pyautogui.pixel(1070, 1070)
    if spawnedPixel == (0, 0, 0):
        return True
    return False


def openConsole():
    checkTerminated()
    for i in range(30):
        if checkConsole() == True:  # Console already opened
            return True
        else:
            if i > 0:
                pyautogui.press("esc")  # attempt to close any menu
                time.sleep(1)
                if i % 5 == 0:  # only click every 5th attempt
                    pyautogui.click(1000, 1000)  # attempt to click to help close a menu
                    time.sleep(1)
        pyautogui.press(keys["arkConsole"])  # attempt to open console
        checkTerminated()
        time.sleep(1)
    # Failed to open the console
    return False


def closeConsole():
    checkTerminated()
    if checkConsole() == True:  # Console already opened
        pyautogui.press("esc")


# Enters a tek pod
def tekPodEnter():
    checkTerminated()
    pyautogui.press(keys["arkCrouch"])
    tekPodLayOn()
    # if not in a tek pod keep trying
    while checkTekPodEntered() == False:
        tekPodLayOn()


def tekPodLayOn():
    checkTerminated()
    lookDown()
    sleep(1)
    pyautogui.keyDown(keys["arkUse"])
    sleep(1)
    pydirectinput.moveTo(1266, 541, duration=0.1)
    sleep(0.1)
    pydirectinput.moveTo(1266, 540, duration=0.1)
    sleep(0.5)
    pyautogui.keyUp(keys["arkUse"])
    sleep(3)


# Checks the tek pod was entered
def checkTekPodEntered():
    checkTerminated()
    img = screen.getScreen()[980:1080, 1350:1800]

    img = cv2.Canny(img, 100, 200)
    res = cv2.matchTemplate(img, tekPodXPBuff, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    max_val_check = 25000000
    if max_val > max_val_check:
        # print("checkTekPodEntered(): Tek pod successfully entered with max_val: " + str(max_val) + " (needs to be > " + str(max_val_check) + ")")
        return True
    return False


# Leaves a tek pod
def tekPodLeave():
    checkTerminated()
    count = 0
    while getBedScreenCoords() == None:
        pyautogui.press(keys["arkUse"])
        sleep(2)
        lookDown()
        sleep(1)
        pyautogui.press(keys["arkUse"])
        sleep(1)
        count += 1
        if count > 5:
            return False
    return True
"""
