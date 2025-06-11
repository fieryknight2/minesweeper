# Minesweeper

I created this program to stretch my understanding of Python and 
to actually finish a project I have created. I started this project 
in 2023 for fun, and I started working on it again in 2024 with 
the help of AI to increase my knowledge of Python and practical coding. As of 2025,
I returned to this project to update it once again.
This game was originally designed to be a simple console-based, minesweeper 
implementation, but I decided to add a GUI and Unicode support for fun.

## Installation

Clone the repository. You will need Python 3 to run the console game.
If you wish to run the GUI game, you will need to install PyQt, you can do
this by running `python -m pip install pyqt6 pyqt6-sip`

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

## License

This project is licensed under the MIT License—see the [LICENSE](LICENSE.md) file for details
