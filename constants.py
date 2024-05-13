"""Constants for the minesweeper game"""

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
MAX_WORLD_SIZE = 26
MAX_REPEAT_WORLD_GEN = 100

FLAG = -1
HIDDEN = -2
BOMB = -3
NOTHING = 0

FAIL = -1
QUIT = -2

CHARACTER_UNICODE = {
    "bomb": "💣",
    "flag": "\u2691",
    "hidden": "\u2588",
}

CHARACTER_COLOR = {
    "bomb": "\033[31m",
    "flag": "\033[32m",
    "hidden": "\033[33m",
    "reset": "\033[0m",
}
