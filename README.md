# Minesweeper

A simple console based minesweeper clone.

## Installation

Clone the repository, there are no dependencies.

## Usage and Controls

Run `python main.py` to start the game.

The game uses a grid of squares, each designated by a letter and a number.
To designate a square, use the algebraic notation, e.g. `a1` for the first square in the first row.
To flag a square, use the flag character `f`. For example, `fa1` would flag the first square in the first row.
To un-flag a square, use the flag character `f` again.

### Command line arguments

`-h, --help`: Prints the help message

`-v, --version`: Prints the version

`-s, --seed`: Sets the random seed

`-m, --mine-count`: Sets the number of mines

`-w, --world-size`: Sets the world size

`--no-white-space`: Do not print white space between squares

Experimental options:

`--use-unicode`: Use unicode characters

`--use-color`: Use color characters

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details