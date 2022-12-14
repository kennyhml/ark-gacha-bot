import time
from itertools import cycle
from math import floor

import discord
import pydirectinput as input
from PIL import Image
from pytesseract import pytesseract as tes
from strenum import StrEnum

from ark.beds import Bed, BedMap
from ark.exceptions import (
    DedisNotDetermined,
    InvalidStationError,
    NoItemsAddedError,
    NoItemsDepositedError,
)
from ark.inventories import DedicatedStorage, Grinder, Inventory, Vault
from ark.items import *
from ark.player import Player
from ark.server import Server
from bot.ark_bot import ArkBot
from bot.unstucking import UnstuckHandler

# map costs for turrets
AUTO_TURRET_COST = {"Paste": 50, "Electronics": 70, "Ingot": 140, "poly": 20}
TURRET_COST = {"Paste": 200, "Electronics": 270, "Ingot": 540, "poly": 70}

# map common mistakes in the dedi OCR
DEDI_NUMBER_MAPPING = {"l": "1", "i": "1", "I": "1", "|": "1", "O": "0"}


class Stations(StrEnum):
    """An enum class representing the different stations to
    avoid typos."""

    GRINDER = "Grinder"
    EXO_MEK = "Exo Mek"
    VAULT = "Vault"
    CRYSTAL = "Crystal"
    HIDE = "Hide"
    INGOTS = "Ingot"
    ELECTRONICS = "Electronics"
    PEARLS = "Pearls"
    PASTE = "Paste"
    GEAR_VAULT = "Gear Vault"


