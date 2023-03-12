import time

from ark import TribeLog, TribeLogMessage
from discord import RequestsWebhookAdapter  # type:ignore[import]
from discord import Embed, Webhook, WebhookMessage
from mss.screenshot import ScreenShot  # type:ignore[import]

from ..tools import img_to_file, mss_to_pil, threaded
from .alert_settings import AlertSettings


class TribeLogWebhook:
    """Handles webhook data traffic to the info webhook, which provides details
    about station completions, errors or statistics.

    Parameters
    ---------
    url :class:`str`:
        The webhook url to post to

    user_id :class:`str`:
        The discord id of the user to ping, with or without < >
    """

    sensor_icon = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/1/16/Tek_Sensor_%28Genesis_Part_1%29.png/revision/latest?cb=20200226080818"
    destroyed_icon = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/4/46/C4_Charge.png/revision/latest/scale-to-width-down/228?cb=20150615094656"
    dino_killed_icon = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/6/61/Tek_Bow_%28Genesis_Part_2%29.png/revision/latest?cb=20210603191501"
    DISCORD_AVATAR = (
        "https://i.kym-cdn.com/entries/icons/original/000/017/373/kimjongz.PNG"
    )

    LOG_MESSAGE: WebhookMessage | None = None
    _LAST_MENTION = time.time()

    def __init__(self, tribelog: TribeLog, alert_url: str, log_url: str):
        self.alert = Webhook.from_url(alert_url, adapter=RequestsWebhookAdapter())
        self.raw_log = Webhook.from_url(log_url, adapter=RequestsWebhookAdapter())
        self.tribelog = tribelog
        self.settings = AlertSettings.load()

    def check_tribelogs(self) -> None:
        self.tribelog.open()
        current_logs = self.tribelog.grab_current_events()
        self.tribelog.close()

        self.check_alerts(current_logs)

    @threaded("Tribe log thread")
    def check_alerts(self, image: ScreenShot) -> None:
        updates = self.tribelog.find_tribelog_events(image)

        print(f"{len(updates)} updates found.")
        embeds = [self.get_alert_embed(event) for event in updates]
        for bulk in range(0, len(embeds), 10):
            self.post_alerts(embeds[bulk:])

        self.post_raw_log(image)

    def post_alerts(self, alerts: list[Embed]) -> None:
        message = self.get_mention_id(alerts)

        self.alert.send(
            content=message,
            embeds=alerts,
            avatar_url=self.DISCORD_AVATAR,
            username="Ling Ling Look Logs",
        )

    def get_mention_id(self, alerts: list[Embed]) -> str:
        if (time.time() - self._LAST_MENTION) < self.settings.mention_cooldown:
            return ""

        if len(alerts) > 10 and self.settings.mass_event_mention:
            return "@everyone"

        if (
            any("Sensor" in alert.title for alert in alerts)
            and self.settings.tek_sensor_id
        ):
            return f"<@&{self.settings.tek_sensor_id.rstrip('<').lstrip('>')}>"

        if len(alerts) < self.settings.mention_at_events:
            return ""

        if (
            any("destroyed" in alert.title for alert in alerts)
            and self.settings.destroyed_id
        ):
            return f"<@&{self.settings.destroyed_id.rstrip('<').lstrip('>')}>"

        if any("killed" in alert.title for alert in alerts) and self.settings.killed_id:
            return f"<@&{self.settings.killed_id.rstrip('<').lstrip('>')}>"

        return ""

    def post_raw_log(self, image: ScreenShot) -> None:
        """Sends the raw tribelog image to the log webhook, deleting the
        previous posted message (if available).
        """
        if self.LOG_MESSAGE is not None:
            self.LOG_MESSAGE.delete()

        self.LOG_MESSAGE = self.raw_log.send(
            content="Current Tribelogs:", file=img_to_file(mss_to_pil(image)), wait=True
        )

    def get_alert_embed(self, message: TribeLogMessage) -> Embed:
        """Sends an alert to discord with the given message."""
        # create our webhook, action and description in the header
        embed = Embed(
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
        embed.set_footer(text="Ling Ling Bot - Kenny#0947")
        return embed
