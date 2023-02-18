import functools
from threading import Thread
from typing import Callable
from PIL import Image
import numpy as np
import cv2 as cv

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