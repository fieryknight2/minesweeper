#!/usr/bin/env python3
"""Minesweeper game entry point"""
import sys
import time
import random
import tkinter as tk
import tkinter.ttk as ttk

MAX_WORLD_SIZE = 26
ALPHABET = "abcdefghijklmnopqrstuvwxyz"

HELP_STRING = \
    """Welcome to Minesweeper!
Usage: {} minesweeper.py
    -h, --help: Print this help message
    -v, --version: Print the version
    -s, --seed: Set the random seed
    -m, --mine-count: Set the number of mines
    -w, --world-size: Set the world size
    --no-white-space: Do not print white space between squares
    
    Experimental options:
    --use-unicode: Use unicode characters
    --use-color: Use color characters
"""

VERSION_STRING = "0.2.0alpha"

FLAG = -1
HIDDEN = -2
BOMB = -3
NOTHING = 0

visible_world = []
world = []

mine_count = 25
world_size = 15

print_white_space = False
use_unicode = False
use_color = False
use_gui = False

random_seed = time.time()

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

start_time = 0


def alph_to_coord(letter):
    """Converts a letter to its corresponding number a-1, b-2, etc."""
    if isinstance(letter, str) and letter in ALPHABET:
        return int(ord(letter) - ord("a"))
    print("Internal Error! Bad string given!")
    sys.exit(1)


def print_world():
    """Prints the current minesweeper world in a grid"""
    if len(visible_world) > world_size or len(visible_world[1]) > world_size:
        return

    if print_white_space:
        print("\n" * 15)  # add some space

    # print header
    print(" " * 4, end="")
    for letter in range(len(visible_world)):
        print(ALPHABET[letter].upper(), end=" ")
    print()

    # print rows
    for i, row in enumerate(visible_world):
        if len(row) > world_size:
            print("ERROR: Incorrect sizing")
            sys.exit(1)

        form = "0" + str(i + 1)
        print(form[len(form) - 2:], end=": ")
        for item in row:
            if item == -2:  # -2 is not visible
                if use_unicode:
                    print(CHARACTER_UNICODE["hidden"], end=" ")
                elif use_color:
                    print(CHARACTER_COLOR["hidden"] + "X" + CHARACTER_COLOR["reset"], end=" ")
                else:
                    print("X", end=" ")
            elif item == -1:  # -1 is flagged
                if use_unicode:
                    print(CHARACTER_UNICODE["flag"], end=" ")
                elif use_color:
                    print(CHARACTER_COLOR["flag"] + "F" + CHARACTER_COLOR["reset"], end=" ")
                else:
                    print("F", end=" ")
            elif item == -3:
                if use_unicode:
                    print(CHARACTER_UNICODE["bomb"], end="")
                elif use_color:
                    print(CHARACTER_COLOR["bomb"] + "B" + CHARACTER_COLOR["reset"], end=" ")
                else:
                    print("B", end=" ")
            elif item == 0:  # 0  means nothing
                print(" ", end=" ")
            else:  # Remaining items are numbers to print
                print(str(item), end=" ")
        print()
    print("Printed current field.", end="\n\n")


def validate(square, world_created):
    """Validates input from user into a location on the grid"""
    if len(square) < 2:
        return -1

    if (square[0] in "Ff") and (len(square) == 3 or len(square) == 4) \
            and (not square[1].isnumeric()) and world_created:  # flag a square
        if not square[1] in ALPHABET:
            return -1
        if alph_to_coord(square[1]) > world_size or alph_to_coord(square[0]) < 0:
            return -1
        c = alph_to_coord(square[1])

        if not square[2:].isnumeric():
            return -1
        if int(square[2:]) > world_size or int(square[2:]) < 1:
            return -1
        r = int(square[2:])

        return "f", r - 1, c

    if not world_created and square[0] in "Ff" and not square[1].isnumeric():
        return -1

    if len(square) != 2 and len(square) != 3:
        return -1

    # check for letter
    if not square[0] in ALPHABET:
        return -1
    if alph_to_coord(square[0]) > world_size or alph_to_coord(square[0]) < 0:
        return -1
    c = alph_to_coord(square[0])

    # check for number
    if not square[1:].isnumeric():
        return -1
    if int(square[1:]) > world_size or int(square[1]) < 1:
        return -1
    r = int(square[1:])

    return r - 1, c


