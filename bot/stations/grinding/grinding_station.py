import time
from itertools import cycle
from typing import Iterable

import cv2  # type: ignore[import]
from ark import (
    ArkWindow,
    Bed,
    Dinosaur,
    IndustrialGrinder,
    Player,
    Structure,
    TekDedicatedStorage,
    exceptions,
    items,
    tools,
)
from discord import Embed  # type: ignore[import]
from PIL import Image  # type: ignore[import]
from pytesseract import pytesseract as tes  # type: ignore[import]

from ...tools import format_seconds, mss_to_pil
from ...webhooks import InfoWebhook, TribeLogWebhook
from .._station import Station
from ._settings import GrindingStationSettings
from ._stations import Stations
from ._status import Status

# map common mistakes in the dedi OCR
DEDI_NUMBER_MAPPING = {"l": "1", "i": "1", "I": "1", "|": "1", "O": "0"}

# the default mats we assume when the dedis could not be determined
DEFAULT_MATS: dict[items.Item, int] = {
    items.SILICA_PEARL: 7000,
    items.PASTE: 5000,
    items.METAL_INGOT: 8757,
    items.ELECTRONICS: 900,
    items.CRYSTAL: 10000,
    items.HIDE: 20000,
}


class GrindingStation(Station):

    GRINDER_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/f/fe/Industrial_Grinder.png/revision/latest/scale-to-width-down/228?cb=20160728174054"
    EXOMEK_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/6/6d/Unassembled_Exo-Mek_%28Genesis_Part_2%29.png/revision/latest/scale-to-width-down/228?cb=20210603184626"
    ELECTRONICS_AVATAR = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/d/dd/Electronics.png/revision/latest/scale-to-width-down/228?cb=20150615100650"

    """Represents the grinding station on the gacha bot.

    The basic concept is to grind the gear from higher quality crystals into
    material to then craft turrets. The station is set ready by the crystal
    station when it notices the vault is full, until finished it then uses
    a `Status` enum to control the tasks.

    Parameters:
    -----------
    station_data :class:`StationData`:
        A dataclass containing data about the station

    player :class:`Player`:
        The player controller handle responsible for movement

    tribelog :class:`Tribelog`:
        The tribelog object to check tribelogs when spawning

    """
    _SUPPORTED_CRAFTABLES = {
        items.HEAVY_AUTO_TURRET,
        items.AUTO_TURRET,
        items.METAL_FOUNDATION,
        items.METAL_TRIANGLE,
        items.METAL_GATE,
        items.C4_DETONATOR,
        items.ROCKET_LAUNCHER,
        items.TEK_TURRET,
    }

    _CRAFTABLES_MAP = {item.name: item for item in _SUPPORTED_CRAFTABLES}

    def __init__(
        self,
        player: Player,
        tribelog: TribeLogWebhook,
        info_webhook: InfoWebhook,
    ) -> None:
        self._name = "grinding"
        self._player = player
        self._tribelog = tribelog
        self._webhook = info_webhook
        self.settings = GrindingStationSettings.load()

        if self.settings.item_to_craft == "None":
            self.item_to_craft = None
        else:
            self.item_to_craft = self._CRAFTABLES_MAP[self.settings.item_to_craft]

        self.bed = Bed("grinding")
        self.ready = False
        self.status = Status.WAITING_FOR_ITEMS
        self.current_station = "Gear Vault"

        self.grinder = IndustrialGrinder()
        self.dedi = TekDedicatedStorage()
        self.vault = Structure("Vault", "assets/templates/vault_capped.png")
        self.exo_mek = Dinosaur("Exo Mek", "assets/templates/exo_mek.png")
        self.screen = ArkWindow()

        self.STATION_MAPPING: dict[str, tuple | list] = {
            "Grinder": (self._player.turn_x_by, -50),
            "Exo Mek": (self._player.turn_x_by, -110),
            "Vault": (self._player.turn_x_by, -95),
            "Crystal": (self._player.turn_x_by, -70),
            "Hide": (self._player.turn_y_by, 40),
            "Ingot": (self._player.turn_x_by, -60),
            "Electronics": (self._player.turn_y_by, -40),
            "Pearls": (self._player.turn_x_by, -60),
            "Paste": (self._player.turn_y_by, 40),
            "Gear Vault": [
                (self._player.turn_y_by, -40),
                (self._player.turn_x_by, -70),
            ],
        }

    def spawn(self) -> None:
        """Override spawn method to set current station"""
        super().spawn()
        self.current_station = Stations.GEAR_VAULT

    def is_ready(self) -> bool:
        """Checks if the station is ready to be completed. Overriding the
        base `is_ready` method because the grinding station is responsible
        for multiple steps within the same instance.
        """
        if not self.settings.enabled:
            return False

        print(f"Checking whether grinding station is ready, status: '{self.status}'")
        if self.status == Status.WAITING_FOR_ITEMS:
            return self.ready

        if self.status == Status.AWAITING_EVALUTION:
            return True

        if self.status in [
            Status.CRAFTING_SUBCOMPONENTS,
            Status.AWAITING_CRAFT,
            Status.AWAITING_PICKUP,
        ]:
            return self.crafting_finished()

        raise ValueError(
            f"Grinding Station failed to match current status '{self.status}'!"
        )

    def complete(self) -> None:
        """Completes the current task at the grinding station."""
        # check what status we are on
        if self.status == Status.WAITING_FOR_ITEMS:
            self.grind_and_deposit()

        elif self.status == Status.AWAITING_EVALUTION:
            self.determine_materials()

        elif self.status == Status.CRAFTING_SUBCOMPONENTS:
            self.do_next_craft()

        elif self.status == Status.AWAITING_CRAFT:
            self.do_final_craft()

        elif self.status == Status.AWAITING_PICKUP:
            self.pickup_final_craft()

        else:
            raise ValueError(
                f"Grinding Station failed to match current status '{self.status}'!"
            )

    def grind_and_deposit(self) -> None:
        """Grinds the gear down, determines the amount of resources we have
        and calculates the optimal crafting."""
        self.spawn()
        start = time.time()

        self.grind_armor()
        self.grind_weapons()
        self.empty_grinder(turn_off=True)

        embed = self._create_grinding_finished_embed(round(time.time() - start))
        self._webhook.send_embed(embed)

        if self.item_to_craft is None:
            self._transfer_dedi_wall()
            self.ready = False
        else:
            self.status = Status.AWAITING_EVALUTION

    def determine_materials(self, debug: bool = False) -> None:
        assert self.item_to_craft is not None and self.item_to_craft.recipe is not None

        result = self.get_dedi_materials(debug)

        available_mats = result["determined"]
        undetermined = result["undetermined"]

        for item in undetermined:
            available_mats[item] = DEFAULT_MATS[item]

        available_mats[items.ORGANIC_POLYMER] = 5000

        self.current_station = Stations.ELECTRONICS
        img = self.screen.grab_screen((0, 0, 1920, 1080))

        for item in self.item_to_craft.recipe:
            if item in available_mats:
                continue

            self.turn_to(Stations.EXO_MEK)
            self.exo_mek.access()
            self.exo_mek.inventory.search(item)
            self.exo_mek.sleep(0.3)

            available_mats[item] = max(
                0,
                self.exo_mek.inventory.count(item) * item.stack_size
                - (0.5 * item.stack_size),
            )
        self.exo_mek.close()

        embed = self.create_available_materials_embed(available_mats, undetermined)
        self._webhook.send_embed(embed, img=img)
        self._player.sleep(3)

        self.compute_crafting_plan(available_mats)
        self.status = Status.CRAFTING_SUBCOMPONENTS

        embed = self.create_crafting_embed()
        self._webhook.send_embed(embed)

    def grind_armor(self) -> None:
        """Grind all the riot gear down, putting the polymer from the first grinding
        into the Exo Mek and dropping the rest. If a piece was not found, it will
        simply continue with the next one in the list.

        If any piece was found, after grinding all armor the crystal will be taken
        from the grinder and deposited into its dedi.
        """
        # pieces to grind
        armor = [
            items.RIOT_LEGGS,
            items.RIOT_CHEST,
            items.RIOT_GAUNTLETS,
            items.RIOT_BOOTS,
            items.MINER_HELMET,
            items.RIOT_HELMET,
        ]

        # flag to determine if any items were grinded
        amount_found = 0
        for piece in armor:

            # empty grinder before we grind miner helmets
            # to avoid overcapping and wasting electronics
            if piece is items.MINER_HELMET:
                self.vault.close()
                self.empty_grinder()

            if not self.take_item(piece):
                continue

            if piece is items.MINER_HELMET:
                self.grind(piece, [items.ORGANIC_POLYMER, items.ELECTRONICS])
            else:
                self.grind(piece, [items.ORGANIC_POLYMER, items.SILICA_PEARL])

            if amount_found < 2:
                self.put_into_exo_mek(items.ORGANIC_POLYMER)
            amount_found += 1

            # deposit the grinded items, turn back to gear vault
            self.deposit(
                [items.ELECTRONICS]
                if piece is items.MINER_HELMET
                else items.SILICA_PEARL
            )
            self.turn_to(Stations.GEAR_VAULT)

        self.vault.close()
        if amount_found:
            self.drop_script_from_grinder(items.CRYSTAL)

    def grind_weapons(self) -> None:
        """Grinds all the weapons in the Gear Vault. If a weapon was not found,
        it will simply continue with the next one.

        Poly from all weapons will be dropped, paste will be taken and directly
        deposited into the dedi. After grinding all weapons, the ingots will be
        taken and deposited.
        """
        weapons = [
            items.FABRICATED_PISTOL,
            items.FABRICATED_SNIPER,
            items.ASSAULT_RIFLE,
            items.PUMPGUN,
            items.LONGNECK,
            items.SIMPLE_PISTOL,
        ]
        for weapon in weapons:
            if not self.take_item(weapon):
                continue

            self.grind(weapon, [items.ORGANIC_POLYMER, items.PASTE])
            self.deposit(items.PASTE)
            self.turn_to(Stations.GEAR_VAULT)
        self._player.drop_all()

        self.drop_script_from_grinder(items.METAL_INGOT)

    def get_cycle(self, stations: Iterable[str]) -> cycle:
        """Converts the list of our stations to a `cycle` object starting at
        our current station to help find the quickest way to the target station.

        Parameters:
        -----------
        stations :class:`Iterable`:
            The stations to convert to the cycle

        Returns:
        ----------
        A `cycle` object with the iteration pointer on the current station.
        """
        stations = cycle(stations)

        # set the cycle pointer to current station
        for station in stations:
            if station == self.current_station:
                return stations
        raise Exception("Not sure how we got here...")

    def find_quickest_way_to(self, target_station: Stations) -> tuple[list[str], str]:
        """Finds the quickest way to the passed target station, forwards
        and backwards possibilities are considered, the shortest is returned.

        Parameters:
        -----------
        target_station :class:`Stations.enum`:
            The station to turn to

        Returns:
        --------
        A list containing the stations to go through to reach the target Stations.

        Raises:
        --------
        `InvalidStationError` if you passed a station that doesnt exist.
        """
        # ensure the passed station exists to avoid looping infinitely
        if not target_station in self.STATION_MAPPING:
            raise ValueError(f"{target_station} is not a valid station!")

        if target_station == self.current_station:
            return [], "stay"

        # remove values from keys to get an proper iterable
        stations = list(self.STATION_MAPPING)

        # get the amount of station to go through if we move forwards
        # use itertools cycle method to allow counting over lists end
        forward_path = []
        for station in self.get_cycle(stations):
            forward_path.append(station)
            if station == target_station:
                break

        backward_path = [self.current_station]
        for station in self.get_cycle(reversed(stations)):
            backward_path.append(station)
            if station == target_station:
                break

        # compare both resulting lists, return the shorter one together with
        # the direction
        if len(forward_path) < len(backward_path):
            return forward_path, "forward"
        return backward_path, "backwards"

    def turn_to(self, target_station: Stations) -> None:
        """Turns to the given station using the fastest way around possible.

        If we are going backwards, the turn amount is multiplies by -1 to
        get the opposite of the actual movement and go backwards instead.

        Parameters:
        -----------
        target_station :class:`Station` | `str`:
            The station to turn to
        """
        # get the quickest path and the direction
        path, direction = self.find_quickest_way_to(target_station)
        self._player.sleep(1)

        for station in path:
            self.current_station = station
            # when going backwards, done once the station is the target
            if direction == "backwards" and station == target_station:
                break

            # check if the station requires multiple turns
            # a station consists of the method (turn x...) + the value
            if isinstance(self.STATION_MAPPING[station], list):
                for func, amount in self.STATION_MAPPING[station]:
                    func(amount * (-1 if direction == "backwards" else 1))
                    self._player.sleep(0.3)
                continue

            func, amount = self.STATION_MAPPING[station]
            func(amount * (-1 if direction == "backwards" else 1))
            self._player.sleep(0.3)
        self._player.sleep(1)

    def grind(self, item: items.Item, take: list[items.Item]) -> None:
        """Turns to the grinder and grinds the item, then takes all requested
        items. Leaves the grinder in a closed state after finishing.

        Can be called with the grinder already being open or at any other
        station as long as the current station is CLOSED!

        Parameters:
        -----------
        grind :class:`Item`:
            The items to grind

        take :class:`list`:
            A list of Items to take after grinding
        """
        # open the grinder and transfer the items into it
        if not self.grinder.inventory.is_open():
            self.turn_to(Stations.GRINDER)

        self.grinder.open()
        self._player.inventory.transfer_all(item)
        self._player.sleep(0.5)

        # turn the grinder on if its not already, grind all the items
        self.grinder.turn_on()
        self.grinder.grind_all()

        for item in take:
            self.grinder.inventory.transfer_all(item)
        self.grinder.close()

    def deposit(self, items: list[items.Item] | items.Item) -> None:
        """Turns to the dedi for each item given and deposits it.

        Parameters:
        ------------
        items :class:`list` | `Item`:
            The item(s) to deposit as Item object(s)
        """
        # turn it into a list if only 1 item was passed
        if not isinstance(items, list):
            items = [items]

        # deposit
        for item in items:
            self.turn_to(Stations.from_item(item))
            self.dedi.deposit([item], get_amount=False)

    def take_item(self, item: items.Item) -> bool:
        """Turns to the gear vault and takes the specified item from it.
        Leaves the vault in a closed state.

        Can be called with the vault already open or at any other station
        as long as it is CLOSED.

        Parameters:
        -----------
        item :class:`Item`:
            The item to take, as Item object

        Returns:
        -----------
        Whether there was any of the specified item in the vault.
        """
        if not self.vault.inventory.is_open():
            self.turn_to(Stations.GEAR_VAULT)
            self.vault.open()

        # clear inventory, search for the target item
        self._player.inventory.drop_all()
        self.vault.inventory.search(item)
        self._player.sleep(0.5)

        # check if any items are within the vault
        if not self.vault.inventory.has(item, is_searched=True):
            return False

        # take all (remember search filter is active), close vault
        self.vault.inventory.transfer_all()
        self.vault.close()
        return True

    def put_into_exo_mek(self, items: list[items.Item] | items.Item) -> None:
        """Puts all given items into exo mek. Leaves the exo mek in a
        closed state.

        Parameters:
        -----------
        item :class:`list` | `Item`:
            The item(s) to put into the exo mek as item object(s)
        """
        # turn it into a list if only 1 item was passed
        if not isinstance(items, list):
            items = [items]

        if not self.exo_mek.inventory.is_open():
            self.turn_to(Stations.EXO_MEK)
            self.exo_mek.access()

        # deposit the items
        for item in items:
            self._player.inventory.transfer_all(item)
            self._player.sleep(0.5)
        self.exo_mek.close()

    def empty_grinder(self, turn_off: bool = False) -> None:
        """Empties the grinder by taking hide and despawning the rest.

        Parameters:
        ----------
        turn_off :class:`bool`:
            Whether to turn the grinder off after cleanup.
        """
        # get all the hide and deposit it
        self.turn_to(Stations.GRINDER)
        self.grinder.open()
        self.grinder.inventory.transfer_all(items.HIDE)
        self.grinder.close()
        self.deposit(items.HIDE)

        # drop all on the remaining items
        self.turn_to(Stations.GRINDER)
        self.grinder.open()
        for item in [items.FIBER, items.STONE, items.ANGLER_GEL, items.WOOD]:
            self.grinder.inventory.search(item)
            self.grinder.sleep(0.3)

            if self.grinder.inventory.has(item, is_searched=True):
                self.grinder.inventory.transfer_all(item)

        self._player.inventory.drop_all()

        # turn off grinder if requestes and close it
        if turn_off:
            self.grinder.turn_off()
        self.grinder.close()

    def drop_script_from_grinder(self, item: items.Item) -> None:
        """Drop scripts the given item from the grinder and puts it
        into its respective dedi, returns to Gear Vault upon finishing.
        """
        # drop script the items out
        self.turn_to(Stations.GRINDER)
        self._player.do_drop_script(item, self.grinder.inventory)
        self._player.turn_y_by(-163)

        # deposit the items, turn back to gear vault
        self.deposit(item)
        self.turn_to(Stations.GEAR_VAULT)

    def put_item_into_exo_mek(self, item: items.Item, amount: int) -> None:
        """Takes the given resource from its dedi and puts the given
        amount into the exo mek.

        Parameters:
        ------------
        item :class:`Item`:
            The item to put into the exo mek

        amount :class:`int`:
            The amount of the item to put into the exo mek
        """
        self.turn_to(Stations.from_item(item))
        self.dedi.open()
        self.dedi.inventory.transfer_all()

        self.dedi.close()
        self._player.sleep(1)

        # transfer the amount into the exo mek
        self.turn_to(Stations.EXO_MEK)
        self.exo_mek.access()

        if self.exo_mek.inventory.has(items.GACHA_CRYSTAL):
            # when travelling from the station before a bag can end up on the
            # bed, check if we opened one on accident.
            self._player.pick_up_bag()
            self.exo_mek.access()

        self._player.inventory.transfer(
            item, amount + item.stack_size, self.exo_mek.inventory
        )
        self.exo_mek.close()

        # put remaining resources back into dedi
        self.turn_to(Stations.from_item(item))
        self.dedi.deposit([item], get_amount=False)

    def get_dedi_screenshot(self, spawn: bool = True) -> Image.Image:
        """Grabs a screenshot of the dedi wall to later determine the
        amount of resources available.

        Parameters:
        -----------
        spawn :class:`bool`:
            Whether the bot should resync to the bed first

        Returns:
        ----------
        A PIL Image of the current dedi wall.
        """

        # sync to bed, look at dedi wall
        if spawn:
            self.spawn()
            self._player.turn_x_by(130)

        # looking up hard then down to make our hands move out of the
        # screen temporarily for better clarity
        self._player.hide_hands()

        # save the result, enable HUD and return the Image
        img = self.screen.grab_screen(region=(0, 0, 1920, 1080))

        self._player.sleep(0.5)
        self._player.disable_hud()

        return mss_to_pil(img)

    def walk_back_little(self) -> None:
        """Crouches and walks back a tiny bit, attempting to getting a better
        view on the dedis."""
        self._player.crouch()
        self._player.walk("s", 0.1)
        self._player.crouch()
        self._player.sleep(0.5)

    def amount_valid(self, item: items.Item, amount: int) -> bool:
        """Validates that the amount we think we OCR'd is within a valid range.

        Parameters:
        -----------
        item :class:`Item`:
            The item object we are determining the amount of

        amount :class:`int`:
            The amount of the item OCRing gave us.

        Returns:
        ----------
        Whether the amount is within a regular range.
        """
        expected = {
            items.SILICA_PEARL: (3000, 130000),
            items.PASTE: (7000, 180000),
            items.ELECTRONICS: (800, 10000),
            items.METAL_INGOT: (5000, 60000),
        }
        if self.item_to_craft is None:
            return True

        assert self.item_to_craft.recipe is not None

        # we dont care about crystal or hide
        if item not in expected or (
            item not in list(self.item_to_craft.recipe)
            and not any(
                subitem.recipe is not None for subitem in self.item_to_craft.recipe
            )
        ):
            return True

        # ensure the OCRd amount is within a f
        lower_range, upper_range = expected[item]
        return upper_range >= amount >= lower_range - 300

    def get_dedi_materials(self, debug: bool = False) -> dict:
        """Tries to get the dedi materials up to 10 times. Will return a dict
        of the material and its amount on the first successful attempt.

        Raises `DediNotFoundError` after 10 unsuccessful attempts.
        """

        dedi_to_region = {
            items.SILICA_PEARL: self.settings.pearls_region,
            items.PASTE: self.settings.paste_region,
            items.ELECTRONICS: self.settings.electronics_region,
            items.METAL_INGOT: self.settings.ingots_region,
            items.CRYSTAL: self.settings.crystal_region,
            items.HIDE: self.settings.hide_region,
        }

        img = self.get_dedi_screenshot(True)
        result: dict[str, dict[items.Item, int]] = {
            "determined": {},
            "undetermined": {},
        }

        for item, region in dedi_to_region.items():
            roi = img.crop(
                (region[0], region[1], region[0] + region[2], region[1] + region[3])
            )
            denoised_roi = self.screen.denoise_text(roi, self.settings.text_rgb, 22)
            amount: str = tes.image_to_string(
                denoised_roi,
                config="-c tessedit_char_whitelist=0123456789liI|O --psm 6",
            ).replace("\n", "")

            # replace common tesseract fuckups
            for char, new_char in DEDI_NUMBER_MAPPING.items():
                amount = amount.replace(char, new_char)
            if debug:
                cv2.imshow(f"{item.name} - {amount}", denoised_roi)
                cv2.waitKey(0)

            try:
                final_result = int(amount)
            except ValueError as e:
                print(e)
                final_result = 0

            # validate that the result is within a logical range
            if not self.amount_valid(item, final_result):
                result["undetermined"][item] = final_result
            else:
                result["determined"][item] = final_result

        return result

    def compute_crafting_plan(self, owned_items: dict[items.Item, int]):
        """Receives the list of materials we own and figures out the most
        'efficient' way to craft turrets mainly taking in consideration the
        balance between metal and electronics.

        It first calculates the usage of the crafted mats we have, and then
        calculates with pearls and ingots instead of electronics.

        Sets object variables `session_turrets`, `session_cost` and
        `electronics_to_craft`.

        Parameters:
        -----------
        owned_items :class:`dict`:
            A dict containing each item and the amount we have available
        """
        assert self.item_to_craft is not None and self.item_to_craft.recipe is not None

        amount, to_craft, total_cost = tools.compute_crafting_plan(
            self.item_to_craft, owned_items
        )

        self.session_crafts = amount
        self.subcomponents_to_craft = to_craft
        self.total_session_cost = total_cost

    def create_crafting_embed(self) -> Embed:
        """Sends an embed to the info webhook informing about the crafting
        plan that has been calculated for the ongoing session. Takes its data
        from the session class attributes."""
        assert self.item_to_craft is not None and self.item_to_craft.recipe is not None

        # reformat the amounts to make it look nicer
        formatted: dict[items.Item, str] = {}
        desired_order = [
            items.METAL_INGOT,
            items.PASTE,
            items.ELECTRONICS,
            items.SILICA_PEARL,
            items.CRYSTAL,
            items.HIDE,
            items.ORGANIC_POLYMER,
            items.ELEMENT,
        ]
        for resource, amount in self.total_session_cost.items():
            formatted[resource] = f"{amount:_}x".replace("_", " ")
        formatted = {k: formatted[k] for k in desired_order if k in formatted}

        # create embed, black sidebar
        embed = Embed(
            type="rich",
            title="Calculated crafting!",
            description="Required materials:",
            color=0x000000,
        )

        # add each resource to the embed, heavies and electronics on the
        # righthand side
        for resource, quantity in formatted.items():
            embed.add_field(name=f"{resource.name}:ㅤ", value=quantity.strip())

        embed.add_field(
            name="Expected Result:",
            value=f"{self.session_crafts}x {self.item_to_craft.name}",
        )

        embed.add_field(
            name="Subcomponents to craft:", value=f"{self.subcomponents_to_craft}"
        )

        # set exo mek image
        embed.set_thumbnail(url=self.EXOMEK_AVATAR)
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")

        # send the embed
        return embed

    def create_available_materials_embed(
        self, available: dict[items.Item, int], undetermined: dict[items.Item, int]
    ) -> Embed:
        """Sends an embed to the info webhook informing about the crafting
        plan that has been calculated for the ongoing session. Takes its data
        from the session class attributes."""
        # reformat the amounts to make it look nicer
        formatted: dict[items.Item, str] = {}
        desired_order = [
            items.METAL_INGOT,
            items.PASTE,
            items.ELECTRONICS,
            items.SILICA_PEARL,
            items.CRYSTAL,
            items.HIDE,
            items.ORGANIC_POLYMER,
            items.ELEMENT,
        ]
        for resource, amount in available.items():
            formatted[resource] = f"{amount:_}x".replace("_", " ")
        formatted = {k: formatted[k] for k in desired_order if k in formatted}

        # create embed, black sidebar
        embed = Embed(
            type="rich",
            title="Determined available materials!",
            description="Available materials:",
            color=0x000000,
        )

        if undetermined:
            embed.description = f"OCR'd invalid amounts for {undetermined}"

        for resource, quantity in formatted.items():
            embed.add_field(name=f"{resource.name}:ㅤ", value=quantity.strip())

        embed.set_thumbnail(url=self.EXOMEK_AVATAR)

        # send the embed
        return embed

    def create_embed(self, profit: int, time_taken: int) -> Embed:
        """Creates the final embed displaying the time taken and the amount
        of heavies that have been crafted."""
        embed = Embed(
            type="rich",
            title="Finished crafting!",
            color=0x133DE7,
        )
        embed.add_field(name=f"Time taken:ㅤ", value=f"{time_taken} seconds")
        embed.add_field(name="Heavies crafted:", value=profit)
        embed.set_thumbnail(url=self.EXOMEK_AVATAR)
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")
        return embed

    def crafting_finished(self) -> bool:
        """Checks if more than 2 minutes passed since the last electronic
        queue up."""

        try:
            time_diff = round(time.time() - self.last_crafted)
            time_left = max(0, (3 * 60) - time_diff)
            if not time_left:
                print("Grinding station has finished crafting.")
                return True
            print(f"{format_seconds(time_left)} left on crafting components..")
            return False
        except AttributeError:
            return True

    def craft(self, item: items.Item, amount: int, put_items: bool = True) -> None:
        """Turns to the exo mek and crafts the given amount of the given item.

        Parameters:
        -----------
        item :class:`Item`:
            The item to craft

        amount :class:`int`:
            The amount to craft, will be A spammed if more than 50.
        """
        assert item.recipe is not None

        if put_items:
            for material, per_craft in item.recipe.items():
                if material is items.ORGANIC_POLYMER:
                    continue

                self.put_item_into_exo_mek(material, per_craft * amount)

        self.turn_to(Stations.EXO_MEK)
        self.exo_mek.access()
        self.exo_mek.inventory.open_tab("crafting")
        self.exo_mek.inventory.craft(item, amount)
        self.exo_mek.inventory.open_tab("inventory")

    def clear_up_exo_mek(self) -> None:
        """Clears the exo mek after a crafting session."""
        self.turn_to(Stations.VAULT)
        self.vault.open()
        self._player.inventory.transfer_all(self.item_to_craft)
        self.vault.close()

        try:
            # clean up the remaining mats from exo mek
            self.turn_to(Stations.EXO_MEK)
            self._player.do_drop_script(items.METAL_INGOT, self.exo_mek.inventory)
            self._player.turn_y_by(-163)
            self.deposit(items.METAL_INGOT)

        except exceptions.NoItemsAddedError:
            print("Failed to take metal from the exo mek!")
            self.exo_mek.close()
            self._player.crouch()

        # get the non heavy mats, drop all on the rest (poly)
        self.turn_to(Stations.EXO_MEK)
        self.exo_mek.access()
        for item in [items.SILICA_PEARL, items.PASTE, items.ELECTRONICS]:
            self.exo_mek.inventory.transfer_all(item)

        self.exo_mek.inventory.drop_all([items.ORGANIC_POLYMER])
        self.exo_mek.close()

        # deposit the lightweight mats
        for item in [items.SILICA_PEARL, items.PASTE, items.ELECTRONICS]:
            self.deposit(item)

    def do_final_craft(self, spawn: bool = True) -> None:
        """Crafts the turrets after all electronics have been crafted.
        Posts the final result to discord as an embed displaying how
        many Heavies ended up crafting (as the result may vary from the
        excpected amount).
        """
        assert self.item_to_craft is not None and self.item_to_craft.recipe is not None
        if spawn:
            self.spawn()

        for item, amount_per_craft in self.item_to_craft.recipe.items():
            if item in [items.ORGANIC_POLYMER, items.AUTO_TURRET, items.ELEMENT]:
                continue

            amount_needed = amount_per_craft * self.session_crafts
            self.put_item_into_exo_mek(item, amount_needed)

        self.craft(self.item_to_craft, self.session_crafts, put_items=False)
        if self.session_crafts < 50:
            while self.exo_mek.inventory.is_crafting():
                self._player.sleep(0.3)
            self.pickup_final_craft(spawn=False)
        else:
            self.last_crafted = time.time()
            self.status = Status.AWAITING_PICKUP

    def pickup_final_craft(self, spawn: bool = True) -> None:
        assert self.item_to_craft is not None
        if spawn:
            self.spawn()

        self.turn_to(Stations.EXO_MEK)

        self.exo_mek.access()
        img = self.screen.grab_screen(self.exo_mek.inventory._ITEM_REGION)
        self.exo_mek.inventory.transfer_all(self.item_to_craft)
        self._player.sleep(1)

        stacks_crafted = self._player.inventory.count(self.item_to_craft)
        self._add_crafts_to_statistics(stacks_crafted)
        self.exo_mek.close()

        embed = self._create_items_picked_up_embed(stacks_crafted)
        self._webhook.send_embed(embed, img=img)

        self.clear_up_exo_mek()
        try:
            self._transfer_vault()
            self._transfer_dedi_wall()
        except Exception as e:
            self._webhook.send_error("Transferring items", e)

        self.status = Status.WAITING_FOR_ITEMS
        self.ready = False

    def _add_crafts_to_statistics(self, crafts: int) -> None:
        assert self.item_to_craft is not None

        self.statistics[self.item_to_craft.name] = (
            self.statistics.get(self.item_to_craft.name, 0)
            + crafts * self.item_to_craft.stack_size
        )

    def do_next_craft(self, spawn: bool = True) -> None:
        """Checks if we need to queue another 1000 electronics to reach the
        total needed amount. Returns `False` if we dont, else `True`.

        This method is intended to be checked every 4 minutes by the main
        gacha bot function to either spawn and queue new electronics, or
        start crafting the turrets.
        """
        if not self.subcomponents_to_craft:
            self.do_final_craft(spawn=True)
            return

        if spawn:
            self.spawn()

        for item, amount in self.subcomponents_to_craft.items():
            assert item.recipe is not None
            if not amount:
                continue

            craft_amount = min(amount, 1000)
            self.craft(item, craft_amount)
            self.subcomponents_to_craft[item] -= craft_amount
            self.last_crafted = time.time()
            break

        img = self.screen.grab_screen(self.exo_mek.inventory.CRAFTING_QUEUE)
        self._player.drop_all()
        self._webhook.send_embed(
            self._create_components_queued_embed(item, craft_amount), img=img
        )

        if not any(amount_left for amount_left in self.subcomponents_to_craft.values()):
            self.status = Status.AWAITING_CRAFT
            if amount < 50:
                self.do_final_craft(spawn=False)
        elif amount < 50:
            self._player.sleep(10)
            self.do_next_craft(spawn=False)

    def _create_grinding_finished_embed(self, time_taken: int) -> Embed:
        """Creates an embed to display the materials we have available to craft."""
        embed = Embed(
            type="rich",
            title="Finished grinding!",
            description="Grinding all gear in the gear vault completed.",
            color=0x03DD74,
        )

        embed.add_field(name="Time taken:", value=format_seconds(time_taken))
        embed.add_field(name="Item to craft:", value=self.item_to_craft)

        embed.set_thumbnail(url=self.GRINDER_AVATAR)
        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")

        return embed

    def _create_items_picked_up_embed(self, stacks: int) -> Embed:
        assert self.item_to_craft is not None

        embed = Embed(
            type="rich",
            title="Finished grinding station!",
            description="The final result has been picked up.",
            color=0x000000,
        )
        total = self.item_to_craft.stack_size * stacks
        if self.item_to_craft.stack_size > 1:
            amount = f"{total} - {total + self.item_to_craft.stack_size}"
        else:
            amount = str(total)

        embed.add_field(name="Item:", value=self.item_to_craft.name)
        embed.add_field(name="Amount crafted:", value=amount)

        embed.set_thumbnail(url=self.EXOMEK_AVATAR)
        return embed

    def _create_components_queued_embed(self, item: items.Item, amount: int) -> Embed:
        embed = Embed(
            type="rich",
            title="Subcomponents have been queued!",
            description="A chunk of subcomponents for the final craft has been queued up.",
            color=0x000000,
        )

        embed.add_field(name="Component:", value=item.name)
        embed.add_field(name="Amount queued:", value=amount)
        embed.add_field(name="Amount left:", value=self.subcomponents_to_craft[item])

        if item is items.ELECTRONICS:
            embed.set_thumbnail(url=self.ELECTRONICS_AVATAR)
        else:
            embed.set_thumbnail(url=self.EXOMEK_AVATAR)

        embed.set_footer(text="Ling Ling Bot - Kenny#0947 - discord.gg/2mPhj8xhS5")
        return embed

    def _transfer_dedi_wall(self) -> None:
        """Spawns at the grindingtransfer bed and transfers the materials
        left after crafting into the next dediwall, so that the ARB station
        can use the metal and it does not clog up the grinding dedis.

        Im sure theres a cleaner way to do this but it works.
        """
        bed = Bed("dedi_transfer")
        self._player.look_down_hard()
        self._player.prone()
        bed.spawn()
        self._tribelog.check_tribelogs()
        self._player.spawn_in()

        for i in range(2):
            # transfer pearls and paste
            self._player.turn_x_by(-90, delay=0.5)
            if i != 0:
                self._player.turn_y_by(50, delay=0.5)

            self.dedi.open()
            self.dedi.inventory.transfer_all()
            self.dedi.close()
            self._player.sleep(2)

            for _ in range(2):
                self._player.turn_x_by(90, delay=0.5)
            self.dedi.deposit([items.SILICA_PEARL], get_amount=False)
            self._player.turn_x_by(-90, delay=0.5)
            self._player.turn_x_by(-90, delay=0.5)

            self.dedi.deposit([items.PASTE], get_amount=False)
            self._player.turn_x_by(90, delay=0.5)

            if i != 0:
                self._player.turn_y_by(-50, delay=0.5)

        self._player.turn_x_by(-160, delay=0.5)

        # take electronics
        self.dedi.open()
        self.dedi.inventory.transfer_all()
        self.dedi.close()
        self._player.sleep(2)

        # take metal
        self._player.turn_y_by(50)
        self.dedi.open()
        self.dedi.inventory.transfer_all()
        self.dedi.close()
        self._player.sleep(2)

        for _ in range(2):
            self._player.turn_x_by(160, delay=0.5)

        self.dedi.deposit([items.METAL_INGOT], get_amount=False)
        self._player.turn_y_by(-50, delay=0.5)
        self.dedi.deposit([items.ELECTRONICS], get_amount=False)

    def _transfer_vault(self) -> None:
        bed = Bed("vault_transfer")
        self._player.look_down_hard()
        self._player.prone()
        bed.spawn()
        self._player.spawn_in()

        self.vault.open()
        self.vault.inventory.transfer_all()
        self.vault.close()

        for turn in [-100, -50, -55, -50]:
            self._player.turn_x_by(turn, delay=0.5)

            self.vault.open()
            self._player.inventory.transfer_all()
            self.vault.close()
            self._player.sleep(0.5)
