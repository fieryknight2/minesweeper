"""Simple functions for simplification of main.py"""
import sys
from typing import Callable

from constants import ALPHABET, HIDDEN, FLAG, CHARACTER_UNICODE, CHARACTER_COLOR, PRINT
from constants import MAX_REPEAT_WORLD_GEN, FAIL, QUIT, INGAME_HELP

import random

_IS_FLAG_FAIL = -3


# Functions
def _alph_to_coord(letter: str) -> int:
    """Converts a letter to its corresponding number a-1, b-2, etc."""
    if isinstance(letter, str) and letter in ALPHABET:
        return int(ord(letter) - ord("a"))
    print("Internal Error! Bad string given!")
    sys.exit(1)


def _print_char(char_type: str, method: str, character: str) -> None:
    """Prints a character"""
    if method == "use_unicode":
        print(CHARACTER_UNICODE[char_type], end=" ")
    elif method == "use_color":
        print(CHARACTER_COLOR[char_type] + character + CHARACTER_COLOR["reset"], end=" ")
    else:
        print(character, end=" ")


def print_world_item(item: int, method: str) -> None:
    """Prints an element of the world"""
    if item == -2:  # -2 is not visible
        _print_char("hidden", method, "X")
    elif item == -1:  # -1 is flagged
        _print_char("flag", method, "F")
    elif item == -3:
        _print_char("bomb", method, "B")
    elif item == 0:  # 0  means nothing
        print(" ", end=" ")
    else:  # Remaining items are numbers to print
        print(str(item), end=" ")


def _check_flagging(square: str, world_size: int, world_created: bool) -> int | tuple[str, int, int]:
    """Checks if a square can be flagged"""
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
    return FAIL


def _validate(square: str, world_created: bool, world_size: int) -> \
            tuple[int, int] | tuple[str, int, int] | int:
    """Validates input from user into a location on the grid"""
    if len(square) < 2:
        return FAIL

    if square == "quit":
        return QUIT

    flag = _check_flagging(square, world_size, world_created)
    if flag == _IS_FLAG_FAIL:
        return FAIL
    elif flag != FAIL:
        return flag

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


def generate_mines(world: list[list[int]], avoid_square: tuple[int, int],
                   mine_count: int, world_size: int) -> list[list[int]]:
    """Generates the mines"""
    for _ in range(mine_count):
        r = random.randint(0, world_size - 1)
        c = random.randint(0, world_size - 1)
        #  prevent starting square from being a mine, next to a mine or stacking mines
        repeated = 0
        while ((r - 1 <= avoid_square[0] <= r + 1) and
               (c - 1 <= avoid_square[1] <= c + 1)) or world[r][c] != 0:
            if repeated > MAX_REPEAT_WORLD_GEN:
                print("Maximum attempts to prevent generation errors reached.")
                repeated = 0
                while r == avoid_square[0] and c == avoid_square[1]:
                    if repeated > MAX_REPEAT_WORLD_GEN:
                        print("Warning in generation: Mine not created at starting square.")
                        break

                    r = random.randint(0, world_size - 1)
                    c = random.randint(0, world_size - 1)

                    repeated += 1
                if repeated == MAX_REPEAT_WORLD_GEN:
                    r = -1  # prevent mine from being created
                break
            r = random.randint(0, world_size - 1)
            c = random.randint(0, world_size - 1)

            repeated += 1

        if r != -1:  # check if mine should be created
            world[r][c] = 1  # 1 for a mine
    return world


def count_nearby(world: list[list[int]], r: int, c: int, comp: int) -> int:
    nearby = world[r - 1][c] == comp if r > 0 else 0  # top
    nearby += world[r - 1][c - 1] == comp if r > 0 and c > 0 else 0  # top left
    nearby += world[r - 1][c + 1] == comp if r > 0 and c < len(world[r - 1]) - 1 else 0  # top right
    nearby += world[r + 1][c] == comp if r < len(world) - 1 else 0  # bottom
    nearby += world[r + 1][c - 1] == comp if r < len(world) - 1 and c > 0 else 0  # bottom left
    nearby += world[r + 1][c + 1] == comp if r < len(world) - 1 and c < len(world[r + 1]) - 1 else 0  # bottom right
    nearby += world[r][c - 1] == comp if c > 0 else 0  # left
    nearby += world[r][c + 1] == comp if c < len(world[r]) - 1 else 0  # right

    return nearby


def count_nearby_mines(world: list[list[int]], r: int, c: int) -> int:
    return count_nearby(world, r, c, 1)


def count_nearby_flags(world: list[list[int]], r: int, c: int) -> int:
    return count_nearby(world, r, c, FLAG)


def check_all_nearby(world: list[list[int]], r: int, c: int,
                     function: Callable[[[int, int]], int]) -> None:
    """Runs the supplied function on all the squares around the given square"""
    if r > 0 and world[r - 1][c] == HIDDEN:  # top
        _ = function((r - 1, c))
    if r > 0 and c > 0 and world[r - 1][c - 1] == HIDDEN:  # top left
        _ = function((r - 1, c - 1))
    if r > 0 and c < len(world[r - 1]) - 1 and world[r - 1][c + 1] == HIDDEN:  # top right
        function((r - 1, c + 1))
    if r < len(world) - 1 and world[r + 1][c] == HIDDEN:  # bottom
        _ = function((r + 1, c))
    if r < len(world) - 1 and c > 0 and world[r + 1][c - 1] == HIDDEN:  # bottom left
        _ = function((r + 1, c - 1))
    if r < len(world) - 1 and c < len(world[r + 1]) - 1 and world[r + 1][c + 1] == HIDDEN:  # bottom right
        _ = function((r + 1, c + 1))
    if c > 0 and world[r][c - 1] == HIDDEN:  # left
        _ = function((r, c - 1))
    if c < len(world[r]) - 1 and world[r][c + 1] == HIDDEN:  # right
        _ = function((r, c + 1))


def count_mines(world, visible_world):
    """Count the number of mines not flagged in the world"""
    m_count = 0
    f_count = 0
    for r in range(len(world)):
        for c in range(len(world[r])):
            if world[r][c] == 1:
                m_count += 1
            if visible_world[r][c] == FLAG:
                f_count += 1
    return m_count - f_count if m_count > f_count else 0


def process_square(square: str, world_size: int) -> int | tuple[int, int] | tuple[str, int, int]:
    """Processes a square"""
    if square == "help":
        print(INGAME_HELP)
        return 1
    if square == "quit":
        return QUIT
    if square == "exit":
        return QUIT
    if square == "print":
        return PRINT
    return _validate(square, True, world_size)


if __name__ == '__main__':
    print("functions.py doesn't contain any main functionality")
    exit(1)