def create_world(starting_square):
    """Generates the first world, and populates with mines"""
    global visible_world, world
    visible_world = [[HIDDEN for _ in range(world_size)] for _j in range(world_size)]
    world = [[0 for _ in range(world_size)] for _j in range(world_size)]

    random.seed(random_seed)

    for i in range(mine_count):
        r = random.randint(0, world_size - 1)
        c = random.randint(0, world_size - 1)
        #  prevent starting square from being a mine or stacking mines
        while (c == starting_square[0] and r == starting_square[1]) or world[r][c] == 1:
            r = random.randint(0, world_size - 1)
            c = random.randint(0, world_size - 1)

        world[r][c] = 1  # 1 for a mine

    check(starting_square)


def flag(valid_square):
    """Simple function for flagging a square"""
    global visible_world
    if visible_world[valid_square[1]][valid_square[2]] == HIDDEN:
        visible_world[valid_square[1]][valid_square[2]] = FLAG
        # print(visible_world[valid_square[1]][valid_square[2]])
    elif visible_world[valid_square[1]][valid_square[2]] == FLAG:
        visible_world[valid_square[1]][valid_square[2]] = HIDDEN


def check(valid_square: tuple[int, int]):
    """Function for processing a square and those around it"""
    global visible_world
    if valid_square[0] < 0 or valid_square[1] < 0 or \
            valid_square[0] >= world_size or valid_square[1] >= world_size:  # out of bounds
        return False

    if visible_world[valid_square[0]][valid_square[1]] == FLAG:
        # square is flagged, ignore
        return False

    if world[valid_square[0]][valid_square[1]] == 1:  # check for a mine
        visible_world[valid_square[0]][valid_square[1]] = BOMB
        return True

    # world is laid out in a grid:
    # [
    #  [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],  # row 0
    #  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],  # row 1
    #  ...
    # ]
    #
    # first access for world(world[0]) is a row and therefore corresponds to height
    # second access for world(world[0][0]) is a column and therefore corresponds to width

    bombs_nearby = 0

    if valid_square[0] > 0:  # prevent out of bounds error
        bombs_nearby += world[valid_square[0] - 1][valid_square[1]]  # top
    if valid_square[0] > 0 and valid_square[1] > 0:
        bombs_nearby += world[valid_square[0] - 1][valid_square[1] - 1]  # top left
    if valid_square[0] > 0 and valid_square[1] < world_size - 1:
        bombs_nearby += world[valid_square[0] - 1][valid_square[1] + 1]  # top right

    if valid_square[0] < world_size - 1:
        bombs_nearby += world[valid_square[0] + 1][valid_square[1]]  # bottom
    if valid_square[0] < world_size - 1 and valid_square[1] > 0:
        bombs_nearby += world[valid_square[0] + 1][valid_square[1] - 1]  # bottom left
    if valid_square[0] < world_size - 1 and valid_square[1] < world_size - 1:
        bombs_nearby += world[valid_square[0] + 1][valid_square[1] + 1]  # bottom right

    if valid_square[1] > 0:
        bombs_nearby += world[valid_square[0]][valid_square[1] - 1]  # left
    if valid_square[1] < world_size - 1:
        bombs_nearby += world[valid_square[0]][valid_square[1] + 1]  # right
    visible_world[valid_square[0]][valid_square[1]] = bombs_nearby

    if bombs_nearby == 0:
        if valid_square[0] > 0 and visible_world[valid_square[0] - 1][valid_square[1]] == HIDDEN:
            check((valid_square[0] - 1, valid_square[1]))  # top
        if valid_square[0] > 0 and valid_square[1] > 0 and \
                visible_world[valid_square[0] - 1][valid_square[1] - 1] == HIDDEN:
            check((valid_square[0] - 1, valid_square[1] - 1))  # top left
        if valid_square[0] > 0 and valid_square[1] < world_size - 1 and \
                visible_world[valid_square[0] - 1][valid_square[1] + 1] == HIDDEN:
            check((valid_square[0] - 1, valid_square[1] + 1))  # top right
        if valid_square[0] < world_size - 1 and \
                visible_world[valid_square[0] + 1][valid_square[1]] == HIDDEN:
            check((valid_square[0] + 1, valid_square[1]))  # bottom
        if valid_square[0] < world_size - 1 and valid_square[1] > 0 and \
                visible_world[valid_square[0] + 1][valid_square[1] - 1] == HIDDEN:
            check((valid_square[0] + 1, valid_square[1] - 1))  # bottom left
        if valid_square[0] < world_size - 1 and valid_square[1] < world_size - 1 and \
                visible_world[valid_square[0] + 1][valid_square[1] + 1] == HIDDEN:
            check((valid_square[0] + 1, valid_square[1] + 1))  # bottom right
        if valid_square[1] > 0 and visible_world[valid_square[0]][valid_square[0] - 1] == HIDDEN:
            check((valid_square[0], valid_square[1] - 1))  # left
        if valid_square[1] < world_size - 1 and \
                visible_world[valid_square[0]][valid_square[1] + 1] == HIDDEN:
            check((valid_square[0], valid_square[1] + 1))  # right

    return False


