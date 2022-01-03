# Santorini
Implementation of the game Santorini with CLI and object-oriented design patterns that allows for 2-player, random-play, and AI game modes.

Santorini is an abstract strategy game (think checkers/chess) designed by Dr. Gordan Hamilton. You can find a copy of the rulebook [here](http://files.roxley.com/Santorini-Rulebook-Web-2016.08.14.pdf).

This is a representation of the 5x5 game board and starting positions. The number in each space represents the level of the building. They all start unbuilt at level 0. A complete tower with a blue dome on top is shown as level 4. Next to the level number there is either a space, or the symbol for one of the 4 workers. The white player controls the A and B workers, while the blue player controls Y and Z.
```
+--+--+--+--+--+
|0 |0 |0 |0 |0 |
+--+--+--+--+--+
|0 |0Y|0 |0B|0 |
+--+--+--+--+--+
|0 |0 |0 |0 |0 |
+--+--+--+--+--+
|0 |0A|0 |0Z|0 |
+--+--+--+--+--+
|0 |0 |0 |0 |0 |
+--+--+--+--+--+
```

## Game modes
This program allows for multiple modes of play. The user can run the program in any of the possible game modes by specifying the player types via command line arguments. Examples of game modes include human v. human, human v. random/AI, or random/AI v. random/AI.

## Running the program
`python3 main.py argv[1] argv[2] argv[3] argv[4]`

argv[1]: white player type (human, AI, or random), default = human

argv[2]: blue player type (human, AI, or random), default = human

argv[3]: enable undo/redo (on or off), default = off

argv[4]: enable score display (on or off), default = off
