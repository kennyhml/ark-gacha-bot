import logging
from dataclasses import dataclass
from datetime import datetime
from threading import Thread

import cv2 as cv
import discord
import numpy as np
from mss.screenshot import ScreenShot
from PIL import Image
from pytesseract import pytesseract as tes

from ark.exceptions import LogsNotOpenedError
from bot.ark_bot import ArkBot

# configure logging file, helps debugging why certain stuff didnt get posted
now = datetime.now()
now = now.strftime("%d-%m-%H-%M")
logging.basicConfig(
    level=logging.INFO,
    filename=f"logs/tribelogs {now}.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# common tesseract mistakes to account for in any tribelog messages
CONTENTS_MAPPING = {
    "{": "(",
    "}": ")",
    "[": "(",
    "]": ")",
    "((": "(",
    "))": ")",
    "Owll": "Owl)",
    "\n": " ",
    "!!": "!",
    "Lvi": "Lvl",
    "Gaby": "Baby",
    "destroved": "destroyed",
    "destroyedl": "destroyed!",
    "destroyedl!": "destroyed!",
    "destrayed!": "destroyed!",
    "destraved": "destroyed",
    "Giaanotosaurus": "Giganotosaurus",
    "Large Gear Trap": "Large Bear Trap",
    "C4 Charae": "C4 Charge",
    "C4 Charce": "C4 Charge",
    "C4& Charae": "C4 Charge",
    "C4 Charace": "C4 Charge",
    "(Pin Coded!": "(Pin Coded)",
    "(Pin Codedl": "(Pin Coded)",
    "”": "''",
    "“": "'",
    '"': "'",
    "‘": "'",
    "’": "'",
    "''": "'",
    "Dcorframe": "Doorframe",
    "Ccorframe": "Doorframe",
    "Doaorframe": "Doorframe",
    "Doarframe": "Doorframe",
    "Ceilina": "Ceiling",
    "Tek Ficor": "Tek Floor",
    "iTek Turret!": "(Tek Turret)",
    "iTek Turret": "(Tek Turret",
    " Tek Turreti": " (Tek Turret)",
    "(Tek Turret!": "(Tek Turret)",
    " Tek Turret)": " (Tek Turret)",
    "fCarbonemvsl": "(Carbonemys)",
    "Carbonemvs": "Carbonemys",
    "(Carbonemysl!": "(Carbonemys)!",
    "iCarbonemysl": "(Carbonemys)",
    "iCarbonemysi": "(Carbonemys)",
    "(Shadowmane!": "(Shadowmane)!",
    "Desmadus": "Desmodus",
    "Desmoadus": "Desmodus"
}

# RGB to denoise with if the templates are located in the tribelog message
DENOISE_MAPPING = {
    (255, 0, 0): [
        "templates/tribelog_red_your.png",
        "templates/tribelog_enemy_destroyed.png",
    ],
    (208, 3, 211): "templates/tribelog_purple_your.png",
    (158, 76, 76): "templates/tribelog_sensor.png",
}

# Denoise RGB indicating a certain tribelog event
EVENT_MAPPING = {
    (255, 0, 0): "Something destroyed!",
    (208, 3, 211): "Something killed!",
    (158, 76, 76): "Tek Sensor triggered!",
}

# common mistakes to replace in the daytime OCR
DAYTIME_MAPPING = {
    "|": "",
    "I": "1",
    "v": "y",
    "O": "0",
    ".": ",",
    "l": "1",
    "i": "1",
    "S": "5",
    "B": "8",
    "Dayy": "Day",
    ";": "",
}


@dataclass
class TribeLogMessage:
    """Represents a single message in the tribe log"""

    day: str
    action: str
    content: str

    def __repr__(self):
        return f"{self.day} {self.action} {self.content}"


class TribeLog(ArkBot):
    """Represents the ark tribe log.
    Stores all previous logs as list of TribeLogMessages.
    """

    sensor_icon = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/1/16/Tek_Sensor_%28Genesis_Part_1%29.png/revision/latest?cb=20200226080818"
    destroyed_icon = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/4/46/C4_Charge.png/revision/latest/scale-to-width-down/228?cb=20150615094656"
    dino_killed_icon = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/6/61/Tek_Bow_%28Genesis_Part_2%29.png/revision/latest?cb=20210603191501"
    LOG_REGION = 1340, 180, 460, 820

    def __init__(
        self, alert_webhook: discord.Webhook, log_webhook: discord.Webhook
    ) -> None:
        super().__init__()
        self._tribe_log: list[TribeLogMessage] = []
        self.alert_webhook = alert_webhook
        self.log_webhook = log_webhook

    def __repr__(self) -> str:
        return "".join(f"{log_message}\n" for log_message in self._tribe_log)

    def is_open(self) -> bool:
        return (
            self.locate_template(
                "templates/tribe_log.png", region=(1300, 70, 230, 85), confidence=0.8
            )
            is not None
        )

    def open(self) -> None:
        """Opens the tribe log. Tries up to 20 times and raises a
        `LogsNotOpenedError` if unsuccessful.
        """
        c = 0
        while not self.is_open():
            self.press(self.keybinds.logs)
            if self.await_open():
                break
            c += 1
            if c > 20:
                raise LogsNotOpenedError

        # litle buffer in case timer pops or server lags
        self.sleep(2)

    def close(self) -> None:
        """Closes the tribelogs."""
        while self.is_open():
            self.press("esc")
            self.await_closed()

    def await_open(self) -> bool:
        """Awaits for the logs to be open to be time efficient.

        to do: write a parent `await` function that does this stuff
        """
        c = 0
        while not self.is_open():
            self.sleep(0.1)
            c += 1
            if c > 50:
                return False
        return True

    def await_closed(self) -> bool:
        """Awaits for the logs to be open to be time efficient."""
        c = 0
        while self.is_open():
            self.sleep(0.1)
            c += 1
            if c > 50:
                return False
        return True

    def check_tribelogs(self) -> None:
        logging.log(logging.INFO, "Updating tribelogs...")
        self.open()
        self.grab_screen(self.LOG_REGION, "temp/tribelog.png")
        self.close()
        Thread(target=self.update_tribelogs, name="Updating tribelogs...").start()

    def update_tribelogs(self) -> None:
        """Returns a list of tuples containing the daytime as string and the
        corresponding log message image
        """

        log_img = Image.open("temp/tribelog.png")
        # sort days from top to bottom by y coordinate so we can get the message frame
        day_points = self.get_day_occurrences()
        days_in_order = sorted([day for day in day_points], key=lambda t: t[1])
        logging.log(logging.INFO, f"{len(day_points)} days found to check...")

        messages = []
        for i, box in enumerate(days_in_order):
            # grab day region
            day_region = (int(box[0] - 5), int(box[1] - 5), box[0] + 170, box[1] + 15)

            # each frame ends where the next frame y starts
            try:
                message_region = (
                    int(box[0] - 5),
                    int(box[1] - 5),
                    440,
                    int(days_in_order[i + 1][1] - 2),
                )

            # not worth checking the last log message because its shadowed
            except IndexError:
                continue

            # OCR the day and validate it, continue if the day is invalid
            if not (day := self.get_daytime(log_img.crop(day_region))):
                continue

            # OCR the contents, None if its irrelevant
            if not (content := self.get_message_contents(log_img.crop(message_region))):
                continue
            logging.log(logging.INFO, f"Found {day} with contents {content}")

            if not self.day_is_known(day):
                message = TribeLogMessage(day, *content)
                messages.append(message)

                if self._tribe_log:
                    logging.log(logging.INFO, f"Sending an alert for {message}!")
                    self.send_alert(message)

        logging.log(logging.INFO, f"New messages added: {messages}!")
        self._tribe_log += reversed(messages)
        self.delete_old_logs()
        self.send_to_discord(
            self.log_webhook,
            "Current tribelogs:",
            file="temp/tribelog.png",
            name="Ling Ling Logs",
            avatar="https://i.kym-cdn.com/entries/icons/original/000/017/373/kimjongz.PNG",
        )
        logging.log(logging.INFO, f"Updated tribelog: {self._tribe_log}")

    def send_alert(self, message: TribeLogMessage) -> None:
        """Sends an alert to discord with the given message."""
        # create our webhook, action and description in the header
        embed = discord.Embed(
            type="rich",
            title=message.action,
            description=message.day,
            color=0xFF0000,
        )

        embed.add_field(name=f"{message.content}", value="\u200b")
        # get a suitable thumbnail
        match message.action:
            case "Something destroyed!":
                thumbnail_url = self.destroyed_icon
            case "Tek Sensor triggered!":
                thumbnail_url = self.sensor_icon
            case "Something killed!":
                thumbnail_url = self.dino_killed_icon

        embed.set_thumbnail(url=thumbnail_url)
        embed.set_footer(text="Ling Ling on top!")

        # mention if a relevant event happened
        mention = any(msg in message.content for msg in ("enemy survivor", "Pin Coded"))

        # send the message
        self.alert_webhook.send(
            content="@everyone" if mention else "",
            avatar_url="https://i.kym-cdn.com/entries/icons/original/000/017/373/kimjongz.PNG",
            embed=embed,
            username="Ling Ling Look Logs",
        )

    def get_day_occurrences(self) -> list[tuple]:
        """Retuns a list of all days, each day being a
        tuple containing top, left, widht and height"""
        return self.locate_all_in_image(
            "templates/tribelog_day.png", "temp/tribelog.png", confidence=0.8
        )

    def get_daytime(self, image: str | Image.Image | ScreenShot) -> str | None:
        """Gets the daytime in the given image. The image is denoised and common
        mistakes are filtered out, then the day is validated.

        Parameters:
        -----------
        image :class:`str`| `Image.Image` | `ScreenShot`:
            The image to get the daytime of

        Returns:
        -----------
        daytime :class:`str` | `None`:
            The daytime to be seen in the image or `None` if it is invalid / undetermined.
        """
        # prepare the image, denoising upscaling dilating etc...
        prepared = self.denoise_text(
            image, denoise_rgb=(180, 180, 180), variance=18, upscale=True, upscale_by=2
        )

        # get tesseract result, whitelisting seems to not be working too well.
        raw_day_string = tes.image_to_string(prepared, config="--psm 6 -l eng")

        # replace the potentially mistaken characters
        for c in DAYTIME_MAPPING:
            raw_day_string = raw_day_string.replace(c, DAYTIME_MAPPING[c])
        day_string = raw_day_string

        try:
            # split the day into the parts we care about
            day = day_string.split(" ")[1].replace(",", "")
            hour, min, sec = (day_string.split(" ")[2].split(":")[i] for i in range(3))

            # check that all values make logical sense
            if any((len(day) > 5, int(hour) > 24, int(min) > 60, int(sec) > 60)):
                return None

        except Exception as e:
            logging.log(logging.WARNING, f"Day {day_string} invalid!\n{e}")
            return None

        return day_string

    def get_message_contents(
        self, image: str | Image.Image | ScreenShot
    ) -> tuple[str, str]:
        """Gets the contents of the given tribelog message image.

        Parameters:
        ------------
        image :class:`str`| `Image.Image` | `ScreenShot`:
            The image to get the contents of

        Returns:
        ------------
        contents :class:`tuple`:
            The contents of the image as a tuple of strings containing the action
            such as "Something destroyed!" and the actual contents.
        """
        # grab the rgb we need to use to denoise the image properly
        # if None there is no meaningful contents in the image
        denoise_rgb = self.get_denoise_rgb(image)
        if not denoise_rgb:
            return None

        # prepare the image for tesseract, the purple RGB needs higher variance
        # than the others. Dilating seems to give accurate results in this case.
        prepared_img = self.denoise_text(
            image,
            denoise_rgb,
            30 if not denoise_rgb == (208, 3, 211) else 50,
            upscale=True,
            upscale_by=2,
        )

        # get the raw tesseract result, assuming a uniform block of text.
        raw_res: str = tes.image_to_string(prepared_img, config="--psm 6 -l eng")

        # replace the common known mistakes that tend to happen
        for c in CONTENTS_MAPPING:
            raw_res = raw_res.replace(c, CONTENTS_MAPPING[c])
        filtered_res = raw_res
        event = EVENT_MAPPING[denoise_rgb]

        if event == "Tek Sensor triggered!":
            sensor_event = self.get_sensor_event(image)
            filtered_res = f"'{filtered_res.rstrip()}' triggered by {sensor_event}!"
        return event, filtered_res

    def get_denoise_rgb(self, image: str | Image.Image | ScreenShot) -> tuple:
        """Gets the RGB to denoise for in the given image.

        Parameters:
        ------------
        image :class:`str`| `Image.Image` | `ScreenShot`:
            The image to be denoised

        Returns:
        -----------
        denoise_rgb :class:`tuple`:
            The rgb  value to denoise in the image for a good result
        """
        # absolute pain, need to convert to BGR and back for some reason
        if isinstance(image, ScreenShot):
            image = np.array(image)
            image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        elif isinstance(image, str):
            image = cv.imread(image, 1)

        else:
            # convert PIL image to np array for template matching
            image = np.array(image)
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        # filter out auto-decay
        if (
            self.locate_in_image(
                "templates/tribelog_auto_decay.png", image, confidence=0.8
            )
            is not None
        ):
            return None

        # find the RGB we need to denoise
        for rgb in DENOISE_MAPPING:
            template = DENOISE_MAPPING[rgb]

            # only 1 template to match
            if not isinstance(template, list):
                if self.locate_in_image(template, image, confidence=0.8) is not None:
                    return rgb
                continue

            # multiple templates to match, check if any match
            if any(
                self.locate_in_image(template, image, confidence=0.8) is not None
                for template in DENOISE_MAPPING[rgb]
            ):
                return rgb

    def get_sensor_event(self, image) -> str:
        if (
            self.locate_in_image(
                "templates/tribelog_enemy_survivor.png", image, confidence=0.8
            )
            is not None
        ):
            return "an enemy survivor"
        if (
            self.locate_in_image(
                "templates/tribelog_enemy_dino.png", image, confidence=0.8
            )
            is not None
        ):
            return "an enemy dinosaur"
        return "something (friendly or undetermined)"

    def day_is_known(self, day) -> bool:
        """Checks if the given day has already been recognized.

        Parameters:
        ------------
        day :class:`str`:
            The day to check for

        Returns:
        ------------
        `True` if the day is already in the database else `False`
        """
        logging.log(logging.INFO, f"Checking if {day} is already in database.")
        # initial log save, no days known yet
        if not self._tribe_log:
            return False

        # typecast both days to integer to use integer operations
        day_int = int(day.split(" ")[1].replace(",", ""))
        most_recent_day = int(self._tribe_log[-1].day.split(" ")[1].replace(",", ""))

        # check if the day to check is smaller or too high compared to our most recent day
        if day_int < most_recent_day or day_int > most_recent_day + 20:
            return True

        # check if any of the saved messages already contain the day
        for message in self._tribe_log:
            if day.strip() == message.day.strip():
                return True

    def delete_old_logs(self) -> None:
        """Deletes all but the past 30 messages in the tribelogs."""
        if len(self._tribe_log) < 30:
            logging.log(logging.INFO, "Not enough tribelog events to delete.")
            return

        old_length = len(self._tribe_log)
        self._tribe_log = self._tribe_log[-30:]
        logging.log(logging.INFO, f"Deleted {old_length - len(self._tribe_log)} old tribelog messages.")
