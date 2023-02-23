import time
from itertools import cycle
from math import floor
from typing import Iterable

from ark import (ArkWindow, Bed, Dinosaur, IndustrialGrinder, Player,
                 Structure, TekDedicatedStorage, TribeLog, exceptions, items)
from discord import Embed  # type: ignore[import]
from PIL import Image  # type: ignore[import]
from pytesseract import pytesseract as tes  # type: ignore[import]

from ...tools import mss_to_pil
from ...webhooks import InfoWebhook
from .._station import Station
from ._exceptions import DedisNotDetermined
from ._stations import Stations
from ._status import Status

# map costs for turrets
AUTO_TURRET_COST = {
    items.PASTE: 50,
    items.ELECTRONICS: 70,
    items.METAL_INGOT: 140,
    items.ORGANIC_POLYMER: 20,
}
TURRET_COST = {
    items.PASTE: 200,
    items.ELECTRONICS: 270,
    items.METAL_INGOT: 540,
    items.ORGANIC_POLYMER: 70,
}

# map common mistakes in the dedi OCR
DEDI_NUMBER_MAPPING = {"l": "1", "i": "1", "I": "1", "|": "1", "O": "0"}

# the default mats we assume when the dedis could not be determined
DEFAULT_MATS: dict[items.Item, int] = {
    items.SILICA_PEARL: 5211,
    items.PASTE: 2600,
    items.METAL_INGOT: 8757,
    items.ELECTRONICS: 1773,
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

    _PEARLS_DEDI = (25, 350, 510, 355)
    _PASTE_DEDI = (17, 697, 560, 370)
    _ELECTRONICS_DEDI = (593, 390, 590, 303)
    _INGOT_DEDI = (570, 730, 640, 305)
    _CRYSTAL_DEDI = (1245, 365, 560, 315)
    _HIDE_DEDI = (1240, 690, 613, 355)

    def __init__(
        self,
        player: Player,
        tribelog: TribeLog,
        info_webhook: InfoWebhook,
    ) -> None:
        self._player = player
        self._tribelog = tribelog
        self._webhook = info_webhook

        self._name = "grinding"
        self.bed = Bed("grinding")
        self.ready = False
        self.status = Status.WAITING_FOR_ITEMS
        self.current_station = "Gear Vault"

        self.grinder = IndustrialGrinder()
        self.dedi = TekDedicatedStorage()
        self.vault = Structure("Vault", "templates/vault_capped.png")
        self.exo_mek = Dinosaur("Exo Mek", "templates/exo_mek.png")
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
        if self.status == Status.WAITING_FOR_ITEMS:
            # ready property set by the crystal station if the vault is full
            return self.ready

        if self.status == Status.AWAITING_EVALUTION:
            return True

        if self.status == Status.QUEUING_ELECTRONICS:
            # already grinded recently, check if electronics need to be queued
            return self.electronics_finished()

        if self.status == Status.AWAITING_CRAFT:
            # we are expecting to craft turrets after the final electronic queue
            return self.electronics_finished()

        raise ValueError(
            f"Grinding Station failed to match current status '{self.status}'!"
        )

    def complete(self) -> None:
        """Completes the current task at the grinding station."""
        # check what status we are on
        if self.status == Status.WAITING_FOR_ITEMS:
            self.grind_and_deposit()

        if self.status == Status.AWAITING_EVALUTION:
            self.determine_materials()

        if self.status == Status.QUEUING_ELECTRONICS:
            self.craft_electronics()

        if self.status == Status.AWAITING_CRAFT:
            self.craft_turrets()

        raise ValueError(
            f"Grinding Station failed to match current status '{self.status}'!"
        )

    def grind_and_deposit(self) -> None:
        """Grinds the gear down, determines the amount of resources we have
        and calculates the optimal crafting."""
        self.spawn()

        # get all resources from grinding, turn off grinder when finished
        self.grind_armor()
        self.grind_weapons()
        self.empty_grinder(turn_off=True)

        self.status = Status.AWAITING_EVALUTION

    def determine_materials(self) -> None:
        try:
            available_mats = self.get_dedi_materials()
        except DedisNotDetermined:
            print("WARNING! Unable to determine dedis. Assuming default materials.")
            available_mats = DEFAULT_MATS

        self.compute_crafting_plan(available_mats)
        self.status = Status.QUEUING_ELECTRONICS
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
        any_found = False
        for piece in armor:

            # empty grinder before we grind miner helmets
            # to avoid overcapping and wasting electronics
            if piece is items.MINER_HELMET:
                self.vault.inventory.close()
                self.empty_grinder()

            if not self.take_item(piece):
                continue

            if piece is items.MINER_HELMET:
                self.grind(piece, [items.ORGANIC_POLYMER, items.ELECTRONICS])
            else:
                self.grind(piece, [items.ORGANIC_POLYMER, items.SILICA_PEARL])

            if not any_found:
                self.put_into_exo_mek(items.ORGANIC_POLYMER)
            else:
                self._player.drop_all([items.ORGANIC_POLYMER])
            any_found = True

            # deposit the grinded items, turn back to gear vault
            self.deposit(
                [items.ELECTRONICS]
                if piece is items.MINER_HELMET
                else items.SILICA_PEARL
            )
            self.turn_to(Stations.GEAR_VAULT)

        self.vault.inventory.close()
        if any_found:
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
            # continue with next item if no item was found
            if not self.take_item(weapon):
                continue

            # grind the weapons, take the relevant mats
            self.grind(weapon, [items.ORGANIC_POLYMER, items.PASTE])
            self.deposit(items.PASTE)
            self.turn_to(Stations.GEAR_VAULT)
        self._player.drop_all()

        # get the metal and deposit it into the dedi
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
        # convert to cycle
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
        print(
            f"Target {target_station}, currently at: {self.current_station}, path: {path, direction}"
        )
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

        self.grinder.inventory.open()
        self._player.inventory.transfer_all(item)
        self._player.sleep(0.5)

        # turn the grinder on if its not already, grind all the items
        self.grinder.turn_on()
        self.grinder.grind_all()

        for item in take:
            self.grinder.inventory.transfer_all(item)
        self.grinder.inventory.close()

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
            self.vault.inventory.open()

        # clear inventory, search for the target item
        self._player.inventory.drop_all()
        self.vault.inventory.search(item)
        self._player.sleep(0.5)

        # check if any items are within the vault
        if not self.vault.inventory.has(item):
            return False

        # take all (remember search filter is active), close vault
        self.vault.inventory.transfer_all()
        self.vault.inventory.close()
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
            self.exo_mek.inventory.open()

        # deposit the items
        for item in items:
            self._player.inventory.transfer_all(item)
            self._player.sleep(0.5)
        self.exo_mek.inventory.close()

    def empty_grinder(self, turn_off: bool = False) -> None:
        """Empties the grinder by taking hide and despawning the rest.

        Parameters:
        ----------
        turn_off :class:`bool`:
            Whether to turn the grinder off after cleanup.
        """
        # get all the hide and deposit it
        self.turn_to(Stations.GRINDER)
        self.grinder.inventory.open()
        self.grinder.inventory.transfer_all(items.HIDE)
        self.grinder.inventory.close()
        self.deposit(items.HIDE)

        # drop all on the remaining items
        self.turn_to(Stations.GRINDER)
        self.grinder.inventory.open()

        self.grinder.inventory.transfer_all(items.FIBER)
        self.grinder.inventory.transfer_all(items.ANGLER_GEL)
        self.grinder.inventory.transfer_all(items.WOOD)
        self._player.inventory.drop_all()

        # turn off grinder if requestes and close it
        if turn_off:
            self.grinder.turn_off()
        self.grinder.inventory.close()

    def drop_script_from_grinder(self, item: items.Item) -> None:
        """Drop scripts the given item from the grinder and puts it
        into its respective dedi, returns to Gear Vault upon finishing.
        """
        # drop script the items out
        self.turn_to(Stations.GRINDER)
        self._player.do_drop_script(item, self.grinder)
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
        self.dedi.inventory.open()
        self.dedi.inventory.transfer_all()

        self.dedi.inventory.close()
        self._player.sleep(1)

        # transfer the amount into the exo mek
        self.turn_to(Stations.EXO_MEK)
        self.exo_mek.inventory.open()

        if self.exo_mek.inventory.has(items.GACHA_CRYSTAL):
            # when travelling from the station before a bag can end up on the
            # bed, check if we opened one on accident.
            self._player.pick_up_bag()
            self.exo_mek.inventory.open()

        self._player.inventory.transfer(item, amount, self.exo_mek.inventory)
        self.exo_mek.inventory.close()

        # put remaining resources back into dedi
        self.turn_to(Stations.from_item(item))
        self.dedi.deposit([item], get_amount=False)

    def find_dedi(self, item: items.Item, img: Image.Image) -> tuple:
        """Returns the position of the items dedi within the Image."""
        return self.dedi.window.locate_in_image(
            f"templates/{item.search_name}_dedi.png",
            img,
            confidence=0.6,
            grayscale=True,
        )

    def find_all_dedi_positions(
        self, image: Image.Image
    ) -> dict[items.Item, Image.Image] | None:
        """Finds the position of all dedi texts within the given image.

        Parameters:
        ----------
        image :class:`Image.Image`:
            A PIL Image representing a screenshot of all dedis with non bugged items.

        Returns:
        ---------
        A dict containing each resource with its corresponding dedi text image.
        """
        images = {}
        for dedi in (
            items.SILICA_PEARL,
            items.PASTE,
            items.METAL_INGOT,
            items.ELECTRONICS,
            items.CRYSTAL,
            items.HIDE,
        ):
            region = self.find_dedi(dedi, image)
            if not region:
                print(f"Failed to find dedi: {dedi.name}")
                return None

            # convert bc grab screen is retarded + extend boundaries
            region = int(region[0] - 80), int(region[1] + region[3] + 5), 350, 130

            # open it as PIL Image, crop out the calculated region of interest
            images[dedi] = image.crop(
                (region[0], region[1], region[0] + region[2], region[1] + region[3])
            )

        return images

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
            items.SILICA_PEARL: (6000, 60000),
            items.PASTE: (7000, 180000),
            items.ELECTRONICS: (800, 10000),
            items.METAL_INGOT: (9000, 60000),
        }
        # we dont care about crystal or hide
        if item not in expected:
            return True

        # ensure the OCRd amount is within a f
        lower_range, upper_range = expected[item]
        return upper_range >= amount >= lower_range - 300

    def get_dedi_materials(self) -> dict:
        """Tries to get the dedi materials up to 10 times. Will return a dict
        of the material and its amount on the first successful attempt.

        Raises `DediNotFoundError` after 10 unsuccessful attempts.
        """

        dedi_to_region = {
            items.SILICA_PEARL: self._PEARLS_DEDI,
            items.PASTE: self._PASTE_DEDI,
            items.ELECTRONICS: self._ELECTRONICS_DEDI,
            items.METAL_INGOT: self._INGOT_DEDI,
            items.CRYSTAL: self._CRYSTAL_DEDI,
            items.HIDE: self._HIDE_DEDI,
        }

        img = self.get_dedi_screenshot(True)
        amounts = {}
        for item, region in dedi_to_region.items():
            roi = img.crop(
                (region[0], region[1], region[0] + region[2], region[1] + region[3])
            )
            denoised_roi = self.screen.denoise_text(roi, (123, 233, 232), 22)
            amount: str = tes.image_to_string(
                denoised_roi, config="-c tessedit_char_whitelist=0123456789liI|O --psm 6"
            ).replace("\n", "")

            # replace common tesseract fuckups
            for char, new_char in DEDI_NUMBER_MAPPING.items():
                amount = amount.replace(char, new_char)
            final_result = int(amount)

            # validate that the result is within a logical range
            if not self.amount_valid(item, final_result):
                raise ValueError(
                    f"Invalid amount of resources for {item.name}: {final_result}"
                )
            print(f"Determined {item.name}: {final_result}")
            amounts[item] = int(final_result)

        # add material and its amount to our dict
        return amounts

    def create_available_material_embed(
        self, owned_mats: dict[items.Item, int]
    ) -> Embed:
        """Creates an embed to display the materials we have available to craft.

        Parameters:
        ----------
        owned_mats :class:`dict`:
            A dictionary containing each item and the total amount we have

        Returns:
        ----------
        A `discord.Embed` displaying the items and amount.
        """
        formatted: dict = {}
        desired_order = [
            items.METAL_INGOT,
            items.PASTE,
            items.ELECTRONICS,
            items.SILICA_PEARL,
            items.HIDE,
            items.CRYSTAL,
        ]

        for item, amount in owned_mats.items():
            formatted[item] = f"{amount:_}x".replace("_", " ")
        formatted = {k: formatted[k] for k in desired_order}

        embed = Embed(
            type="rich",
            title="Finished grinding!",
            description="Available materials:",
            color=0x03DD74,
        )

        for item, amount in formatted.items():
            embed.add_field(name=f"{item}:ㅤ", value=amount)

        embed.set_thumbnail(url=self.GRINDER_AVATAR)
        embed.set_footer(text="Ling Ling on top!")

        return embed

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
        
        # set our costs, no pearls for now
        cost = {items.PASTE: 0, items.METAL_INGOT: 0, items.ELECTRONICS: 0}
        # find how many turrets we can craft right away
        lowest_1 = min(
            owned_items[material] / TURRET_COST[material] for material in cost
        )

        # set the inital cost
        phase_1 = {
            items.PASTE: int(TURRET_COST[items.PASTE] * lowest_1),
            items.METAL_INGOT: int(TURRET_COST[items.METAL_INGOT] * lowest_1),
            items.ELECTRONICS: int(TURRET_COST[items.ELECTRONICS] * lowest_1),
        }

        # add the initial cost, remove it from the owned mats
        for material in phase_1:
            cost[material] += phase_1[material]
            owned_items[material] -= phase_1[material]

        # set new turret cost using pearls and more ingots instead, set
        # pearl value
        raw_turret_cost = {
            items.PASTE: 200,
            items.SILICA_PEARL: 270 * 3,
            items.METAL_INGOT: 540 + 270,
        }
        cost[items.SILICA_PEARL] = 0

        # once again get the amount of craftable turrets, create phase 2 cost
        lowest_2 = min(
            owned_items[material] / raw_turret_cost[material]
            for material in raw_turret_cost
        )
        phase_2 = {
            items.PASTE: int(raw_turret_cost[items.PASTE] * lowest_2),
            items.METAL_INGOT: int(raw_turret_cost[items.METAL_INGOT] * lowest_2),
            items.SILICA_PEARL: int(raw_turret_cost[items.SILICA_PEARL] * lowest_2),
        }

        # add each material to the total cost, electronics to craft is now
        # pearls / 3
        for material in phase_2:
            cost[material] += phase_2[material]

        # flatten some of the needed amounts to get the exact amounts required
        cost[items.PASTE] -= cost[items.PASTE] % 200
        cost[items.SILICA_PEARL] -= cost[items.SILICA_PEARL] % 3

        # calculate the total electronics we will end up with to discard
        # surplus
        total_elec = cost[items.SILICA_PEARL] / 3 + cost[items.ELECTRONICS]
        crafting_too_much = total_elec % 270
        cost[items.SILICA_PEARL] -= round(crafting_too_much * 3)
        cost[items.METAL_INGOT] -= round(crafting_too_much)

        # dicard surplus metal, EXCLUDING the cost for electronics
        cost[items.METAL_INGOT] -= (
            round(cost[items.METAL_INGOT] - (cost[items.SILICA_PEARL] / 3)) % 540
        )

        # set session costs
        self.electronics_to_craft = round(cost[items.SILICA_PEARL] / 3)
        self.electronics_crafted = 0
        self.session_turrets = floor(lowest_1 + lowest_2)
        self.session_cost = cost
        print(
            f"Need to craft {self.electronics_to_craft} electronics for {self.session_turrets} Turrets"
        )

    def create_crafting_embed(self) -> Embed:
        """Sends an embed to the info webhook informing about the crafting
        plan that has been calculated for the ongoing session. Takes its data
        from the session class attributes."""

        # reformat the amounts to make it look nicer
        formatted = {}
        desired_order = [
            items.METAL_INGOT,
            items.PASTE,
            items.ELECTRONICS,
            items.SILICA_PEARL,
        ]
        for resource in self.session_cost:
            formatted[resource] = f"{self.session_cost[resource]:_}x".replace("_", " ")
        formatted = {k: formatted[k] for k in desired_order}

        # create embed, black sidebar
        embed = Embed(
            type="rich",
            title="Calculated crafting!",
            description="Required materials:",
            color=0x000000,
        )

        # add each resource to the embed, heavies and electronics on the
        # righthand side
        for resource, amount in formatted.items():
            embed.add_field(name=f"{resource.name}:ㅤ", value=amount)
            if resource == items.PASTE:
                embed.add_field(
                    name="Expected Result:",
                    value=f"{self.session_turrets} Heavy Turrets",
                )
        embed.add_field(
            name="Electronics to craft:", value=f"{self.electronics_to_craft}x"
        )

        # set exo mek image
        embed.set_thumbnail(url=self.EXOMEK_AVATAR)
        embed.set_footer(text="Ling Ling on top!")

        # send the embed
        return embed

    def create_electronics_embed(self, time_taken: int) -> Embed:
        """Sends an embed to the info webhook informing that electronics
        have been queued. Contains the time taken to queue the electronics
        and how many have been crafted/how many to craft are left.

        Parameters:
        ------------
        time_taken :class:`time`:
            The timestamp when the queue function was started
        """
        # create embed, yellowsidebar
        embed = Embed(
            type="rich",
            title="Queued electronics!",
            color=0xFCFC2C,
        )

        # add contents
        embed.add_field(
            name=f"Time taken:",
            value=f"{time_taken} seconds",
        )
        embed.add_field(
            name="Crafted:",
            value=f"{self.electronics_crafted}/{self.electronics_to_craft}",
        )

        # set electronics picture
        embed.set_thumbnail(url=self.ELECTRONICS_AVATAR)
        embed.set_footer(text="Ling Ling on top!")

        # send to the webhook as Ling Ling
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
        embed.set_footer(text="Ling Ling on top!")
        return embed

    def electronics_finished(self) -> bool:
        """Checks if more than 2 minutes passed since the last electronic
        queue up."""
        try:
            time_diff = round(time.time() - self.last_crafted)
            return time_diff > 120

        except AttributeError:
            # last_crafted is not yet set, so no electronics are queued
            return True

    def craft(self, item: items.Item, amount: int) -> None:
        """Turns to the exo mek and crafts the given amount of the given item.

        Parameters:
        -----------
        item :class:`Item`:
            The item to craft

        amount :class:`int`:
            The amount to craft, will be A spammed if more than 50.
        """
        if not self.exo_mek.inventory.is_open():
            self.turn_to(Stations.EXO_MEK)
            self.exo_mek.inventory.open()

        self.exo_mek.inventory.open_tab("crafting")
        self.exo_mek.inventory.craft(item, amount)
        self.exo_mek.inventory.open_tab("inventory")
        self.exo_mek.inventory.close()

    def transfer_turret_resources(self) -> None:
        """Transfers all resources needed for turrets into the exo mek.

        Handles:
        ----------
        `NoItemsDepositedError` up to 3 times when failing to deposit the
        remaining items by resyncing to the bed and trying again.
        """

        self.put_item_into_exo_mek(items.PASTE, self.session_cost[items.PASTE])

        # subtract the amount of ingots used to craft electronics
        self.put_item_into_exo_mek(
            items.METAL_INGOT,
            self.session_cost[items.METAL_INGOT] - self.electronics_to_craft,
        )

        # add the amount of electronics crafted to determine the total stacks
        self.put_item_into_exo_mek(
            items.ELECTRONICS,
            self.session_cost[items.ELECTRONICS] + self.electronics_to_craft,
        )

    def clear_up_exo_mek(self) -> None:
        """Clears the exo mek after a crafting session."""
        self.turn_to(Stations.VAULT)
        self.vault.inventory.open()
        self._player.inventory.transfer_all(items.HEAVY_AUTO_TURRET)
        self.vault.inventory.close()

        try:
            # clean up the remaining mats from exo mek
            self.turn_to(Stations.EXO_MEK)
            self._player.do_drop_script(
                items.METAL_INGOT, self.exo_mek  # type:ignore[arg-type]
            )
            self._player.turn_y_by(-163)
            self.deposit(items.METAL_INGOT)

        except exceptions.NoItemsAddedError:
            print("Failed to take metal from the exo mek!")
            self.exo_mek.inventory.close()
            self._player.crouch()

        # get the non heavy mats, drop all on the rest (poly)
        self.turn_to(Stations.EXO_MEK)
        self.exo_mek.inventory.open()
        for item in [items.SILICA_PEARL, items.PASTE, items.ELECTRONICS]:
            self.exo_mek.inventory.transfer_all(item)

        self.exo_mek.inventory.drop_all()
        self.exo_mek.inventory.close()

        # deposit the lightweight mats
        for item in [items.SILICA_PEARL, items.PASTE, items.ELECTRONICS]:
            self.deposit(item)

    def craft_turrets(self) -> None:
        """Crafts the turrets after all electronics have been crafted.
        Posts the final result to discord as an embed displaying how
        many Heavies ended up crafting (as the result may vary from the
        excpected amount).
        """
        # spawn and get the resources
        self.spawn()
        start = time.time()
        try:
            self.transfer_turret_resources()

            # craft the turrets
            self.craft(items.AUTO_TURRET, self.session_turrets)
            self.craft(items.HEAVY_AUTO_TURRET, self.session_turrets + 3)

            # take out the turrets
            self.exo_mek.inventory.open()
            self.exo_mek.inventory.transfer_all(items.HEAVY_AUTO_TURRET)
            self._player.sleep(1)

            turrets_crafted = self._player.inventory.count(items.HEAVY_AUTO_TURRET)
            self.exo_mek.inventory.close()

            # deposit turrets and clear up the exo mek
            self.clear_up_exo_mek()

            total_time = round(time.time() - start)

            embed = self.create_embed(turrets_crafted, total_time)
            self._webhook.send_embed(embed)

        finally:
            self.transfer_dedi_wall()
            self.status = Status.WAITING_FOR_ITEMS
            self.ready = False

    def craft_electronics(self) -> None:
        """Checks if we need to queue another 1000 electronics to reach the
        total needed amount. Returns `False` if we dont, else `True`.

        This method is intended to be checked every 4 minutes by the main
        gacha bot function to either spawn and queue new electronics, or
        start crafting the turrets.
        """
        # spawn at station
        self.spawn()
        start = time.time()

        if self.electronics_crafted + 1000 <= self.electronics_to_craft:
            to_craft = 1000
        else:
            to_craft = self.electronics_to_craft - self.electronics_crafted
        print(f"Need to craft {to_craft} more electronics...")

        # get resources, craft 1000 electronics
        self.put_item_into_exo_mek(items.METAL_INGOT, to_craft)
        self.put_item_into_exo_mek(items.SILICA_PEARL, to_craft * 3)
        self.craft(items.ELECTRONICS, to_craft)

        # add the newly crafted electronics to the total, set new
        # last crafted timestamp
        self.electronics_crafted += to_craft
        self.last_crafted = time.time()

        if self.electronics_crafted >= self.electronics_to_craft:
            self.status = Status.AWAITING_CRAFT
        self._player.drop_all()

        time_taken = round(time.time() - start)

        embed = self.create_electronics_embed(time_taken)
        self._webhook.send_embed(embed)

    def transfer_dedi_wall(self) -> None:
        """Spawns at the grindingtransfer bed and transfers the materials
        left after crafting into the next dediwall, so that the ARB station
        can use the metal and it does not clog up the grinding dedis.

        Im sure theres a cleaner way to do this but it works.
        """
        bed = Bed("dedi_transfer")
        bed.spawn()
        self._tribelog.check_tribelogs()
        self._player.spawn_in()

        for i in range(2):
            # transfer pearls and paste
            self._player.turn_x_by(-90, delay=0.5)
            if i != 0:
                self._player.turn_y_by(50, delay=0.5)

            self.dedi.inventory.open()
            self.dedi.inventory.transfer_all()
            self.dedi.inventory.close()

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
        self.dedi.inventory.open()
        self.dedi.inventory.transfer_all()
        self.dedi.inventory.close()

        # take metal
        self._player.turn_y_by(50)
        self.dedi.inventory.open()
        self.dedi.inventory.transfer_all()
        self.dedi.inventory.close()

        for _ in range(2):
            self._player.turn_x_by(160, delay=0.5)

        self.dedi.deposit([items.METAL_INGOT], get_amount=False)
        self._player.turn_y_by(-50, delay=0.5)
        self.dedi.deposit([items.ELECTRONICS], get_amount=False)
