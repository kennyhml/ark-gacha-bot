import json
import time

from ark import State, TribeLog
from ark.server import Server, server_query
from discord import Webhook  # type:ignore[import]
from discord import RequestsWebhookAdapter, WebhookMessage

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

    def __init__(self, url: str, server: Server, tribelog: TribeLog, timer_pop: int):
        self._hook = Webhook.from_url(url, adapter=RequestsWebhookAdapter())
        self._tribelog = tribelog
        self._url = url
        self._timer_pop = timer_pop
        if server.ip is None:
            server_query.query(server)

        self._timer: int | None = None
        self._server = server
        self.timer_loop_running = True

        with open("settings/settings.json") as f:
            data = json.load(f)
        try:
            state_id = int(data["discord"]["state_message_id"])
            self._hook.edit_message(state_id, content=self._build_message())
        except Exception:
            TimerWebhook.ORIGINAL_MESSAGE = self.post_initial_message().id
            data["discord"]["state_message_id"] = str(TimerWebhook.ORIGINAL_MESSAGE)
            with open("settings/settings.json", "w") as f:
                json.dump(data, f, indent=4)
        else:
            TimerWebhook.ORIGINAL_MESSAGE = state_id

        self.start_timer_loop()

    @property
    def url(self) -> str:
        return self._url

    @property
    def timer(self) -> int | None:
        return self._timer

    @timer.setter
    def timer(self, timer: int) -> None:
        if timer > 1020:
            raise ValueError("Invalid timer")
        self._timer = timer
        self.timer_popped = False

    def _build_message(self) -> str:
        if self._timer is not None:
            minutes, seconds = divmod(self._timer, 60)

        return (
            "```fix\n"
            f"Online Tribemembers: {self._tribelog.online_members}\n"
            f"Server Timer: {'?' if self._timer is None else f'{minutes}:{seconds:02d}'}\n"
            f"Server Status: {self._server.status}\n"
            f"Server Day: {self._server.day}```"
        )

    def post_initial_message(self) -> WebhookMessage:
        """Sends the initial message to discord for the session so that we can edit
        it later."""
        return self._hook.send(
            content=self._build_message(),
            wait=True,
            username=self._server.name,
            avatar_url=self.AVATAR,
        )

    @threaded("Timer thread")
    def start_timer_loop(self) -> None:
        assert TimerWebhook.ORIGINAL_MESSAGE is not None

        while self.timer_loop_running and State.running:
            start = time.perf_counter()
            try:
                self._hook.edit_message(
                    self.ORIGINAL_MESSAGE, content=self._build_message()
                )
            except ConnectionError:
                pass

            except Exception as e:
                print(f"Unhandled error in timer thread!\n{e}")

            time_taken = (time.perf_counter() - start)
            if self._timer is None:
                continue

            # check how long sending the message took so we can adjust
            # the sleep
            if time_taken > 1:
                self._timer -= round(time_taken)
            else:
                time.sleep(1 - time_taken)
                self._timer -= 1

            if self._timer <= self._timer_pop:
                self._timer = (15 * 60) + 10
                self.timer_popped = True