from io import BytesIO
from typing import Optional

from discord import (Embed, File,  # type:ignore[import]
                     RequestsWebhookAdapter, Webhook)
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
            
        if mention and self._user_id is not None:
            message = f"<{self._user_id}>"
        else:
            message = ""

        self._hook.send(content=message, embed=embed, file=file)