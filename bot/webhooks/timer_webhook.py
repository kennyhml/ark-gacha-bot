import json
import time

from ark.server import Server, server_query
from discord import (RequestsWebhookAdapter, Webhook,  # type:ignore[import]
                     WebhookMessage)

from ..tools import threaded


class TimerWebhook:
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

    AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/1/18/Tek_Transmitter.png/revision/latest/scale-to-width-down/228?cb=20170131150002"
    ORIGINAL_MESSAGE: WebhookMessage | None = None

    def __init__(self, url: str, server: Server):
        self._hook = Webhook.from_url(url, adapter=RequestsWebhookAdapter())
        self._hook.user = "Ling Ling"
        self._hook.avatar = self.AVATAR

        self._url = url
        if server.ip is None:
            server_query.query(server)

        self._server = server
        self.timer_loop_running = True
        self.handshake = False
        with open("settings/settings.json") as f:
            data = json.load(f)
        try:
            state_id = int(data["discord"]["state_message_id"])
            message = (
                "```fix\n"
                f"Status: {self._server.status}\n"
                f"Day: {self._server.day}\n"
                f"Timer: ?```"
            )
            self._hook.edit_message(state_id, content=message)
        except Exception:
            TimerWebhook.ORIGINAL_MESSAGE = self.post_initial_message().id
            data["discord"]["state_message_id"] = str(TimerWebhook.ORIGINAL_MESSAGE)
            with open("settings/settings.json", "w") as f:
                json.dump(data, f, indent=4)
        else:
            TimerWebhook.ORIGINAL_MESSAGE = state_id

    @property
    def url(self) -> str:
        return self._url

    def post_initial_message(self) -> WebhookMessage:
        """Sends the initial message to discord for the session so that we can edit
        it later."""
        message = (
            "```fix\n"
            f"Status: {self._server.status}\n"
            f"Day: {self._server.day}\n"
            f"Timer: ?```"
        )

        return self._hook.send(
            content=message,
            wait=True,
            username=self._server.name,
            avatar_url=self.AVATAR,
        )

    def refresh(self, timer: int) -> None:
        print("Stopped timer thread, awaiting handshake...")
        self.timer_loop_running = False

        while not self.handshake:
            time.sleep(0.1)

        print("Handshake successful. Refreshing...")
        self.timer_loop_running = True
        self.handshake = False
        self.start_timer_loop(timer)

    @threaded("Timer thread")
    def start_timer_loop(self, timer: int) -> None:
        assert TimerWebhook.ORIGINAL_MESSAGE is not None
        while self.timer_loop_running:
            minutes, seconds = divmod(timer, 60)
            message = (
                "```fix\n"
                f"Status: {self._server.status}\n"
                f"Day: {self._server.day}\n"
                f"Timer: {minutes}:{seconds:02d}```"
            )
            s = time.perf_counter()
            self._hook.edit_message(self.ORIGINAL_MESSAGE, content=message)
            time_taken = time.perf_counter() - s
            if time_taken > 1:
                timer -= round(time_taken)
            else:
                time.sleep(1 - time_taken)
                timer -= 1

            if timer <= 10:
                timer = (15 * 60) + 10

        self.handshake = True
