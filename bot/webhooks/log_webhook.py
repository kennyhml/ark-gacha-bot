from io import BytesIO

from discord import RequestsWebhookAdapter  # type:ignore[import]
from discord import File, Webhook, WebhookMessage
from mss.screenshot import ScreenShot  # type:ignore[import]

from ..tools import mss_to_pil, threaded


class LogWebhook:
    """Handles webhook data traffic to the timer / server status webhook.
    The webhook provides information about the status of the current server
    such as the day and the status as well as what the current timer is.

    Parameters
    ---------
    url :class:`str`:
        The webhook url to post to

    server :class:`Server`:
        The server to post updates for
    """

    AVATAR = "https://i.kym-cdn.com/entries/icons/original/000/017/373/kimjongz.PNG"
    _PREV_MESSAGE: WebhookMessage | None = None

    def __init__(self, url: str):
        self._hook = Webhook.from_url(url, adapter=RequestsWebhookAdapter())

    @threaded("Posting tribelogs")
    def send_logs(self, image: ScreenShot) -> None:
        if self._PREV_MESSAGE is not None:
            self._PREV_MESSAGE.delete()

        image_pil = mss_to_pil(image)
        with BytesIO() as image_binary:
            image_pil.save(image_binary, "PNG")
            image_binary.seek(0)
            file = File(fp=image_binary, filename="image.png")

        self._PREV_MESSAGE = self._hook.send(
            "Current tribelogs:",
            file=file,
            wait=True,
            avatar_url=self.AVATAR,
            username="Ling Ling Look Logs",
        )
