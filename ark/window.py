"""
Ark API module handling the ark window.

All further ark classes should derive from `ArkWindow` as it provides the
methods neccessary to deal with alot of screen related stuff as well as
converting points, regions and even images to the resolution the game is running
in.

Note that the ark window class expects points and templates to be taken on 1920x1080
resolution.
"""
import cv2 as cv
import numpy as np
import PIL
import pyautogui as pg
import pygetwindow
from mss import mss, tools
from PIL import Image, ImageOps
from pytesseract import pytesseract as tes
from screeninfo import get_monitors

tes.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class ArkWindow:
    """ARK window handle
    ---------------------

    Contains the boundaries of the game and the monitor it is running on.\n
    Scales points, regions and images depending on the games resolution.

    Contains methods to grab screenshots, match templates and check if the game
    is running. If no ark window could be grabbed, it assumes a regular 1920x1080
    ark window running on a 1920x1080 monitor.

    Attributes:
    ----------
    window :class:`dict`:
        A dictionary containing the games boundaries

    monitor :class:`dict`:
        A dictionary containing the boundaries of the monitor the game is running on

    fullscreen :class:`bool`:
        Whether the game is running in fullscreen or not.
    """

    TITLE_BAR_HEIGHT = 30

    def __init__(self) -> None:
        self._window = self.get_window()
        self._monitor = self.get_monitor()
        self._fullscreen = self.check_fullscreen()

    @property
    def window(self):
        return self._window

    @property
    def monitor(self):
        return self._monitor

    @property
    def fullscreen(self):
        return self._fullscreen

    def grab_screen(self, region, path: str = None, convert: bool = True) -> str:
        """Grabs a screenshot of the given region using mss and saves it
        at the specified path.

        Parameters:
        ---------
        Region :class:`tuple`:
            The region of the area to screenshot as (x, y, w, h)

        Path :class:`str`:
            The path to save the image at

        convert :class:`bool`:
            Decides if the given region will be converted or not

        Returns:
        ---------
        The specified path, to improve usage possibilites
        """
        with mss() as sct:
            # set region
            if convert:
                region = self.convert_region(region)
            x, y, w, h = region

            region_dict = {"left": x, "top": y, "width": w, "height": h}

            # grab img
            img = sct.grab(region_dict)

            if path:
                # Save to the picture file
                tools.to_png(img.rgb, img.size, output=path)
                return path
            return img

    def get_window(self) -> dict:
        """Grab the ark window using pygetwindow and create the boundaries.
        If it fails to grab a window it will assume a 1920x1080 window.
        """
        try:
            window = pygetwindow.getWindowsWithTitle("ARK: Survival Evolved")[0]

            # create a window dict for mss
            return {
                "left": window.left,
                "top": window.top,
                "width": window.width,
                "height": window.height,
            }
        except Exception as e:
            print(
                f"Could not grab the ark boundaries!\n{e}\n\n"
                "Assuming a 1920x1080 windowed fullscreen game."
            )
            return {"left": 0, "top": 0, "width": 1920, "height": 1080}

    def get_window_center(self) -> tuple:
        """Gets the center of the window. Used to determine what monitor
        the game is running on.
        """
        return (
            self._window["left"] + (self._window["width"] // 2),
            self._window["top"] + (self._window["height"] // 2),
        )

    def get_monitor(self) -> dict:
        """Gets the monitor boundaries of the monitor ark is running on
        and makes sure its the primary monitor

        Returns:
        ---------
        The boundaries of the monitor ARK is running on
        """
        center = self.get_window_center()

        for m in get_monitors():
            # check x spacing
            if not (m.x < center[0] and center[0] < m.x + m.width):
                continue

            # check y spacing
            if not (m.y < center[1] and center[1] < m.y + m.height):
                continue

            # create a dict of the monitor
            return {
                "left": m.x,
                "top": m.y,
                "width": m.width,
                "height": m.height,
            }

        print(
            "Could not find then monitor ARK is running on!\n"
            "Assuming a 1920x1080 monitor."
        )
        return self._window

    def check_fullscreen(self):
        """Checks if ARK is running in fullscreen by checking if the monitor
        dict matches the ARK boundaries.
        """
        return all(
            [
                self._window[boundary] == self._monitor[boundary]
                for boundary in ["left", "top", "width", "height"]
            ]
        )

    def print_boundaries(self):
        print(
            f"Ark Window: {self._window}\n"
            f"Monitor boundaries: {self._monitor}\n"
            f"Fullscreen: {self._fullscreen}"
        )

    def need_boundary_scaling(self):
        """Checks if we need to scale width and height on regions or images"""
        return not (
            self._monitor["height"] == 1080
            and self._monitor["width"] == 1920
            or not self._fullscreen
        )

    def update_boundaries(self):
        """Re-initializes the class to update the window"""
        self._window = self.get_window()
        self._monitor = self.get_monitor()
        self._fullscreen = self.check_fullscreen()

    def convert_width(self, width) -> int:
        if not self.need_boundary_scaling():
            return width

        return self.convert_point(width, 0)[0]

    def convert_height(self, height) -> int:
        if not self.need_boundary_scaling():
            return height

        return self.convert_point(0, height)[1]

    def convert_point(self, x=None, y=None):
        """Converts the given point to the corresponding point on the ARK window"""
        # Normalize the position using pyautogui
        x, y = pg._normalizeXYArgs(x, y)

        # check for fullscreen converting
        if self._fullscreen:
            return (
                int((x / 1920) * self.monitor["width"]),
                int((y / 1080) * self.monitor["height"]),
            )

        return (
            self.monitor["left"] + x + self._window["left"] + 8,
            self.monitor["top"] + y + self._window["top"] + self.TITLE_BAR_HEIGHT,
        )

    def convert_region(self, region: tuple):
        """Converts the given region to the corresponding region on the ARK window"""
        x, y, w, h = region

        # check if we can apply native scaling
        if not self.need_boundary_scaling():
            return (*self.convert_point(x, y), w, h)

        return (*self.convert_point(x, y), *self.convert_point(w, h))

    def convert_image(self, image: str) -> Image.Image | str:
        """Converts the given image to an upscaled image of ARKs resolution.

        Parameters:
        ----------
        image: :class:`str`:
            The path of the image to convert

        Returns:
        ----------
        A PIL `Image.Image` or the path if no converting was needed.
        """
        # check if we need to scale at all
        if not self.need_boundary_scaling():
            return image

        # open the image in PIL and use ImageOps to upscale it (maintains aspect ratio)
        raw_image = Image.open(image)
        new_width = self.convert_point(raw_image.width, raw_image.height)
        return ImageOps.contain(raw_image, new_width, PIL.Image.Resampling.LANCZOS)

    def locate_in_image(
        self, template: str, image, confidence: float, grayscale: bool = False
    ):
        return pg.locate(template, image, confidence=confidence, grayscale=grayscale)

    def locate_all_in_image(
        self, template: str, image, confidence: float, grayscale: bool = False
    ):
        return self.filter_points(
            set(
                pg.locateAll(
                    template, image, confidence=confidence, grayscale=grayscale
                )
            ),
            min_dist=15,
        )

    def locate_template(
        self,
        template: str,
        region: tuple,
        confidence: float,
        convert: bool = True,
        grayscale: bool = False,
    ):

        return pg.locateOnScreen(
            self.convert_image(template),
            region=self.convert_region(region) if convert else region,
            confidence=confidence,
            grayscale=grayscale,
        )

    def locate_all_template(
        self, template: str, region: tuple, confidence: float, convert: bool = True
    ):
        return self.filter_points(
            set(
                pg.locateAllOnScreen(
                    self.convert_image(template),
                    region=self.convert_region(region) if convert else region,
                    confidence=confidence,
                )
            ),
            min_dist=15,
        )

    def filter_points(self, targets, min_dist) -> set:
        """Filters a set of points by min dist from each other.
        This is important because pyautogui may locate the same template
        multiple times on the same position.
        """
        filtered = set()

        while targets:
            eps = targets.pop()
            for point in targets:
                if all(abs(c2 - c1) < min_dist for c2, c1 in zip(eps, point)):
                    break
            else:
                filtered.add(eps)
        return filtered

    def denoise_text(
        self,
        image: str,
        denoise_rgb: tuple,
        variance: int,
        dilate: bool = True,
        upscale: bool = False,
        upscale_by: int = 8,
    ) -> Image.Image:
        """Denoises / Masks the passed image by the given RGB and variance.
        Useful to pre-process images for a tesseract character scan.

        Parameters:
        ----------
        image :class:`str` | `Image`:
            The image to denoise, if passed as string it will be read using cv2

        denoise_rgb :class:`tuple`:
            The rgb to filter out, only pixels with this rgb will remain in the image

        variance :class:`int`:
            The variance allowed for the denoise_rgb

        Returns:
        ----------
        An upscaled, filtered and dilated version of the given Image as Mat

        """
        # check if we need to read the image or convert it
        if isinstance(image, str):
            image = cv.imread(image, 1)
        else:
            image = np.asarray(image)

        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)

        # set color range (filering the color of the chars here)
        lower_bound = (
            max(0, denoise_rgb[0] - variance),
            max(0, denoise_rgb[1] - variance),
            max(0, denoise_rgb[2] - variance),
        )
        upper_bound = (
            min(255, denoise_rgb[0] + variance),
            min(255, denoise_rgb[1] + variance),
            min(255, denoise_rgb[2] + variance),
        )

        # load the image into pillow to resize it
        image = cv.inRange(image, lower_bound, upper_bound)

        if not dilate:
            return image

        if upscale:
            image = Image.fromarray(image)
            image = image.resize(
                (image.size[0] * upscale_by, image.size[1] * upscale_by), 1
            )

        matrix_size = 2 if not upscale else 3

        # Taking a matrix of size 5 as the kernel
        kernel = np.ones((matrix_size, matrix_size), np.uint8)
        return cv.dilate(np.asarray(image), kernel, iterations=1)

    def count_pixels(self, masked_img) -> int:
        """Counts all non zero pixels in the given mask"""
        try:
            return len(cv.findNonZero(masked_img))
        except TypeError:
            return None
