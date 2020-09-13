# ALTANTIS
Man, fuck Python.

## A Precautionary Opening
This is a bot for the Warwick Tabletop Games and Roleplaying Society's "The Depths" Megagame - a game about people in submarines and the bad things that happen with them. We ran this game on the 13th September 2020 with forty people using the bot (ten submarines, a news team and a control team). I must be honest here and open with the fact that it dramatically crashed multiple times during the first two hours of the event - most of the bugs arising seem to have been fixed, but some have not. Like most open source software, this is provided with no warranty. The word "no" is doing a lot of work in that sentence, needless to say.

(I'd also like to note while I will always readily admit that I'm a bad programmer, Python was against me here - I essentially applied as much verification as I could to the code, and even then bugs that would be picked up by type-safe languages were just missed altogether. I'm not looking for recommendations of ways to make Python "better", as I genuinely think it was the wrong tool for this job.)

I would post the rest of the games resources along with this, however we're hoping to take the issues found during its first running and make the game even better. We've had an amazing discussion with the players of the game and found a variety of ways to improve it, and I will be working on a new implementation written in a safer language in order to live up to the improvements we've discussed. As a result, this version of the code is final and likely won't ever be touched again. I'm incredibly thankful to control and all of the players of the megagame for their thoughts, comments and support - especially during the incredibly low point of the first two hours of the running of this game, or rather, the crashing of this game. I really hope the new version can make up for the first version's issues, and we can make an amazing game! This repo will not hold any of this new implementation however - keep an eye out for that in a different repo!

With that, let's get onto the README for this particular bot.

## README

You'll need to do a few things to run this bot. In no particular order:

* Install `requirements.txt`. `pip3 -r requirements.txt` is your friend.
* Create a directory called `/puzzles` and fill it with puzzles (each a single file). Discord will upload these, so they must fit into Discord's upload limits. These will be presented to the players in the order provided in the answers file, so you can present beginner puzzles earlier on. You should also have an `answers.json` file in there with a filename-answer mapping like so:

```json
{
    "puzzles/00.png": ["a"],
    "puzzles/01.pdf": ["001", "--1"]
}
```

* Create a directory `/weather` that contains `txt` files of ASCII maps of the world made up of 's' (stormy), 'c' (calm), 'r' (rough) and '.' characters. These can be used to apply weather to all squares simultaneously.
* Create a `.env` file with the following:
    * A Discord API token (`DISCORD_TOKEN`). At the time of writing, the bot needs the permissions given by integer `268561488`. If you're lazy you can just give it Administrator, but I expect anyone with an inkling of security knowledge may not be entirely happy with that idea.
    * A website for it to request maps from. Feel free to contact me about this and I'll try my best to set you up. (This should be a `MAP_TOKEN` and a `MAP_DOMAIN`.)
* Look through the const files (`/ALTANTIS/utils/consts.py` and `/ALTANTIS/world/consts.py`) and add your own constants. Most of these are self-explanatory.

## What's it do?

The ALTANTIS bot deals with the organisation of three entities - the *state*, which contains submarines, *npcs* which contains non-Submarine objects, and *world* which contains a map. These work together to allow you to have a map filled with sea creatures, treasure that can be picked up, and submarines. These submarines are what the players navigate the world with, and those are what you really need to know about.

### Submarines
The actions of submarines can be found in `docs/ALTANTIS and You....pdf`, a helpful document provided to the players. To give a summary of the sort of things submarines can do:

* They exist on the world and move around it based on their engine power.
* They have an FTL-based power system, where you can shift power around your subsystems and take damage to your main reactor, reducing its output. Instead of FTL's power and health systems being different, we merge the two together and have your reactor output be your health.
* They can pick up items from the seafloor using cranes.
* They can trade items between subs in the same square, using an `!offer` command.
* They can shoot at other entities (NPCs and other submarines).
* They can send reports back to control about their actions.
* They can broadcast messages to other submarines.
* They can scan their surroundings and report back on the directions and locations of other entities (including buried treasure).
* They can become worn and rusty and require fixing using puzzles.
* They can `!interact` with NPCs, including taking photos of them.
* They can be upgraded both in terms of their power and through additional keywords that allow for more interesting upgrades (`ALTANTIS/subs/subsystems/upgrades.py`).
* They can dock at docking stations, assigning roles to players and allowing them into secret Discord channels.

These all operate on a "tick" system - you schedule your actions and then they resolve each minute.

### NPCs
There is an extensible NPC system. The base NPC class allows you to define entities which act each turn (`npc_tick`), can attack, move towards subs or randomly, and be photographable. There's a bunch of additional functionality which can be seen in the `ALTANTIS/npcs` folder, including the class itself (`npcs.py`) and many examples (`templates.py`).

### Map
The map system allows you to introduce *attributes* to squares in it, that allow it to do different things. There are attributes for weather (to make sub motion faster/slower), whether it is an obstacle, whether it is a ruin and so on. Unless you want your game to take weeks, I would recommend using a small map size. `ALTANTIS/world` has various functions for these.

## Anyway
I'm writing this README on the evening after the game, and I think I don't need to write any more. Also I'm tired. So, thank you for reading, and if you played, thank you for playing. And with that, I don't need to touch this cursed codebase any more.