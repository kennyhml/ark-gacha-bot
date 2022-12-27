# ark-gacha-bot
'Ark gacha bot' is the base for ark automation with insane potential.

The basic concept is feeding Gachas (Dinosaurs that will drop crystals when you feed them) with Y-Traps (grown in crop plots, basically an infinite resource)
and funnelling the produced crystals into a collection point where they are picked up and opened, which gives a wide variety of resources that can
be used for alot of different things.

# Challenges
The biggest challenge in this project was definitely task management, the bot needs to accuretly keep track of the stations and what task it should do next.
For more complex I chose to use enums to represent the current Status and choose the next step depending on it. Another challenge was OCR'ing various things
correctly, e.g in the grinding station the bot OCRs the amounts of resources available and then computes how we can craft items.

# Design choices
I decided to split the structure into 2 directories, 'ark' and 'bot' where ark essentially contains all the classes representing in-game objects such as
Dinos, Inventories, Structures, the Player..., whereas the bot folder contains everything related to actually creating automation (the different types
of botting stations, the main station handler, unstucking, settings...)

I learned how to use Protocol and abstract base classes, I chose to make 'Station' an ABC so other contributors could create their own botting station 
and easily implement it by just following what the 'Station' ABC provides. It was also my first time using a strict mypy type hinting and I definitely 
grew to like strong type hinting.


# I normally do not encourage any sort of botting
But this is something different, the developers of ark have been asked multiple times whether they will enforce gacha bots, and they have said that they do not
intend to do so. It also does not give you an unfair advantage against other players.


