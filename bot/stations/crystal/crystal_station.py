from __future__ import annotations

import time
from datetime import datetime
from typing import Optional

from ark import (Bed, Player, Structure, Stryder, TekDedicatedStorage,
                 TribeLog, _helpers, exceptions)
from ark.exceptions import DediNotInRangeError
from ark.items import *
from discord import Embed  # type: ignore[import]

from ...exceptions import NoCrystalAddedError
from ...webhooks import InfoWebhook, TimerWebhook
from .._station import Station
from ..arb import ARBStation
from ..grinding import GrindingStation
from ..ytrap import YTrapStation
from ._settings import CrystalStationSettings


class CrystalStation(Station):
    """Crystal Station handle.
    ------------------------------
    Follows the `Station` abstract base class and uses its default implementations.
    Has two different use modes, regular dedi depositing and stryder depositing
    where stryder depositing is required to run the ARB station and makes checking
    amounts gained alot more accurate.

    Additionally, the crystal station is responsible for setting other stations ready.

    Parameters:
    -----------
    station_data :class:`StationData`:
        A dataclass containing data about the station

    player :class:`Player`:
        The player controller handle responsible for movement

    tribelog :class:`Tribelog`:
        The tribelog object to check tribelogs when spawning

    grinding_station :class:`GrindingStation`:
        The grinding station object to set ready when the vault is capped

    arb_station :class:`ARBStation`:
        The arb station object to add the wood to
    """

    CRYSTAL_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/c/c3/Gacha_Crystal_%28Extinction%29.png/revision/latest?cb=20181108100408"
    DUST_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/b/b1/Element_Dust.png/revision/latest/scale-to-width-down/228?cb=20181107161643"
    DROP_ITEMS = ["primitive", "ramshackle"]

    _ITEMS = [
        ASSAULT_RIFLE,
        BEHEMOTH_GATE,
        BEHEMOTH_GATEWAY,
        BLACK_PEARL,
        DUST,
        FABRICATED_SNIPER,
        FLINT,
        FUNGAL_WOOD,
        GACHA_CRYSTAL,
        METAL_GATE,
        METAL_GATEWAY,
        MINER_HELMET,
        PUMPGUN,
        RIOT,
        STONE,
        TREE_PLATFORM,
    ]

    def __init__(
        self,
        name: str,
        player: Player,
        tribelog: TribeLog,
        info_webhook: InfoWebhook,
        settings: CrystalStationSettings,
        timer_webhook: TimerWebhook,
        grinding_station: Optional[GrindingStation],
        arb_station: Optional[ARBStation],
        *,
        gen2: bool,
    ) -> None:

        self._name = name
        self._player = player
        self._tribelog = tribelog
        self._webhook = info_webhook
        self._timer_webhook = timer_webhook
        self.settings = settings

        self.bed = Bed(name)
        self.dedi = TekDedicatedStorage()
        self.stryder = Stryder()
        self.vault = Structure(
            "Vault",
            "assets/templates/vault.png",
            capacity="assets/templates/vault_capped.png",
        )
        self.gen2 = gen2

        self._grinding_station = grinding_station
        self._arb_station = arb_station

        self._first_pickup = True

        self._total_pickups = 0
        self._resources_made: dict[Item, int] = {}
        self.last_completed = datetime.now()
        self.interval = self.settings.crystal_interval

    @staticmethod
    def build_stations(
        player: Player,
        tribelog: TribeLog,
        info_webhook: InfoWebhook,
        timer_webhook: TimerWebhook,
        grinding_station: GrindingStation,
        arb_station: ARBStation,
        *,
        gen2: bool,
    ) -> list[CrystalStation]:
        settings = CrystalStationSettings.load()

        return [
            CrystalStation(
                f"{settings.crystal_prefix}{i:02d}",
                player,
                tribelog,
                info_webhook,
                settings,
                timer_webhook,
                None if i else grinding_station,
                None if i else arb_station,
                gen2=gen2,
            )
            for i in range(settings.crystal_beds)
        ]

    def is_ready(self) -> bool:
        if YTrapStation.total_ytraps_collected < self.settings.min_ytraps_collected:
            return False

        return super().is_ready()

    def complete(self) -> None:
        """Completes the crystal collection station.

        Travels to the crystal station, picks, opens and deposits crystals and
        puts away the items into the vault as configured by the user.

        Keeps track of the amounts it has deposited into dedis and returns them.
        """
        try:
            self.spawn()
            start = time.time()

            # open the crystals and deposit the items into dedis
            try:
                self._pick_crystals()
            except NoCrystalAddedError:
                if self.gen2:
                    self._get_timer()
                return

            self._walk_to_dedi()
            self._open_crystals()

            if self.settings.stryder_depositing:
                resources_deposited = self.deposit_into_stryder()
                if self._arb_station is not None:
                    self._arb_station.add_wood(resources_deposited[FUNGAL_WOOD])
            else:
                resources_deposited = self.deposit_dedis()

            # put items into vault
            vault_full = self.deposit_items()
            if vault_full and self._grinding_station is not None:
                self._grinding_station.ready = True

            # increase the counters
            self._total_pickups += 1
            for item, amount in resources_deposited.items():
                got = self._resources_made.get(item, 0)
                self._resources_made[item] = got + amount

            embed = self.create_embed(resources_deposited, round(time.time() - start))
            self._webhook.send_embed(embed)

        finally:
            self.last_completed = datetime.now()

    def deposit_into_stryder(self) -> dict[Item, int]:
        self._player.turn_y_by(-50, delay=0.5)
        profits: dict[Item, int] = {}

        self.stryder.access()
        self.stryder.inventory.drop_all()

        for item in [DUST, FLINT, STONE, FUNGAL_WOOD, BLACK_PEARL]:
            self._player.inventory.search(item)
            self._player.sleep(0.3)

            stacks = self._player.inventory.count(item)
            profits[item] = max(
                int((stacks * item.stack_size) - (0.5 * item.stack_size)), 0
            )
            if stacks:
                self._player.inventory.transfer_all()
            else:
                self._player.inventory.delete_search()

        self.stryder.inventory.close()
        self.stryder.sort_items_to_nearby_dedis()
        self.stryder.sleep(1)
        return profits

    def _get_timer(self) -> None:
        try:
            if not self._timer_webhook.timer_popped:
                return
        except AttributeError:
            pass

        if not self.gen2:
            self.vault.inventory.search(EXO_GLOVES)
            self.vault.inventory.sleep(0.3)

            if not self.vault.inventory.has(EXO_GLOVES, is_searched=True):
                return

            self.vault.inventory.take(EXO_GLOVES, stacks=1)
            self._player.inventory.equip(EXO_GLOVES)

        self.vault.close()
        try:
            timer = self._player.hud.get_timer()
        except exceptions.TimerNotVisibleError:
            print("Failed to get timer!")
            timer = None

        if timer is not None:
            self._timer_webhook.timer = timer

        if self.gen2:
            return

        self.vault.open()
        self._player.inventory.unequip(EXO_GLOVES)
        self._player.inventory.transfer_all(EXO_GLOVES)

    def _pick_crystals(self) -> None:
        """Picks up the crystals in the collection point.

        Walks all the way into the back, slowly picks the crystals
        and walks back to the dedi with lag protection.
        """
        # walk back, crouch and look down
        self._walk_into_back()
        self._player.crouch()
        self._player.turn_y_by(80)

        self._walk_forward_spam_f()

    def _walk_into_back(self) -> None:
        """Walks into the back of the collection point, attempts to pick
        up a crystal to determine if it has reached the back without lagging.

        Tries again if it does not get a crystal added.
        """
        self._player.walk("s", duration=3)
        self._player.pick_up()

        # wait for the crytal to be picked up
        if _helpers.await_event(self._player.received_item, max_duration=3):
            return

        # did not pick a crystal, if its first collection we assume there is none
        if self._first_pickup:
            raise NoCrystalAddedError

        if self._timer_webhook.timer is not None and self._timer_webhook.timer < 120:
            print("Idling 20 seconds because timer is likely to have popped...")
            self._player.sleep(20)
        else:
            self._player.sleep(5)
        self._player.walk("s", duration=3)

    def _walk_forward_spam_f(self) -> None:
        """Slowly walks foward spaming the pick-up key to pick all the
        crystals while being angled slighty downwards.
        """
        for _ in range(9):
            self._player.pick_all()
            self._player.sleep(0.1)
            self._player.walk("w", duration=0.2)

        self._player.walk("w", 2)

    def _walk_to_dedi(self) -> None:
        """Walks forward to dedi with various lag protection

        Being at the dedi is determined when we can see the deposit text.
        We then attempt to open the dedi to ensure its not lagging, if it doesnt
        open, the action wheel logic is used to determine if its lag or a bad angle.

        Raises:
        ---------
        `DediNotInRangeError` when the dedi cannot be accessed.
        """
        # look up further (so the deposit text 100% appears)
        self._player.turn_y_by(-70)

        # try to access the dedi, rewalk if its not possible
        count = 0
        while not self.dedi.can_be_opened():
            while not self.dedi.is_in_deposit_range():
                self._player.walk("w", 1)
                count += 1
                if count > 30:
                    raise DediNotInRangeError
            self._player.walk("w", 1)
        self.dedi.inventory.close()

    def _open_crystals(self) -> None:
        """Opens the crystals at the dedis, counting each iteration of the hotbar
        until there are no more crystals in our player inventory.

        Parameters:
        -----------
        first_time :class:`bool`:
            Whether the bot has opened crystals before, this will decide if it will
            put crystals into the hotbar or not.
        """
        # open inv and search for gacha crystals, click first crystal
        self._player.inventory.open()
        self._player.inventory.search(GACHA_CRYSTAL)
        self._player.inventory.select_slot(0)

        # put crystals into hotbar always on the first run
        if self._first_pickup:
            self._player.set_hotbar()
            self._first_pickup = False

        # open until no crystals left in inventory
        while self._player.inventory.has(GACHA_CRYSTAL, is_searched=True):
            self._player.spam_hotbar()
            self._player.pick_up()

        # go over the hotbar 5 more times to ensure no crystals left behind
        for _ in range(5):
            self._player.spam_hotbar()
        self._player.inventory.close()
        self._player.sleep(3)

    def deposit_dedis(self) -> dict[Item, int]:
        """Deposits all the dust / black pearls into the dedis.
        OCRs the amount amount deposited.

        Returns:
        -----------
        A dictionary containing the amounts of items deposited for dust and pearls
        """
        gains = {DUST: 0, BLACK_PEARL: 0}
        turns = [
            lambda: self._player.turn_x_by(40, delay=0.2),
            lambda: self._player.turn_y_by(-50, delay=0.2),
            lambda: self._player.turn_x_by(-80, delay=0.2),
            lambda: self._player.turn_y_by(50, delay=0.2),
        ]

        # go through each turn depositing into dedi
        for turn in turns:
            turn()

            item_deposited = self.dedi.deposit([DUST, BLACK_PEARL], get_amount=True)
            if item_deposited is None:
                continue
            item, amount = item_deposited
            if item == DUST:
                amount = self.validate_dust_amount(amount)
            gains[item] += amount

        # return to original position
        self._player.turn_x_by(40, delay=0.2)
        return gains

    def need_to_access_top_vault(self) -> bool:
        return any(
            self._player.inventory.has(item)
            for item in [
                TREE_PLATFORM,
                BEHEMOTH_GATE,
                BEHEMOTH_GATEWAY,
                METAL_GATE,
                METAL_GATEWAY,
            ]
        )

    def deposit_items(self) -> bool:
        """Puts the gear items into the vaults.

        Returns:
        --------
        Whether the vault is full after or before depositing items.
        """
        vault_full = False

        # put the grinding items in the left vault
        self._player.sleep(0.3)
        self._player.turn_90_degrees("left")
        self._player.sleep(1)
        self.vault.open()

        if not self.vault.inventory.is_full():
            self._player.inventory.drop_all(self.settings.drop_items)
            self._player.inventory.transfer_all(self.settings.keep_items)
            vault_full = self.vault.inventory.is_full()
        else:
            vault_full = True

        if not self.need_to_access_top_vault() or self.settings.stryder_depositing:
            self._get_timer()
            self.vault.close()
            return vault_full

        # turn to the upper vault
        self.vault.close()
        self._player.turn_90_degrees("right")
        self._player.look_up_hard()
        self.vault.open()

        if self.vault.inventory.is_full():
            self._player.inventory.drop_all()
            self._get_timer()
            self.vault.close()
            return vault_full

        self._player.inventory.transfer_all([METAL_GATE, TREE_PLATFORM])

        self._player.inventory.drop_all()
        self._get_timer()
        self.vault.inventory.close()

        return vault_full

    def validate_dust_amount(self, amount: int) -> int:
        """Checks if the given amount of dust is valid compared to the usual average.

        Parameters
        ----------
        amount :class:`int`:
            The amount of dust we think we got

        Returns
        --------
        The given amount if its within a valid range, else the average amount
        """
        try:
            average_amount = round(
                self._resources_made.get(DUST, 0) / self._total_pickups
            )
        except ZeroDivisionError:
            # assume 6000 dust / minute, or 100 / second
            average_amount = round(100 * self.settings.crystal_interval)

        if average_amount - 15000 < amount < average_amount + 15000:
            return amount
        return average_amount

    def create_embed(self, profit: dict[Item, int], time_taken: int) -> Embed:
        crystals = round(profit[DUST] / 120)
        embed = Embed(
            type="rich",
            title=f"Collected crystals at '{self._name}'!",
            color=0x07F2EE,
        )
        embed.add_field(name="Time taken:ㅤㅤㅤ", value=f"{time_taken} seconds")
        embed.add_field(name="Crystals opened:", value=f"~{crystals} crystals")

        for item, amount in profit.items():
            if not amount:
                continue

            formatted_amount = f"{amount:_}".replace("_", " ")
            embed.add_field(name=item.name, value=formatted_amount)

        missing = 3 - len(embed.fields) % 3
        for _ in range(missing if missing != 3 else 0):
            embed.add_field(name="\u200b", value="\u200b")
            
        embed.set_thumbnail(url=self.CRYSTAL_AVATAR)
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")

        return embed
