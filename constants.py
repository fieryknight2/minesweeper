"""Constants for the minesweeper game"""

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
MAX_WORLD_SIZE = 26
MAX_GUI_WORLD_SIZE = 250
MAX_REPEAT_WORLD_GEN = 100

FLAG = -1
HIDDEN = -2
BOMB = -3
BAD_FLAG = -4
NOTHING = 0

PRINT = 2
FAIL = -1
QUIT = -2

CHARACTER_UNICODE = {
    "bomb": "💣",
    "flag": "\u2691",
    "hidden": "\u2588",
    "bad_flag": "🚩",
}

CHARACTER_COLOR = {
    "bomb": "\033[31m",  # red
    "flag": "\033[32m",  # green
    "bad_flag": "\033[35m",  # pink
    "hidden": "\033[33m",  # yellow
    "reset": "\033[0m",  # reset
}

INGAME_HELP = \
    """Commands:
    help: Print this help message
    quit: Quit the game
    print: Reprint the current world
    
    How to Play:
        Enter a square by first placing a letter and then a number indicating
        a row and a column respectively (e.g. a1, b2, c3).

        To flag a square, enter the letter f first (e.g. fa1, fb2, fc3).
    
    Representation:
        - Bomb: B
        - Hidden: X
        - Flag: F
        - Wrong Flag: L
        
"""