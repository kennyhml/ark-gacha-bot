# ark-gacha-bot
Ark gacha bot lays the foundation for a factorio-like automation concept. 

It is entirely free to use, open-source and mostly based on my [ark-api](https://github.com/kennyhml/ark-api) package for ark automation.

Note that this description is *extremely* surface-scratching and does not at all reflect the amount of possible things that can be done based on this concept.


## Installation
- `git clone` the repository (or download the .zip)
- Run the `setup` batch file inside the downloaded directory
- Python 3.10 + is required, so is tesseract


## Concept
The basis of the ark *gacha* bot is the [gacha](https://ark.fandom.com/wiki/Gacha), see specifically the 'roles' section:
- A Snow Owl can be landed or walked to face a Gacha and the gacha will pick up the Snow Owl Pellet when the Snow Owl spits it out.
- Place resources within the Gacha's inventory and the Gacha will slowly consume them to produce [Gacha Crystals](https://ark.fandom.com/wiki/Gacha_Crystal_(Extinction))
- Via the selection wheel, survivors can select which of the available resources that their Gacha will produce
- Gachas will sometimes produce 'loot' of varying qualities, which will be denoted by quality-colored crystals (white, green, deep blue, purple, etc).
- Feeding the Gacha a Snow Owl Pellet will provide a temporary buff that increases crafting speed, increases the quality of loot produced, and increases the quantity of resources inside the Gacha Crystals (by double on average)
- The quality and type of the resource the Gacha eats will affect the Gacha Crystal's quantity of contained resources and quality of the loot. A very popular feeding method is therefore to feed them Plant Species Y Traps, which creates very high quality loot and lots of resources, since the game seems to think that Plant Y Traps are a "Structure" (which therefore has much higher "Gacha nutritional value" than basic resources

So, to sum it up:
- We need Plant YTrap and Snow Owl Pellets to feed the gacha
- We need Snow Owl Pellets to grow the Plant YTraps
- Gachas can pick up Snow Owls Pellets from nearby Snow Owls automatically

You might see that this is a self enclosing circle, which allows for a perfect automation concept.
Here is what one station for this automation may look like, and what a whole "tower" of these stations looks like:

<p float="left">
  <img src="https://user-images.githubusercontent.com/106347478/224790835-17d64719-bec5-4b8b-bae6-743a74698283.png" width="490" height="280" />
  <img src="https://user-images.githubusercontent.com/106347478/224791277-51998652-5184-4c4d-b917-bcba2f9d11a3.png" width="490" height="280" />
</p>

The way the tower works is basically just based on the ingame physics, the gacha crystals will roll down stairs / slopes.
We make use of this to "funnel" all the produced crystals into a collection point (as seen in the right image), like a marble run!

The collection point itself is just a big pit of accumulated crystals, that will be picked up in a set interval. The crystals will then be opened and the materials will be stored. Special items gained from the crystals will be stored and later processed into other things.
<p float="left">

  <img src="https://user-images.githubusercontent.com/106347478/224799043-454308d0-7ce6-4c0f-9077-b4e1e461ae3f.png" width="490" height="280" />
  <img src="https://user-images.githubusercontent.com/106347478/224799575-97fc068f-5161-4e95-aac7-3971c5e4e9c4.png" width="490" height="280" />
</p>

So, without going into much detail, the only thing left is to fast travel from bed to bed, collect ytraps from the crop plots, refill the fertilizer with the pellets inside the gacha if neccessary, then feed the gacha with the collected ytraps. Every 5-15 minutes we travel to the collection point and pick up / open the crystals.
