from discord import RequestsWebhookAdapter  # type:ignore[import]
from discord import Embed, Webhook

from ..tools import threaded


class AlertWebhook:
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

    def __init__(self, url: str, user_id: str):
        self._hook = Webhook.from_url(url, adapter=RequestsWebhookAdapter())
        self._url = url
        if not user_id:
            self._user_id = None
        else:
            self._user_id = user_id.rstrip(">").lstrip("<")

    @property
    def user_id(self) -> str | None:
        return self._user_id

    @property
    def url(self) -> str:
        return self._url

    @threaded("Posting alert")
    def send_alert(self, embed: Embed, *, mention: bool = False) -> None:

        if mention and self._user_id is not None:
            message = f"<{self._user_id}>"
        else:
            message = ""

        self._hook.send(content=message, embed=embed, avatar_url=self.AVATAR, username="Ling Ling Look Logs")