def force_check(valid_square: tuple[int, int]):
    """Force a check on all squares next to an already revealed square"""
    global visible_world
    bomb = 0
    if visible_world[valid_square[0]][valid_square[1]] > 0:
        # count nearby flags
        flagged = 0
        flagged += 1 if valid_square[0] > 0 and \
            visible_world[valid_square[0] - 1][valid_square[1]] == FLAG else 0  # top
        flagged += 1 if valid_square[0] > 0 and valid_square[1] > 0 and \
            visible_world[valid_square[0] - 1][valid_square[1] - 1] == FLAG else 0  # top left
        flagged += 1 if valid_square[0] > 0 and valid_square[1] < world_size - 1 and \
            visible_world[valid_square[0] - 1][valid_square[1] + 1] == FLAG else 0  # top right

        flagged += 1 if valid_square[0] < world_size - 1 and \
            visible_world[valid_square[0] + 1][valid_square[1]] == FLAG else 0  # bottom
        flagged += 1 if valid_square[0] < world_size - 1 and valid_square[1] > 0 and \
            visible_world[valid_square[0] + 1][valid_square[1] - 1] == FLAG else 0  # bottom left
        flagged += 1 if valid_square[0] < world_size - 1 and valid_square[1] < world_size - 1 and \
            visible_world[valid_square[0] + 1][valid_square[1] + 1] == FLAG else 0  # bottom right

        flagged += 1 if valid_square[1] > 0 and \
            visible_world[valid_square[0]][valid_square[1] - 1] == FLAG else 0  # left
        flagged += 1 if valid_square[1] < world_size - 1 and \
            visible_world[valid_square[0]][valid_square[1] + 1] == FLAG else 0  # right

        # only check if the user has flagged all nearby squares (to prevent accidental loss)
        if flagged == visible_world[valid_square[0]][valid_square[1]]:
            bomb += check((valid_square[0] - 1, valid_square[1]))  # top
            bomb += check((valid_square[0] - 1, valid_square[1] - 1))  # top left
            bomb += check((valid_square[0] - 1, valid_square[1] + 1))  # top right
            bomb += check((valid_square[0] + 1, valid_square[1]))  # bottom
            bomb += check((valid_square[0] + 1, valid_square[1] - 1))  # bottom left
            bomb += check((valid_square[0] + 1, valid_square[1] + 1))  # bottom right
            bomb += check((valid_square[0], valid_square[1] - 1))  # left
            bomb += check((valid_square[0], valid_square[1] + 1))  # right

    return bomb


def process_args(args):
    """Process command line arguments"""
    if len(args) <= 1:
        return

    if args[1] in ["-h", "--help"]:
        print(HELP_STRING.format(args[0]))
        sys.exit(0)

    if args[1] in ["-v", "--version"]:
        print(VERSION_STRING)
        sys.exit(0)

    skip = False
    for j, arg in enumerate(args[1:]):
        i = j + 1
        if skip:
            skip = False
            continue

        if arg in ["-s", "--seed"]:
            global random_seed
            if len(args) >= i and str(args[i]).isnumeric():
                random_seed = int(args[i])
                skip = True
        elif arg in ["-w", "--world-size"]:
            global world_size
            if len(args) >= i and str(args[i + 1]).isnumeric():
                world_size = int(args[i + 1])
                if world_size > MAX_WORLD_SIZE:
                    print(f"World size must be less than {MAX_WORLD_SIZE}.")
                    print(HELP_STRING.format(args[0]))
                    sys.exit(1)
                print(f"World size set to {world_size}.")
            else:
                print(HELP_STRING.format(args[0]))
                sys.exit(1)
            skip = True
        elif arg in ["-m", "--mine-count"]:
            global mine_count
            if len(args) >= i and str(args[i + 1]).isnumeric():
                mine_count = int(args[i + 1])
                if mine_count > MAX_WORLD_SIZE ** 2:
                    print(f"Mine count must be less than {MAX_WORLD_SIZE ** 2}.")
                    print(HELP_STRING.format(args[0]))
                    sys.exit(1)
                print(f"Mine count set to {mine_count}.")
                skip = True
        elif arg == "--no-white-space":
            global print_white_space
            print_white_space = False
        elif arg == "--use-unicode":
            global use_unicode
            use_unicode = True
        elif arg == "--use-color":
            global use_color
            use_color = True
        elif arg == "--use-gui":
            global use_gui
            use_gui = True
        else:
            print(f"Unrecognized arguments: {arg}")
            print(HELP_STRING.format(args[0]))
            sys.exit(1)


