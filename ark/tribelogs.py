from dataclasses import dataclass

import numpy as np
from mss.screenshot import ScreenShot
from PIL import Image
from pytesseract import pytesseract as tes
import discord
from bot.ark_bot import ArkBot
from mss import tools
import cv2 as cv

CONTENTS_MAPPING = {
    "{": "(",
    "}": ")",
    "[": "(",
    "]": ")",
    "\n": " ",
    "!!": "!",
    "Lvi": "Lvl",
    "Gaby": "Baby",
    "destroved": "destroyed",
    "destroyedl": "destroyed!",
    "destroyedl!": "destroyed!",
    "destrayed!": "destroyed!",
    "Giaanotosaurus": "Giganotosaurus",
    "Large Gear Trap": "Large Bear Trap",
    "C4 Charae": "C4 Charge",
    "”": "''",
    "“": "'",
    '"': "'",
    "‘": "'",
    "’": "'",
    "''": "'",
    "Dcorframe": "Doorframe",
    "Ccorframe": "Doorframe",
    "Doaorframe": "Doorframe",
    "iTek Turret!": "(Tek Turret)",
    "iTek Turret": "(Tek Turret",
    " Tek Turreti": " (Tek Turret)",
    "(Tek Turret!": "(Tek Turret)"
}


@dataclass
class TribeLogMessage:
    day: str
    action: str
    content: str

    def __repr__(self):
        return f"{self.day} {self.action} {self.content}"


