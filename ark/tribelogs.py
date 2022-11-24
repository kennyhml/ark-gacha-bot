from bot.ark_bot import ArkBot
from pytesseract import pytesseract as tes
from mss.screenshot import ScreenShot
from PIL.Image import Image


class Tribelogs(ArkBot):

    LOG_REGION = 1340, 180, 460, 820

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
            "templates/day.png", region=self.LOG_REGION, confidence=0.8
        )

    def get_log_frames(self) -> dict[str:ScreenShot]:
        """Returns a list of tuples containing the top, left, width and height
        values for each Daytime in the currently shown tribelog.
        """
        # sort days from top to bottom by y coordinate so we can get the message frame
        day_points = self.get_day_occurrences()
        days_in_order = sorted([day for day in day_points], key=lambda t: t[1])

        frames = {}
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

            # OCR the day and make it the key to the correspnding log message
            frames[self.get_daytime(self.grab_screen(day_region))] = self.grab_screen(
                message_region
            )

        return frames

    def get_daytime(self, image: str | Image | ScreenShot) -> str:
        """Prepares the given image for a tesseract OCR scan replaces potential
        mistakes in the result, returns the OCR'd daytime in the given image.
        """
        replace_mapping = {"|": "", "v": "y", "O": "0", ".": ",", "l": "1", "i": "1"}

        # prepare the image, denoising upscaling dilating etc...
        prepared = self.denoise_text(
            image, denoise_rgb=(180, 180, 180), variance=18, upscale=True, upscale_by=2
        )
        # get tesseract result, whitelisting seems to not be working too well.
        res = tes.image_to_string(
            prepared,
            config="--psm 6 -l eng",
        ).rstrip()

        # replace the potentially mistaken characters
        for c in replace_mapping:
            res = res.replace(c, replace_mapping[c])
        return res
