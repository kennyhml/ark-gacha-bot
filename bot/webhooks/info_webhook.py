from io import BytesIO
from typing import Optional

from ark import ArkWindow
from discord import File  # type:ignore[import]
from discord import Embed, RequestsWebhookAdapter, Webhook
from mss.screenshot import ScreenShot  # type:ignore[import]

from ..tools import mss_to_pil, threaded


class InfoWebhook:
    """Handles webhook data traffic to the info webhook, which provides details
    about station completions, errors or statistics.

    Parameters
    ---------
    url :class:`str`:
        The webhook url to post to

    user_id :class:`str`:
        The discord id of the user to ping, with or without < >
    """

    DISCORD_AVATAR = "https://i.kym-cdn.com/entries/icons/facebook/000/022/293/Bloodyshadow_rolled_user_shutupandsleepwith_i_m_bisexual_let_s_work_from__a48265eae6a474904cdc2cae9f184aad.jpg"

    def __init__(self, url: str, user_id: str):
        self._hook = Webhook.from_url(url, adapter=RequestsWebhookAdapter())
        self._hook.user = "Ling Ling"
        self._hook.avatar = self.DISCORD_AVATAR
        self.screen = ArkWindow()
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

    @threaded("Sending embed")
    def send_embed(
        self, embed: Embed, *, img: Optional[ScreenShot] = None, mention: bool = False
    ) -> None:
        """Sends an embed to the info webhook alongside a mention. If an image is passed
        it will be converted to a bytes-like object and integrated into the embed.

        Parameters
        ----------
        embed :class:`discord.Embed`:
            The embed to send

        img :class:`Optional[mss.Screenshot]`:
            The image to include into the embed, `None` by default

        mention :class:`bool`:
            Whether to mention the user alongside the embed or not.
        """
        if img is None:
            file = None
        else:
            image_pil = mss_to_pil(img)
            with BytesIO() as image_binary:
                image_pil.save(image_binary, "PNG")
                image_binary.seek(0)
                file = File(fp=image_binary, filename="image.png")
            embed.set_image(url="attachment://image.png")

        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")

        if mention and self._user_id is not None:
            message = f"<{self._user_id}>"
        else:
            message = ""
        try:
            self._hook.send(content=message, embed=embed, file=file)
        except Exception:
            print("Failed to send embed.")

    @threaded("Sending error")
    def send_error(
        self,
        task: str,
        exception: Exception,
        image: Optional[ScreenShot] = None,
        *,
        mention: bool = False,
    ) -> None:
        """Posts an image of the current screenshot alongside current
        bed and the exception to discord for debugging purposes.

        Parameters:
        ------------
        bed :class:`Bed`:
            The bed (station) the exception occured at

        exception: :class:`Exception`:
            The description of the occured exception
        """
        embed = Embed(
            type="rich",
            title="Ran into a problem!",
            description="An unexpected error occurred!",
            color=0xF20A0A,
        )

        embed.add_field(name=f"Task:", value=task)
        embed.add_field(name=f"Error:", value=exception)

        embed.set_image(url="attachment://image.png"),

        if image is None:
            image = self.screen.grab_screen((0, 0, 1920, 1080))

        image_pil = mss_to_pil(image)

        with BytesIO() as image_binary:
            image_pil.save(image_binary, "PNG")
            image_binary.seek(0)
            file = File(fp=image_binary, filename="image.png")
        embed.set_image(url="attachment://image.png")

        if mention and self._user_id is not None:
            message = f"<{self._user_id}>"
        else:
            message = ""
        try:
            self._hook.send(content=message, embed=embed, file=file)
        except Exception:
            print("Failed to send embed.")
