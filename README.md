# ALTANTIS
A possible bot for an upcoming Megagame run by Warwick Tabletop.

## README
You'll need to do a few things to run this bot. In no particular order:

* Create a directory called `/puzzles` and fill it with puzzles (each a single file). Discord will upload these, so they must fit into Discord's upload limits. These will be presented to the players in alphabetical order, so you can present beginner puzzles in slot `00.png`, and so on. You should also have an `answers.json` file in there with a filename-answer mapping like so:

```json
{
    "00.png": "a",
    "01.pdf": "001"
}
```

## Feature list

Important features:
[x] Can have submarines, which move.
[x] Has a map with obstacles.
[x] Can turn the sub off and on. (Allowing players to dock.)
[x] Submarines can travel at multiple speeds.
[x] Full power management. Can power systems, but has a power cap (which can be increased by control).
[x] Pretty power management (!status will tell you about upcoming power changes.)
[x] Can broadcast messages to all in range (via Comms system, which garbles longer-distance messages). Messages have a cooldown.
[x] A channel per person, so that role-specific info can be broadcast (engineers only get puzzles, navigator only gets end-of-turn, scientists only gets scanners).
[x] Can activate scanners, and inform players when they hover over things (level 1), are near things and other named subs (level 2), and further afield (level 3). Identify things via direction.
[x] Control can drop items on the seafloor. (!bury for control)
[x] Can shout at an engineer - control gives a question and answer, and then the engineer has to give a response. Ship takes more damage if the engineer gets it wrong.
[ ] Basic inventory management. (!give for control, !drop for players, !remove for control)
[ ] Basic resources.
[ ] !death, so you can die.

Important fixes:
[x] The world should not wrap.

Important non-gameplay features:
[x] Save bot state to disk with each game loop, as to avoid any issues.
[ ] Possibly deal with locking/unlocking of the main thread.
[ ] Complete README.