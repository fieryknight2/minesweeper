"""Simple functions for simplification of main.py"""
import sys
from constants import *

_IS_FLAG_FAIL = -3


# Functions
def _alph_to_coord(letter: str) -> int:
    """Converts a letter to its corresponding number a-1, b-2, etc."""
    if isinstance(letter, str) and letter in ALPHABET:
        return int(ord(letter) - ord("a"))
    print("Internal Error! Bad string given!")
    sys.exit(1)


def print_world_item(item: int, method: str) -> None:
    """Prints an element of the world"""
    if item == -2:  # -2 is not visible
        if method == "use_unicode":
            print(CHARACTER_UNICODE["hidden"], end=" ")
        elif method == "use_color":
            print(CHARACTER_COLOR["hidden"] + "X" + CHARACTER_COLOR["reset"], end=" ")
        else:
            print("X", end=" ")
    elif item == -1:  # -1 is flagged
        if method == "use_unicode":
            print(CHARACTER_UNICODE["flag"], end=" ")
        elif method == "use_color":
            print(CHARACTER_COLOR["flag"] + "F" + CHARACTER_COLOR["reset"], end=" ")
        else:
            print("F", end=" ")
    elif item == -3:
        if method == "use_unicode":
            print(CHARACTER_UNICODE["bomb"], end="")
        elif method == "use_color":
            print(CHARACTER_COLOR["bomb"] + "B" + CHARACTER_COLOR["reset"], end=" ")
        else:
            print("B", end=" ")
    elif item == 0:  # 0  means nothing
        print(" ", end=" ")
    else:  # Remaining items are numbers to print
        print(str(item), end=" ")


def _check_flagging(square: str, world_size: int, world_created: bool) -> int | tuple[str, int, int]:
    """Checks if a square is flagged"""
    if (square[0] in "Ff") and (len(square) == 3 or len(square) == 4) \
            and (not square[1].isnumeric()) and world_created:  # flag a square
        if not square[1] in ALPHABET:
            return _IS_FLAG_FAIL
        if _alph_to_coord(square[1]) > world_size or _alph_to_coord(square[0]) < 0:
            return _IS_FLAG_FAIL
        c = _alph_to_coord(square[1])

        if not square[2:].isnumeric():
            return _IS_FLAG_FAIL
        if int(square[2:]) > world_size or int(square[2:]) < 1:
            return _IS_FLAG_FAIL
        r = int(square[2:])

        return "f", r - 1, c


def validate(square: str, world_created: bool, world_size: int) -> \
            tuple[int, int] | tuple[str, int, int] | int:
    """Validates input from user into a location on the grid"""
    if len(square) < 2:
        return FAIL

    if square == "quit":
        return QUIT

    flag = _check_flagging(square, world_size, world_created)
    if flag == _IS_FLAG_FAIL:
        return FAIL

    if not world_created and square[0] in "Ff" and not square[1].isnumeric():
        return FAIL

    if len(square) != 2 and len(square) != 3:
        return FAIL

    # check for letter
    if not square[0] in ALPHABET:
        return FAIL
    if _alph_to_coord(square[0]) > world_size or _alph_to_coord(square[0]) < 0:
        return FAIL
    c = _alph_to_coord(square[0])

    # check for number
    if not square[1:].isnumeric():
        return FAIL
    if int(square[1:]) > world_size or int(square[1]) < 1:
        return FAIL
    r = int(square[1:])

    return r - 1, c


if __name__ == '__main__':
    print("functions.py doesn't contain any main functionality")
    exit(1)
