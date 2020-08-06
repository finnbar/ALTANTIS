# ALTANTIS
A possible bot for an upcoming Megagame run by Warwick Tabletop.

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
[ ] Control can drop items on the seafloor. (!bury for control)
[ ] Can shout at an engineer - control gives a question and answer, and then the engineer has to give a response. Ship takes more damage if the engineer gets it wrong.
[ ] Basic inventory management. (!give for control, !drop for players, !remove for control)
[ ] Basic resources.
[ ] !death, so you can die.

Important fixes:
[x] The world should not wrap.

Important non-gameplay features:
[x] Save bot state to disk with each game loop, as to avoid any issues.
[ ] Possibly deal with locking/unlocking of the main thread.
[ ] Add requirements.txt if necessary