def win():
    """Check for a win if the world has bombs left that aren't flags"""
    for r, row in enumerate(world):
        for c, col in enumerate(row):
            if world[r][c] == 1 and not visible_world[r][c] == FLAG:
                return False
    return True


def gui_new_game(gui_world):
    """Create a new game"""
    # Actual world creation should be delayed until the user clicks a tile
    # clear the world
    for child in gui_world.winfo_children():
        child.destroy()

    w_buttons = []
    for i in range(world_size):
        w_buttons.append([])
        for j in range(world_size):
            w_buttons[i].append(ttk.Button(gui_world, text="",
                                           command=lambda a=i, b=j: gui_click(a, b)).grid(row=i, column=j))
    return w_buttons


def gui_click(i, j):
    """Click a tile"""
    print(f"Clicked {i}, {j}")
    pass  # TODO implement


def gui_main(args):
    """Alternative main loop for the GUI"""
    global start_time
    process_args(args)

    # Create the main window and run the event loop
    root = tk.Tk()
    root.geometry('800x600')
    root.title('Minesweeper')

    # Create menu
    text_label = ttk.Label(root, text="Minesweeper")
    text_label.grid()

    # Create main buttons
    buttons = ttk.Frame(root)

    new_game_button = ttk.Button(buttons, text="New Game", command=gui_new_game)
    new_game_button.grid(column=0, row=0)

    quit_button = ttk.Button(buttons, text="Quit", command=root.quit)
    quit_button.grid(column=1, row=0)

    buttons.columnconfigure(0, pad=15)
    buttons.rowconfigure(1, pad=15)
    buttons.grid()

    # Create game timer and remaining mine count
    counts = ttk.Frame(root)

    timer_label = ttk.Label(counts, text="Timer")
    timer_label.grid(column=0, row=0)

    timer = ttk.Label(counts, text="0:00")
    timer.grid(column=0, row=1)

    mine_count_label = ttk.Label(counts, text="Mines Left")
    mine_count_label.grid(column=1, row=0)

    mine_count_visible = ttk.Label(counts, text="0")
    mine_count_visible.grid(column=1, row=1)

    counts.grid()

    # Create world
    gui_world = ttk.Frame(root)

    w_buttons = gui_new_game(gui_world)

    gui_world.grid()

    start_time = time.time()  # start game timer
    root.mainloop()


def main(args):
    """Main function and entry point for the minesweeper program"""
    global start_time
    process_args(args)

    sys.setrecursionlimit(100 * world_size * world_size)  # might need rework in the future

    if use_gui:
        gui_main(args)  # start the GUI

        # do something here (maybe)

        return

    # start game
    print("Welcome to Minesweeper!")
    square = input("Enter a starting square to begin: ").lower()

    start_time = time.time()  # start game timer

    validated_square = validate(square, False)
    while validated_square == -1:
        square = input("Enter a starting square to begin (Use algebraic notation): ").lower()
        validated_square = validate(square, False)

    create_world(validated_square)

    while True:
        print_world()

        square = input("Enter a square: ").lower()
        validated_square = validate(square, True)
        while validated_square == -1:
            square = input("Enter a square (Use algebraic notation): ").lower()
            validated_square = validate(square, True)

        if validated_square[0] == "f":  # flag
            flag(validated_square)
        else:
            if visible_world[validated_square[0]][validated_square[1]] > 0:
                x = force_check(validated_square)
            else:
                x = check(validated_square)

            if x:
                print("Oh No! You hit a bomb!")
                print_world()
                print("Oh No! You hit a bomb!")
                print("You have lost!")
                break
        if win():
            print("Congrats! You win!")
            break

    finish_time = time.time() - start_time
    print(f"Finished in {round(finish_time)} seconds.")


if __name__ == '__main__':
    main(sys.argv)  # runs the program
