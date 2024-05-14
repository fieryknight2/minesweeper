# Minesweeper

I created this program to stretch my understanding of Python and 
to actually finish a project I have created. I started this project 
in 2023 for fun, and I have recently started working on it again with 
the help of AI to increase my knowledge of Python and practical coding. 
This game was originally designed to be a simple console based, minesweeper 
implementation, but I decided to add a GUI and unicode support for fun.

## Installation

Clone the repository, the only dependency is Python 3

## Usage and Controls

### Console Version

Run `python3 main.py` to start the game.

The game uses a grid of squares, each designated by a letter and a number.
To designate a square, use the algebraic notation, e.g. `a1` for the first square in the first row.
To flag a square, use the flag character `f`. For example, `fa1` would flag the first square in the first row.
To un-flag a square, use the flag character `f` again.

### GUI Version

Run `python3 main.py --use-gui` to start the game.

Start the game by clicking any tile. The timer will then start ticking. To flag a tile, click
a tile with the right mouse button. To quit the game, click the Quit button.

### Command line arguments

`-h, --help`: Prints the help message

`-v, --version`: Prints the version

`-s, --seed`: Sets the random seed

`-m, --mine-count`: Sets the number of mines

`-w, --world-size`: Sets the world size

`--no-white-space`: Do not print white space between squares

`--use-unicode`: Use unicode characters

`--use-color`: Use color characters

`--use-gui`: Use the GUI

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details