class GrindBot(ArkBot):
    """Grinding station handler for the gachabot.
    Allows ling ling to spawn at a grind bed and turn grinded resources
    into structures.

    Parameters:
    ------------
    bed :class:`Bed`:
        The bed object to travel to to spawn at the grinding station


    Instance attributes:
    ------------------
    electronics_to_craft :class:`int`:
        The total number of electronics to craft for the current crafting
        session

    electronics_crafted :class:`int`:
        The total number of electronics crafted in the current crafting
        session

    session_cost :class:`dict`:
        The total crafting cost for the current crafting session

    session_turrets :class:`int`:
        The total amount of heavies to be crafted in the current crafting
        session

    last_crafted :class:`time.time()`:
        The timestamp of the last time 1k electronics have been queued

    station_mapping :class:`dict` [CONSTANT]:
        A map containing the turns for each station, to get around the station
    """

    grinder_avatar = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/f/fe/Industrial_Grinder.png/revision/latest/scale-to-width-down/228?cb=20160728174054"
    exomek_avatar = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/6/6d/Unassembled_Exo-Mek_%28Genesis_Part_2%29.png/revision/latest/scale-to-width-down/228?cb=20210603184626"
    electronics_avatar = "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/d/dd/Electronics.png/revision/latest/scale-to-width-down/228?cb=20150615100650"

    def __init__(self, bed: Bed, info_webhook: discord.Webhook, server: Server) -> None:
        super().__init__()
        self.player = Player()
        self.beds = BedMap()
        self.grinder = Grinder()
        self.vault = Vault()
        self.dedis = DedicatedStorage()
        self.exo_mek = Inventory("Exo Mek", "exo_mek")
        self.bed = bed
        self.server = server
        self.info_webhook = info_webhook
        self.current_station = "Gear Vault"
        self.electronics_to_craft = 0
        self.electronics_crafted = 0
        self.session_turrets = 0
        self.session_cost = {}
        self.last_crafted = None

        self.STATION_MAPPING = {
            "Grinder": (self.player.turn_x_by, -50),
            "Exo Mek": (self.player.turn_x_by, -110),
            "Vault": (self.player.turn_x_by, -95),
            "Crystal": (self.player.turn_x_by, -70),
            "Hide": (self.player.turn_y_by, 40),
            "Ingot": (self.player.turn_x_by, -60),
            "Electronics": (self.player.turn_y_by, -40),
            "Pearls": (self.player.turn_x_by, -60),
            "Paste": (self.player.turn_y_by, 40),
            "Gear Vault": [(self.player.turn_y_by, -40), (self.player.turn_x_by, -70)],
        }

    def resync_to_bed(self) -> None:
        """Resyncs to the bed to fix movements being messed up."""
        self.beds.lay_down()
        self.player.turn_90_degrees("left")
        self.current_station = Stations.GEAR_VAULT

    def session_reset(self) -> None:
        """Resets the session attributes. Intended to be called once
        the crafting has been finished and the exomek has been cleaned up."""
        self.electronics_to_craft = 0
        self.electronics_crafted = 0
        self.session_turrets = 0
        self.session_cost = {}
        self.last_crafted = None

    def find_quickest_way_to(self, target_station: Stations) -> list[str]:
        """Finds the quickest way to the passed target station, forwards
        and backwards possibilities are considered, the shortest is returned.

        Parameters:
        -----------
        target_station :class:`Station`:
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
            raise InvalidStationError(f"{target_station} is not a valid station!")

        # remove values from keys to get an proper iterable
        stations = list(self.STATION_MAPPING)

        # get the amount of station to go through if we move forwards
        # start counting flag, true once we reach our current station
        start_counting = False
        forward_path = []
        if target_station == self.current_station:
            return [], "stay"

        # make use of itertools cycle method to enable counting over
        # list end
        for station in cycle(stations):
            if station == self.current_station:
                start_counting = True
                continue

            if not start_counting:
                continue

            forward_path.append(station)
            if station == target_station:
                break

        # now count backwards
        start_counting = False
        backward_path = []
        for station in cycle(reversed(stations)):
            if station == self.current_station:
                start_counting = True

            if not start_counting:
                continue

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
        target_station :class:`Station`:
            The station to turn to
        """
        # get the quickest path and the direction
        path, direction = self.find_quickest_way_to(target_station)

        for station in path:
            self.current_station = station
            # if we are going backwards we are done once the station
            # is our target
            if direction == "backwards" and station == target_station:
                return

            # check if the station requires multiple turns
            # each station consists of the method (turn x, turn y)
            # whereas the argument consists of the amount to turn by
            if isinstance(self.STATION_MAPPING[station], list):
                for turn in self.STATION_MAPPING[station]:
                    method = turn[0]
                    args = turn[1] * (-1 if direction == "backwards" else 1)
                    method(args)
                    self.sleep(0.3)
                continue

            # only one turn
            method = self.STATION_MAPPING[station][0]
            args = self.STATION_MAPPING[station][1] * (
                -1 if direction == "backwards" else 1
            )
            method(args)
            self.sleep(0.3)

    def grind(self, grind: str | Item, take: list[Item | str]) -> None:
        """Turns to the grinder and grinds the item, then takes all requested
        items. Leaves the grinder in a closed state after finishing.

        Can be called with the grinder already being open or at any other
        station as long as the current station is CLOSED!

        Parameters:
        -----------
        grind :class:`str`| `Item`:
            The items to grind, either as Item object or the string
            representation

        take :class:`list`:
            A list of Items or string representations of the items to take
            after grinding
        """
        # open the grinder and transfer the items into it
        if not self.grinder.is_open():
            self.turn_to(Stations.GRINDER)
        self.grinder.open()
        self.player.inventory.transfer_all(self.grinder, grind)

        # turn the grinder on if its not already, grind all the items
        self.grinder.turn_on()
        self.sleep(1)
        self.grinder.grind_all()

        for item in take:
            self.grinder.take_all_items(item)
        self.grinder.close()

    def deposit(self, items: list[Item | str] | Item | str) -> None:
        """Deposits the given item into its respective dedi, assuming no
        current UI window is open.

        Parameters:
        ------------
        items :class:`list` | `str` | `Item`:
            The item(s) either as Item object(s) or string representation(s)
        """
        # turn it into a list if only 1 item was passed
        if not isinstance(items, list):
            items = [items]

        # deposit
        for item in items:
            if isinstance(item, Item):
                item = item.name
            self.sleep(0.3)
            self.turn_to(item)
            self.sleep(0.3)
            self.dedis.attempt_deposit(item, False)
            self.sleep(0.3)

    def take_item(self, item: Item) -> bool:
        """Takes the given item from the Gear Vault. Leaves the vault in
        a closed state.

        Can be called with the vault already open or at any other station
        as long as it is CLOSED.

        Parameters:
        -----------
        item :class:`Item`:
            The item to take, as Item object

        Returns:
        -----------
        `True` if items were available and taken from the Vault, else `False`
        """
        if not self.vault.is_open():
            self.turn_to(Stations.GEAR_VAULT)
            self.vault.open()

        # clear inventory, search for the target item
        self.player.inventory.drop_all()
        self.vault.search_for(item)
        self.sleep(0.5)

        # check if any items are within the vault
        if not self.vault.has_item(item):
            print(f"Vault has no {item.name}!")
            return False

        # take all (remember search filter is active), close vault
        self.vault.take_all()
        self.vault.close()
        return True

    def put_into_exo_mek(self, items: list[Item | str] | Item | str) -> None:
        """Puts all given items into exo mek. Leaves the exo mek in a
        closed state.

        Parameters:
        -----------
        item :class:`list` | `Item` | `str`:
            The item(s) to put into the exo mek as item object or string
            representation
        """
        print(f"Depositing {items} into exo mek...")
        # turn it into a list if only 1 item was passed
        if not isinstance(items, list):
            items = [items]

        if not self.exo_mek.is_open():
            self.turn_to(Stations.EXO_MEK)
            self.exo_mek.open()

        # deposit the items
        for item in items:
            self.player.inventory.transfer_all(self.exo_mek, item)
            self.sleep(0.5)
        self.exo_mek.close()

    def grind_armor(self) -> None:
        """Grind all the riot gear down, putting the polymer from the first grinding
        into the Exo Mek and dropping the rest. If a piece was not found, it will
        simply continue with the next one in the list.

        If any piece was found, after grinding all armor the crystal will be taken
        from the grinder and deposited into its dedi.
        """
        # pieces to grind
        armor = [
            riot_leggs,
            riot_chest,
            riot_gauntlets,
            riot_boots,
            miner_helmet,
            riot_helmet,
        ]

        # flag to determine if any items were grinded
        any_found = False
        for piece in armor:

            # empty grinder before we grind miner helmets
            # to avoid overcapping and wasting electronics
            if piece is miner_helmet:
                self.vault.close()
                self.empty_grinder()

            # continue with next piece if there isnt any
            # of the current one
            if not self.take_item(piece):
                continue

            # take electronics if miner helmet was grinded
            if piece is miner_helmet:
                self.grind(piece, ["poly", "Electronics"])
            else:
                self.grind(piece, ["poly", "Pearls"])

            # deposit the poly if its the first grinded piece
            if not any_found:
                self.put_into_exo_mek("poly")
            else:
                self.player.drop_all_items("poly")
            any_found = True

            # deposit the grinded items, turn back to gear vault
            self.deposit(["Electronics"] if piece is miner_helmet else "Pearls")
            self.turn_to(Stations.GEAR_VAULT)
        self.vault.close()

        if any_found:
            self.drop_script_from_grinder(crystal)

    def drop_script_from_grinder(self, item: Item) -> None:
        """Drop scripts the given item from the grinder and puts it
        into its respective dedi, returns to Gear Vault upon finishing.
        """
        # drop script the items out
        self.turn_to(Stations.GRINDER)
        self.player.do_drop_script(item, self.grinder)
        self.player.turn_y_by(-163)

        # deposit the items, turn back to gear vault
        self.deposit(item)
        self.turn_to(Stations.GEAR_VAULT)

    def grind_weapons(self) -> None:
        """Grinds all the weapons in the Gear Vault. If a weapon was not found,
        it will simply continue with the next one.

        Poly from all weapons will be dropped, paste will be taken and directly
        deposited into the dedi. After grinding all weapons, the ingots will be
        taken and deposited.
        """
        weapons = [fabricated_pistol, fabricated_sniper, assault_rifle, pumpgun]
        for weapon in weapons:
            print(f"Grinding {weapon.name}...")

            # continue with next item if no item was found
            if not self.take_item(weapon):
                continue

            # grind the weapons, take the relevant mats
            self.grind(grind=weapon, take=["poly", "Paste"])
            self.deposit("Paste")
            self.turn_to(Stations.GEAR_VAULT)
        self.player.drop_all_items("poly")

        # get the metal and deposit it into the dedi
        self.drop_script_from_grinder(metal_ingot)

    def find_all_dedi_positions(self, image: Image.Image) -> dict[str : Image.Image]:
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
        for dedi in ("Pearls", "Paste", "Ingot", "Electronics", "Crystal", "Hide"):
            region = self.find_dedi(dedi.lower(), image)
            if not region:
                print(f"Failed to find {dedi}")
                return

            # convert bc grab screen is retarded + extend boundaries
            region = int(region[0] - 80), int(region[1] + region[3] + 5), 350, 130

            # open it as PIL Image, crop out the calculated region of interest
            pil_img = Image.open(image)
            images[dedi] = pil_img.crop(
                (region[0], region[1], region[0] + region[2], region[1] + region[3])
            )
        return images

    def find_dedi(self, item: str, img: Image.Image) -> tuple:
        """Returns the position of the items dedi within the Image."""
        return self.locate_in_image(
            f"templates/{item}_dedi.png", img, confidence=0.75, grayscale=True
        )

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
            self.beds.travel_to(self.bed)
            self.player.await_spawned()
            self.sleep(1)
            self.player.turn_x_by(130)

        # looking up hard then down to make our hands move out of the
        # screen temporarily for better clarity
        self.player.look_up_hard()
        self.sleep(0.2)
        self.player.look_down_hard()
        self.player.disable_hud()
        self.sleep(0.5)
        self.player.turn_y_by(-160)
        self.sleep(0.3)

        # save the result, enable HUD and return the Image
        img = self.grab_screen(region=(0, 0, 1920, 1080), path="temp/dedis.png")
        self.sleep(0.5)
        self.player.disable_hud()
        return img

    def walk_back_little(self) -> None:
        """Crouches and walks back a tiny bit, attempting to getting a better
        view on the dedis."""
        self.player.crouch()
        self.sleep(0.1)
        input.press("s")
        self.player.crouch()
        self.sleep(0.5)

    def get_dedi_materials(self) -> dict:
        """Tries to get the dedi materials up to 10 times. Will return a dict
        of the material and its amount on the first successful attempt.

        Raises `DediNotFoundError` after 10 unsuccessful attempts.
        """
        for i in range(10):
            amounts = {}
            # get all dedis regions
            dedis = self.find_all_dedi_positions(self.get_dedi_screenshot(spawn=i < 1))
            # a dedi could not be determined, try to move further back.
            if not dedis:
                self.walk_back_little()
                continue
            try:
                # got all regions, denoise and OCR the amount, using psm 6 for the moment
                for name in dedis:
                    img = self.denoise_text(dedis[name], (55, 228, 227), 22)
                    tes_config = (
                        "-c tessedit_char_whitelist=0123456789liI|O --psm 6 -l eng"
                    )

                    raw_result = tes.image_to_string(img, config=tes_config).strip()
                    # replace common tesseract fuckups
                    for c in DEDI_NUMBER_MAPPING:
                        raw_result = raw_result.replace(c, DEDI_NUMBER_MAPPING[c])
                    final_result = int(raw_result)

                    # validate that the result is within a logical range
                    if not self.amount_valid(name, final_result):
                        raise ValueError(
                            f"Invalid amount of resources detected for {name}: {final_result}"
                        )
                    amounts[name] = int(final_result)

            except (TypeError, ValueError) as e:
                print(f"Failed to get amount of {name}!\n{e}")
                continue

            # add material and its amount to our dict
            self.post_available_materials(amounts)
            return amounts
        raise DedisNotDetermined(
            "Failed to determine the amounts of resources within one or more dedis!\n"
            "This could have been caused by poor tesseract performance, bad dedi placement "
            "or simply too much materials within the dedis. Please check on the dedis!"
        )

    def amount_valid(self, material, amount) -> bool:
        expected = {
            "Pearls": (6000, 60000),
            "Paste": (7000, 160000),
            "Electronics": (800, 10000),
            "Ingot": (9000, 40000),
        }
        # we dont care about crystal or hide
        if material not in expected:
            return True

        # ensure the OCRd amount is within a f
        expected_amount = expected[material]
        return expected_amount[1] >= amount >= expected_amount[0] - 300

    def post_available_materials(self, owned_mats: dict[str:int]) -> None:
        formatted = {}
        desired_order = ["Ingot", "Paste", "Electronics", "Pearls", "Hide", "Crystal"]

        for resource in owned_mats:
            formatted[resource] = f"{owned_mats[resource]:_}x".replace("_", " ")
        formatted = {k: formatted[k] for k in desired_order}

        embed = discord.Embed(
            type="rich",
            title="Finished grinding!",
            description="Available materials:",
            color=0x03DD74,
        )

        for resource in formatted:
            embed.add_field(name=f"{resource}:ㅤ", value=formatted[resource])

        embed.set_thumbnail(url=self.grinder_avatar)
        embed.set_footer(text="Ling Ling on top!")

        self.info_webhook.send(
            embed=embed,
            username="Ling Ling",
        )

    def post_dedis_not_determined(self) -> None:
        """Posts an embed informing that the dedis could not be determined and
        that an average amount will be assumed."""
        embed = discord.Embed(
            type="rich",
            title="Finished grinding, but failed to determine the resources!",
            description="Something went wrong trying to determine the resources",
            color=0x03DD74,
        )
        file = discord.File(
            self.grab_screen((0, 0, 1920, 1080), "temp/unknown_error.png"),
            filename="image.png",
        )
        embed.set_image(url="attachment://image.png"),

        embed.add_field(
            name=f"Ling ling will assume a 13x Heavy Turret craft!", value="\u200b"
        )

        embed.set_thumbnail(url=self.grinder_avatar)
        embed.set_footer(text="Ling Ling on top!")

        self.info_webhook.send(
            embed=embed,
            file=file,
            username="Ling Ling",
        )

    def get_crafting_method(self, owned_items: dict[str:int]):
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
        cost = {"Paste": 0, "Ingot": 0, "Electronics": 0}
        # find how many turrets we can craft right away
        lowest_1 = min(
            owned_items[material] / TURRET_COST[material] for material in cost
        )

        # set the inital cost
        phase_1 = {
            "Paste": int(TURRET_COST["Paste"] * lowest_1),
            "Ingot": int(TURRET_COST["Ingot"] * lowest_1),
            "Electronics": int(TURRET_COST["Electronics"] * lowest_1),
        }

        # add the initial cost, remove it from the owned mats
        for material in phase_1:
            cost[material] += phase_1[material]
            owned_items[material] -= phase_1[material]

        # set new turret cost using pearls and more ingots instead, set
        # pearl value
        raw_turret_cost = {"Paste": 200, "Pearls": 270 * 3, "Ingot": 540 + 270}
        cost["Pearls"] = 0

        # once again get the amount of craftable turrets, create phase 2 cost
        lowest_2 = min(
            owned_items[material] / raw_turret_cost[material]
            for material in raw_turret_cost
        )
        phase_2 = {
            "Paste": int(raw_turret_cost["Paste"] * lowest_2),
            "Ingot": int(raw_turret_cost["Ingot"] * lowest_2),
            "Pearls": int(raw_turret_cost["Pearls"] * lowest_2),
        }

        # add each material to the total cost, electronics to craft is now
        # pearls / 3
        for material in phase_2:
            cost[material] += phase_2[material]

        # flatten some of the needed amounts to get the exact amounts required
        cost["Paste"] -= cost["Paste"] % 200
        cost["Pearls"] -= cost["Pearls"] % 3

        # calculate the total electronics we will end up with to discard
        # surplus
        total_elec = cost["Pearls"] / 3 + cost["Electronics"]
        crafting_too_much = total_elec % 270
        cost["Pearls"] -= round(crafting_too_much * 3)
        cost["Ingot"] -= round(crafting_too_much)

        # dicard surplus metal, EXCLUDING the cost for electronics
        cost["Ingot"] -= round(cost["Ingot"] - (cost["Pearls"] / 3)) % 540

        # set session costs
        self.electronics_to_craft = round(cost["Pearls"] / 3)
        self.session_turrets = floor(lowest_1 + lowest_2)
        self.session_cost = cost

        self.post_crafting_plan()
        print(
            f"Need to craft {self.electronics_to_craft} electronics for {self.session_turrets} Turrets"
        )

    def post_crafting_plan(self) -> None:
        """Sends an embed to the info webhook informing about the crafting
        plan that has been calculated for the ongoing session. Takes its data
        from the session class attributes."""

        # reformat the amounts to make it look nicer
        formatted = {}
        desired_order = ["Ingot", "Paste", "Electronics", "Pearls"]
        for resource in self.session_cost:
            formatted[resource] = f"{self.session_cost[resource]:_}x".replace("_", " ")
        formatted = {k: formatted[k] for k in desired_order}

        # create embed, black sidebar
        embed = discord.Embed(
            type="rich",
            title="Calculated crafting!",
            description="Required materials:",
            color=0x000000,
        )

        # add each resource to the embed, heavies and electronics on the
        # righthand side
        for resource in formatted:
            embed.add_field(name=f"{resource}:ㅤ", value=formatted[resource])
            if resource == "Paste":
                embed.add_field(
                    name="Expected Result:",
                    value=f"{self.session_turrets} Heavy Turrets",
                )
        embed.add_field(
            name="Electronics to craft:", value=f"{self.electronics_to_craft}x"
        )

        # set exo mek image
        embed.set_thumbnail(url=self.exomek_avatar)
        embed.set_footer(text="Ling Ling on top!")

        # send the embed
        self.info_webhook.send(
            embed=embed,
            username="Ling Ling",
        )

    def post_electronics_crafting(self, time_taken: time.time) -> None:
        """Sends an embed to the info webhook informing that electronics
        have been queued. Contains the time taken to queue the electronics
        and how many have been crafted/how many to craft are left.

        Parameters:
        ------------
        time_taken :class:`time`:
            The timestamp when the queue function was started
        """
        # create embed, yellowsidebar
        embed = discord.Embed(
            type="rich",
            title="Queued electronics!",
            color=0xFCFC2C,
        )

        # add contents
        embed.add_field(
            name=f"Time taken:",
            value=f"{round(time.time() - time_taken)} seconds",
        )
        embed.add_field(
            name="Crafted:",
            value=f"{self.electronics_crafted}/{self.electronics_to_craft}",
        )

        # set electronics picture
        embed.set_thumbnail(url=self.electronics_avatar)
        embed.set_footer(text="Ling Ling on top!")

        # send to the webhook as Ling Ling
        self.info_webhook.send(
            embed=embed,
            username="Ling Ling",
        )

    def post_final_result(self, result: int, start_time: time.time) -> None:

        time_taken = round(time.time() - start_time)
        embed = discord.Embed(
            type="rich",
            title="Finished crafting!",
            color=0x133DE7,
        )
        embed.add_field(name=f"Time taken:ㅤ", value=f"{time_taken} seconds")
        embed.add_field(name="Heavies crafted:", value=result)
        embed.set_thumbnail(url=self.exomek_avatar)
        embed.set_footer(text="Ling Ling on top!")

        self.info_webhook.send(
            embed=embed,
            username="Ling Ling",
        )

    def empty_grinder(self, turn_off: bool = False) -> None:
        """Empties the grinder by taking hide and 'popcorning' the rest.
        Leaves the grinder in a closed state. Leaves the grinder on by default,
        but will turn it off before closing if requested.
        """
        # get all the hide and deposit it
        self.turn_to(Stations.GRINDER)
        self.grinder.open()
        self.grinder.take_all_items("Hide")
        self.grinder.close()
        self.deposit("Hide")

        # drop all on the remaining items
        self.turn_to(Stations.GRINDER)
        self.grinder.open()
        for _ in range(3):
            self.grinder.take_all()
            self.player.inventory.drop_all()

        # turn off grinder if requestes and close it
        if turn_off:
            self.grinder.turn_off()
        self.grinder.close()

    def put_resource_into_exo_mek(self, resource, amount, stacksize) -> None:
        """Takes the given resource from its dedi and puts the given
        amount into the exo mek."""
        self.turn_to(resource)
        self.dedis.open()
        self.dedis.take_all()
        self.dedis.close()
        self.sleep(1)

        # transfer the amount into the exo mek
        self.turn_to(Stations.EXO_MEK)
        self.sleep(1)
        self.exo_mek.open()
        if self.exo_mek.has_item(gacha_crystal):
            self.move_to(1287, 289)
            self.press("o")
            self.sleep(1)
            self.exo_mek.open()

        self.player.inventory.transfer_amount(resource, amount, stacksize)
        self.exo_mek.close()
        self.sleep(1)

        # put remaining resources back into dedi
        self.turn_to(resource)
        self.sleep(1)
        self.dedis.attempt_deposit(resource, False)

    def craft(self, item, amount) -> None:
        """Turns to the exo mek and crafts the given amount of the given item"""
        if not self.exo_mek.is_open():
            self.turn_to(Stations.EXO_MEK)
            self.exo_mek.open()

        self.exo_mek.open_craft()
        self.exo_mek.craft(item, amount)
        self.exo_mek.close_craft()
        self.exo_mek.close()

    def need_to_craft_electronics(self) -> bool:
        """Checks if we need to queue another 1000 electronics to reach the
        total needed amount. Returns `False` if we dont, else `True`.

        This method is intended to be checked every 4 minutes by the main
        gacha bot function to either spawn and queue new electronics, or
        start crafting the turrets.
        """
        if self.electronics_crafted >= self.electronics_to_craft:
            print("Crafted enough electronics! Now crafting turrets...")
            return False

        # spawn at station
        start = time.time()
        self.spawn()

        if self.electronics_crafted + 1000 <= self.electronics_to_craft:
            to_craft = 1000
        else:
            to_craft = self.electronics_to_craft - self.electronics_crafted
        print(f"Need to craft {to_craft} more electronics...")

        # get resources, craft 1000 electronics
        self.put_resource_into_exo_mek("Ingot", to_craft, 300)
        self.put_resource_into_exo_mek("Pearls", to_craft * 3, 100)
        self.craft("Electronics", to_craft)

        # add the newly crafted electronics to the total, set new
        # last crafted timestamp
        self.electronics_crafted += to_craft
        self.last_crafted = time.time()
        self.post_electronics_crafting(start)
        self.player.drop_all()
        return True

    def transfer_turret_resources(self) -> None:
        """Transfers all resources needed for turrets into the exo mek.

        Handles:
        ----------
        `NoItemsDepositedError` up to 3 times when failing to deposit the
        remaining items by resyncing to the bed and trying again.
        """
        for resource in ["Paste", "Electronics", "Ingot"]:
            while True:
                attempt = 0
                try:
                    if resource == "Ingot":
                        self.put_resource_into_exo_mek(
                            resource, self.session_cost[resource], 300
                        )
                    else:
                        self.put_resource_into_exo_mek(
                            resource, self.session_cost[resource], 100
                        )
                    break
                except NoItemsDepositedError:
                    attempt += 1
                    unstucking = UnstuckHandler(self.server)
                    if not unstucking._ingame_menu.check_reponding() or attempt > 3:
                        raise
                    self.resync_to_bed()

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
            self.craft("Auto Turret", self.session_turrets)
            self.craft("Heavy Auto Turret", self.session_turrets + 3)

            # take out the turrets
            self.exo_mek.open()
            self.exo_mek.take_all_items("Heavy Auto Turret")
            self.sleep(1)
            turrets_crafted = self.player.inventory.count_item(heavy_auto_turret)
            self.exo_mek.close()

            # deposit turrets and clear up the exo mek
            turrets_crafted = self.clear_up_exo_mek()
            self.post_final_result(turrets_crafted, start)
        finally:
            self.session_reset()

    def clear_up_exo_mek(self) -> int:
        """Clears the exo mek after a crafting session."""
        self.turn_to(Stations.VAULT)
        self.vault.open()
        self.player.inventory.transfer_all(self.vault, "Turret")
        self.vault.close()
        self.sleep(1)

        try:
            # clean up the remaining mats from exo mek
            self.turn_to(Stations.EXO_MEK)
            self.sleep(1)
            self.player.do_drop_script(metal_ingot, self.exo_mek, 1)
            self.player.turn_y_by(-163)
            self.deposit(metal_ingot)

        except NoItemsAddedError:
            print("Failed to take metal from the exo mek!")
            self.exo_mek.close()
            self.player.crouch()

        # get the non heavy mats, drop all on the rest (poly)
        self.turn_to(Stations.EXO_MEK)
        self.sleep(1)
        self.exo_mek.open()
        for item in ["Pearls", "Paste", "Electronics"]:
            self.exo_mek.take_all_items(item)
        self.exo_mek.drop_all()
        self.exo_mek.close()
        self.sleep(0.5)

        # deposit the lightweight mats
        for item in ["Pearls", "Paste", "Electronics"]:
            self.deposit(item)

    def spawn(self) -> None:
        self.beds.travel_to(self.bed)
        self.player.await_spawned()
        self.current_station = Stations.GEAR_VAULT
        self.sleep(1)

    def run(self):
        print("A grinding session has been created!")
        self.spawn()

        # get all resources from grinding, turn off grinder when finished
        self.grind_all_gear()
        self.empty_grinder(turn_off=True)

        try:
            available_mats = self.get_dedi_materials()

        except DedisNotDetermined:
            self.post_dedis_not_determined()
            available_mats = {
                "Pearls": 5211,
                "Paste": 2600,
                "Ingot": 8757,
                "Electronics": 1773,
                "Crystal": 10000,
                "Hide": 20000,
            }

        self.get_crafting_method(available_mats)
        # craft the first batch of electronics, should we for whatever reason
        # not have to craft any, craft turrets straight away to avoid breaking
        if not self.need_to_craft_electronics():
            self.craft_turrets()
            return True

    def grind_all_gear(self) -> None:
        """Grinds armor, then gear"""
        self.grind_armor()
        self.grind_weapons()