class TribeLog(ArkBot):

    alert_webhook = "https://discord.com/api/webhooks/1045378199737073714/HtrFyfX3Ya2EPgWJJgwlIxxUmJeTcP0jj9xSatizBEqNOxojyl4FA4K7gK-_LzMqxhQp"
    logs_webhook = "https://discord.com/api/webhooks/1045378297321771019/079MeqEVvJdfsDCX-l6tSLi2OvP9yvHdSdMrYyGZbNkm7VDlcfer399UOwZtekPXIeFm"
    sensor_icon = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/1/16/Tek_Sensor_%28Genesis_Part_1%29.png/revision/latest?cb=20200226080818"
    destroyed_icon = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/4/46/C4_Charge.png/revision/latest/scale-to-width-down/228?cb=20150615094656"
    dino_killed_icon = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/6/61/Tek_Bow_%28Genesis_Part_2%29.png/revision/latest?cb=20210603191501"

    LOG_REGION = 1340, 180, 460, 820
    DENOISE_MAPPING = {
        (255, 0, 0): [
            "templates/tribelog_red_your.png",
            "templates/tribelog_enemy_destroyed.png",
        ],
        (208, 3, 211): "templates/tribelog_purple_your.png",
        (158, 76, 76): "templates/tribelog_sensor.png",
    }

    def __init__(self) -> None:
        super().__init__()
        self._tribe_log: list[TribeLogMessage] = []

    def __repr__(self) -> str:
        return "".join(f"{log_message}\n" for log_message in self._tribe_log)

    def send_alert(self, message: TribeLogMessage) -> None:

        webhook = discord.Webhook.from_url(
                self.alert_webhook,
                adapter=discord.RequestsWebhookAdapter(),
            )

        embed = discord.Embed(
            type="rich",
            title=message.action,
            description=message.day,
            color=0xFC97E8,
        )

        embed.add_field(name=f"{message.content}", value="\u200b")

        if message.action == "Something destroyed!":
            avatar = self.destroyed_icon
        elif message.action == "Tek Sensor triggered!":
            avatar = self.sensor_icon

        elif message.action == "Something destroyed!":
            avatar = self.destroyed_icon

        embed.set_thumbnail(url=avatar)
        embed.set_footer(text="Ling Ling on top!")

        webhook.send(
            embed=embed,
            username="Ling Ling",
        )

    def is_open(self) -> bool:
        return (
            self.locate_template(
                "templates/tribe_log.png", region=(1300, 70, 230, 85), confidence=0.8
            )
            is not None
        )

    def get_day_occurrences(self) -> list[tuple]:
        """Retuns a list of all days, each day being a
        tuple containing top, left, widht and height"""
        return self.locate_all_template(
            "templates/tribelog_day.png", region=self.LOG_REGION, confidence=0.8
        )

    def get_log_messages(self) -> list[TribeLogMessage]:
        """Returns a list of tuples containing the daytime as string and the
        corresponding log message image
        """
        # sort days from top to bottom by y coordinate so we can get the message frame
        day_points = self.get_day_occurrences()
        days_in_order = sorted([day for day in day_points], key=lambda t: t[1])

        messages = []
        for i, box in enumerate(days_in_order):
            # grab day region
            day_region = (int(box[0] - 5), int(box[1] - 5), 175, 20)

            # each frame ends where the next frame y starts
            try:
                message_region = (
                    int(box[0] - 5),
                    int(box[1] - 5),
                    445,
                    int(days_in_order[i + 1][1] - box[1] + 3),
                )

            # not worth checking the last log message because its shadowed
            except IndexError:
                continue

            # OCR the day and validate it, continue if the day is invalid
            if not (day := self.get_daytime(self.grab_screen(day_region))):
                continue

            content = self.get_message_contents(self.grab_screen(message_region))
            if not content:
                continue

            if not self.day_is_known(day):
                message = TribeLogMessage(day, *content)
                messages.append(message)

                if self._tribe_log:
                    self.send_alert(message)

        self._tribe_log += messages

    def get_daytime(self, image: str | Image.Image | ScreenShot) -> str:
        """Prepares the given image for a tesseract OCR scan replaces potential
        mistakes in the result, returns the OCR'd daytime in the given image.
        """
        replace_mapping = {
            "|": "",
            "v": "y",
            "O": "0",
            ".": ",",
            "l": "1",
            "i": "1",
            "S": "5",
            "B": "8",
        }

        # prepare the image, denoising upscaling dilating etc...
        prepared = self.denoise_text(
            image, denoise_rgb=(180, 180, 180), variance=18, upscale=True, upscale_by=2
        )

        # get tesseract result, whitelisting seems to not be working too well.
        raw_day_string = tes.image_to_string(
            prepared,
            config="--psm 6 -l eng",
        ).rstrip()

        # replace the potentially mistaken characters
        for c in replace_mapping:
            raw_day_string = raw_day_string.replace(c, replace_mapping[c])
        day_string = raw_day_string

        try:
            # split the day into the parts we care about
            day = day_string.split(" ")[1].replace(",", "")
            hour, min, sec = (day_string.split(" ")[2].split(":")[i] for i in range(3))

            # check that all values make logical sense
            if any((len(day) > 5, int(hour) > 24, int(min) > 60, int(sec) > 60)):
                print("Invalid day detected!", day_string)
                return None

        except Exception as e:
            print("Day invalid!", day_string)
            return None

        return day_string

    def get_message_contents(self, image) -> str:

        denoise_rgb = self.get_noise_rgb(image)
        if not denoise_rgb:
            return None

        event_mapping = {
            (255, 0, 0): "Something destroyed!",
            (208, 3, 211): "Something killed!",
            (158, 76, 76): "Tek Sensor triggered!",
        }

        prepared_img = self.denoise_text(
            image,
            denoise_rgb,
            30 if not denoise_rgb == (208, 3, 211) else 50,
            upscale=True,
            upscale_by=2,
        )

        raw_res = tes.image_to_string(
            prepared_img,
            config="--psm 6 -l eng",
        ).rstrip()

        for c in CONTENTS_MAPPING:
            raw_res = raw_res.replace(c, CONTENTS_MAPPING[c])
        filtered_res = raw_res

        return event_mapping[denoise_rgb], filtered_res


    def get_noise_rgb(self, image: str | Image.Image | ScreenShot) -> str:

        denoising_rgb = None

        image = np.array(image)
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        if (
            self.locate_in_image(
                "templates/tribelog_auto_decay.png", image, confidence=0.8
            )
            is not None
        ):
            return None

        for rgb in self.DENOISE_MAPPING:
            template = self.DENOISE_MAPPING[rgb]

            if not isinstance(template, list):
                if self.locate_in_image(template, image, confidence=0.8) is not None:
                    denoising_rgb = rgb
                    break
                continue

            if any(
                self.locate_in_image(template, image, confidence=0.8) is not None
                for template in self.DENOISE_MAPPING[rgb]
            ):
                denoising_rgb = rgb
                break

        return denoising_rgb

    def day_is_known(self, day) -> bool:

        if not self._tribe_log:
            print("No days yet!")
            return False

        print(f"Checking if {day} is already known!")

        day_int = int(day.split(" ")[1].replace(",", ""))
        most_recent_day = int(self._tribe_log[0].day.split(" ")[1].replace(",", ""))

        if day_int < most_recent_day or day_int > most_recent_day + 20:
            return True

        for message in self._tribe_log:
            print(day, message.day)
            if day == message.day:
                print("Day is already known in tribelog!")
                return True

        print("Can add day!")