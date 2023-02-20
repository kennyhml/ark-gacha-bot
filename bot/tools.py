import functools
from threading import Thread
from typing import Callable

import cv2 as cv  # type:ignore[import]
import numpy as np
from PIL import Image # type:ignore[import]


def threaded(name: str):
    """Threads a function, beware that it will lose its return values"""

    def outer(func: Callable):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            thread = Thread(target=func, name=name, args=args, kwargs=kwargs)
            thread.start()

        return inner

    return outer


def mss_to_pil(image) -> Image.Image:
    img_array = np.asarray(image)
    image_rgb = cv.cvtColor(img_array, cv.COLOR_BGR2RGB)
    return Image.fromarray(image_rgb)


def format_seconds(seconds: int) -> str:
    """Formats a number in seconds to a string nicely displaying it in
    different formats."""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    days, hours, minutes = round(days), round(hours), round(minutes)
    if days:
        return f"{days} day{'s' if days != 1 else ''} {hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    elif hours:
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    elif minutes:
        return f"{minutes} minute{'s' if minutes != 1 else ''} {seconds} second{'s' if seconds != 1 else ''}"
    else:
        return f"{seconds} seconds"
