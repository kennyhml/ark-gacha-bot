import time

from ark import Player, TekSleepingPod, TribeLog, _helpers, exceptions
from discord import Embed  # type: ignore[import]

from ...tools import format_seconds
from ...webhooks import InfoWebhook
from .._station import Station
from ._settings import HealingStationSettings

class HealingStation(Station):
    """Represents a healing station, a healing station is responsible for
    ensuring that the player does not die. It will be travelled to when
    the player has a bad debuff such as hunger, thirst or broken bones.

    The player will enter a tek pod to heal up, healing is finished when
    health, food and water have reached their maximum or when the healing
    timer has elapsed, which is calculated by the players stats / the rate
    a tek pod heals at.

    Parameters
    -----------
    name :class:`str`:
        The name of the station, or the name of the bed to travel to.

    player :class:`Player`:
        The player instance to handle movements.

    tribelog :class:`Tribelog`:
        The tribelog instance to check tribelogs when spawning.

    info_webhook :class:`InfoWebhook`:
        The info webhook instance to post station statistics to.
    """

    POD_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/0/0b/Tek_Sleeping_Pod_%28Aberration%29.png/revision/latest/scale-to-width-down/228?cb=20171214081119"

    def __init__(
        self,
        player: Player,
        tribelog: TribeLog,
        info_webhook: InfoWebhook,
    ) -> None:

        self.settings = HealingStationSettings.load()
        self._name = self.settings.pod_name
        self._player = player
        self._tribelog = tribelog
        self._webhook = info_webhook

        self._least_healed = time.time()
        self.pod = TekSleepingPod(self._name)

    def is_ready(self) -> bool:
        return self._player.needs_recovery()

    def complete(self) -> None:
        """Spawns at the healing station and enters the tek pod to heal,
        then leaves the tek pod and sends a healing statistics embed.
        """
        start = time.time()
        try:
            self.spawn()

            self.pod.heal(self._player)
            self.pod.leave()

        except exceptions.PlayerDiedError:
            pass

        except exceptions.WheelError:
            if not _helpers.await_event(self._player.has_died, max_duration=20):
                raise

        embed = self._create_embed(round(time.time() - start))
        self._webhook.send_embed(embed)

    def spawn(self) -> None:
        """Spawns at the healing station, override to use a pod
        instead of a bed.
        """
        self._player.stand_up()
        self._player.prone()
        self._player.look_down_hard()

        self.pod.spawn()
        self._tribelog.check_tribelogs()
        self._player.spawn_in()

    def _create_embed(self, time_taken: int) -> Embed:
        """Sends a msg to discord that we healed"""
        taken = format_seconds(time_taken)
        interval = format_seconds(round(time.time() - self._least_healed))
        embed = Embed(
            type="rich",
            title=f"Recovered player at '{self._name}'!",
            color=0x4F4F4F,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=taken)
        embed.add_field(name="Last healed:", value=interval)

        embed.set_thumbnail(url=self.POD_AVATAR)
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")

        return embed
