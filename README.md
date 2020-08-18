# ALTANTIS
A possible bot for an upcoming Megagame run by Warwick Tabletop.

## README
You'll need to do a few things to run this bot. In no particular order:

* Create a directory called `/puzzles` and fill it with puzzles (each a single file). Discord will upload these, so they must fit into Discord's upload limits. These will be presented to the players in alphabetical order, so you can present beginner puzzles in slot `00.png`, and so on. You should also have an `answers.json` file in there with a filename-answer mapping like so:

```json
{
    "puzzles/00.png": "a",
    "puzzles/01.pdf": "001"
}
```

You can also specify multiple answers for a puzzle - just replace the string with a list of strings.

## Feature list

Important features:
- [x] Can have submarines, which move.
- [x] Has a map with obstacles.
- [x] Can turn the sub off and on. (Allowing players to dock.)
- [x] Submarines can travel at multiple speeds.
- [x] Full power management. Can power systems, but has a power cap (which can be increased by control).
- [x] Pretty power management (!status will tell you about upcoming power changes.)
- [x] Can broadcast messages to all in range (via Comms system, which garbles longer-distance messages). Messages have a cooldown.
- [x] A channel per person, so that role-specific info can be broadcast (engineers only get puzzles, navigator only gets end-of-turn, scientists only gets scanners).
- [x] Can activate scanners, and inform players when they hover over things (level 1), are near things and other named subs (level 2), and further afield (level 3). Identify things via direction.
- [x] Control can drop items on the seafloor. (!bury for control)
- [x] Can shout at an engineer - control gives a question and answer, and then the engineer has to give a response. Ship takes more damage if the engineer gets it wrong.
- [x] Basic inventory management. (!give for control, !remove for control, no !drop as that's littering)
- [x] Trading between players (see Discord discussion for model).
- [x] The Crane.
- [x] Better map squares, including the ability for other types of square to have things in them, and "treasure chests". (Basically items that look like one thing but appear in the inventory as another.) Also update The Crane to work with these.
- [x] Weapons, oh my.
- [x] !death, so you can die.

Important non-gameplay features:
- [x] Save bot state to disk with each game loop, as to avoid any issues.
- [x] Deal with locking/unlocking of the main thread, if possible. (Could have issues if someone does something during game turn execution.) I don't believe this is actually necessary, as async is still single-threaded.
- [ ] Complete README.
- [x] Possible minor refactor of submarine, encapsulating the power system into its own thing (with damage/healing) and navigation, communications, inventory and puzzles into their own things.
- [x] Sort commands by functionality.
- [ ] Type annotations if possible, to make debugging significantly easier. Not sure how to structure.

Nice features:
- [ ] !explode, which explodes (x,y) with a range and amount of damage.
- [ ] Control alerts, which inform control about events such as: puzzle fails, treasure pickup, sub damage.
- [ ] NPCs/Structures, which can take damage etc. Also trading predefined trades. See my notes for this in #bot-impl. Probably needs its own state dictionary, except a list will suffice. (It's fine if this is a little slow, as it's called every few minutes.)
- [ ] See the list of keywords pinned in #spoilers and implement them. See if this can be done with class heirarchy stuff, but I am very slightly lost in that regard. (It will likely have to be on a keyword by keyword basis, tres sad.)
- [ ] Control commands run in team channels default to affecting that team.
- [ ] If the loop hasn't started, only control commands work. Do this by modifying our `perform` and `perform_async` functions.
- [ ] !drop? Might need to have undroppable items.
- [ ] Emoji map
- [ ] !save (determine if this is a safe command to add)
- [ ] !disable/!enable, which disables commands for teams. (as a control-available safety valve).

Fixes:
- [ ] Trading should cease at movement rather than tick.
- [ ] Remove "focus sash" idea.
- [ ] Fix issues when bot is deleted (causes A Lot).
- [ ] Add !sensor to recall previous sensor command.
- [ ] !mapall should also show treasure
- [ ] Sub "is online" should have tick emoji in !status
- [ ] Communicate power ERRORS better (e.g. "x has too much power")
- [ ] Tell _everyone_ when it's activated/deactivated.
- [ ] !investigate_square, which shouts about the attributes/treasure of a given square (CONTROL)
- [ ] Standardise commands to _team_ _strings_ _coordinates_.
- [ ] Crane with more power can go up/down faster.