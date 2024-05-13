#!/usr/bin/env python3
"""
* Copyright (c) 2024 Matthew Brown
* Licensed under the MIT License, see LICENSE.md for details.
*
* About -
* I created this program to stretch my understanding of Python and
* to actually finish a project I have created. I started this project
* in 2023 for fun, and I have recently started working on it again with
* the help of AI to increase my knowledge of Python and practical coding.
* This game was originally designed to be a simple console based, minesweeper
* implementation, but I decided to add a GUI and unicode support for fun.
*
*
* How to Play - Console Version -
* To play the console version of the game, enter a square to get started.
* Squares are denoted by a letter and a number respectively, for example, a1, b2, c3
* This is akin to algebraic notation from chess which is a popular game I like.
* to flag a square, enter the letter f followed by the square number, for example, ff3.
* You may quit the game by typing 'quit' or by pressing Ctrl+C.
*
* How to Play - GUI Version -
* As of now, the GUI version is still experimental and is not yet fully functional.
* To play the GUI version of the game, run the program with the --use-gui flag. You can
* begin by clicking any tile. The timer will then start ticking. To flag a tile, click
* a tile with the right mouse button. To quit the game, click the Quit button.
*
* If you have any questions, comments or suggestions, please feel free to contact me
* or open an issue on GitHub at https://github.com/fieryknight2/minesweeper.
* I'm also available at my email address, furyinight3@gmail.com.
*
* main.py - Minesweeper game entry point
*
* Author: Matthew Brown
* Created May 5, 2023
* Last Modified May 13, 2024
"""
import sys
import time
import random
from functions import validate, print_world_item
from constants import *

enable_tkinter = True

try:
    import tkinter as tk
    import tkinter.ttk as ttk
except ImportError:
    enable_tkinter = False

    tk = None
    ttk = None

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
    --use-gui: Use the GUI
"""

VERSION_STRING = "0.3.0"


visible_world = []
world = []

mine_count = 25
world_size = 15

print_white_space = False
use_unicode = False
use_color = False
use_gui = False

if enable_tkinter:
    gui_buttons = []
    gui_world: tk.Frame | None = None
    gui_root: tk.Tk | None = None
    gui_lose_message: tk.Label | None = None
    gui_win_message: tk.Label | None = None
    gui_mines_left: tk.Label | None = None
    gui_time_taken: tk.Label | None = None
    gui_has_played_first_move = False
    gui_counting_time = False

random_seed = time.time()

start_time = 0


def print_world():
    """Prints the current minesweeper world in a grid"""
    if len(visible_world) > world_size or len(visible_world[1]) > world_size:
        return

    if print_white_space:
        print("\n" * 15)  # add some space

    if use_unicode:
        method = "use_unicode"
    elif use_color:
        method = "use_color"
    else:
        method = "default"

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
            print_world_item(item, method)
        print()
    print("Printed current field.", end="\n\n")


def create_world(starting_square):
    """Generates the first world, and populates with mines"""
    global visible_world, world
    visible_world = [[HIDDEN for _ in range(world_size)] for _j in range(world_size)]
    world = [[0 for _ in range(world_size)] for _j in range(world_size)]

    random.seed(random_seed)

    if mine_count >= world_size ** 2:  # Backup for if validation fails somewhere
        world = [[1 for _ in range(world_size)] for _j in range(world_size)]
        world[starting_square[0]][starting_square[1]] = 0
        check(starting_square)

        return

    for _ in range(mine_count):
        r = random.randint(0, world_size - 1)
        c = random.randint(0, world_size - 1)
        #  prevent starting square from being a mine, next to a mine or stacking mines
        repeated = 0
        while ((r - 1 <= starting_square[0] <= r + 1) and
               (c - 1 <= starting_square[1] <= c + 1)) or world[r][c] != 0:
            if repeated > MAX_REPEAT_WORLD_GEN:
                print("Maximum attempts to prevent generation errors reached.")
                repeated = 0
                while r == starting_square[0] and c == starting_square[1]:
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

    r, c = valid_square  # for readability

    if r < 0 or c < 0 or \
            r >= world_size or c >= world_size:  # out of bounds
        return False

    if visible_world[r][c] == FLAG:
        # square is flagged, ignore
        return False

    if world[r][c] == 1:  # check for a mine
        visible_world[r][c] = BOMB
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
    # access should be made in form world[r][c]

    bombs_nearby = ((world[r - 1][c] if r > 0 else 0) +  # top
                    (world[r - 1][c - 1] if r > 0 and c > 0 else 0) +  # top left
                    (world[r - 1][c + 1] if r > 0 and c < world_size - 1 else 0) +  # top right
                    (world[r + 1][c] if r < world_size - 1 else 0) +  # bottom
                    (world[r + 1][c - 1] if r < world_size - 1 and c > 0 else 0) +  # bottom left
                    (world[r + 1][c + 1] if r < world_size - 1 and c < world_size - 1 else 0) +  # bottom right
                    (world[r][c - 1] if c > 0 else 0) +  # left
                    (world[r][c + 1] if c < world_size - 1 else 0)  # right
                    )

    visible_world[r][c] = bombs_nearby

    if bombs_nearby == 0:
        if r > 0 and visible_world[r - 1][c] == HIDDEN:  # top
            check((r - 1, c))
        if r > 0 and c > 0 and visible_world[r - 1][c - 1] == HIDDEN:  # top left
            check((r - 1, c - 1))
        if r > 0 and c < world_size - 1 and visible_world[r - 1][c + 1] == HIDDEN:  # top right
            check((r - 1, c + 1))
        if r < world_size - 1 and visible_world[r + 1][c] == HIDDEN:  # bottom
            check((r + 1, c))
        if r < world_size - 1 and c > 0 and visible_world[r + 1][c - 1] == HIDDEN:  # bottom left
            check((r + 1, c - 1))
        if r < world_size - 1 and c < world_size - 1 and visible_world[r + 1][c + 1] == HIDDEN:  # bottom right
            check((r + 1, c + 1))
        if c > 0 and visible_world[r][c - 1] == HIDDEN:  # left
            check((r, c - 1))
        if c < world_size - 1 and visible_world[r][c + 1] == HIDDEN:  # right
            check((r, c + 1))

    return False


def force_check(valid_square: tuple[int, int]):
    """Force a check on all squares next to an already revealed square"""
    global visible_world
    bomb = 0
    r, c = valid_square  # for readability
    if visible_world[valid_square[0]][valid_square[1]] > 0:
        # count nearby flags
        flagged = (
                (r > 0 and visible_world[r - 1][c] == FLAG) +  # top
                (r > 0 and c > 0 and visible_world[r - 1][c - 1] == FLAG) +  # top left
                (r > 0 and c < world_size - 1 and visible_world[r - 1][c + 1] == FLAG) +  # top right
                (r < world_size - 1 and visible_world[r + 1][c] == FLAG) +  # bottom
                (r < world_size - 1 and c > 0 and visible_world[r + 1][c - 1] == FLAG) +  # bottom left
                (r < world_size - 1 and c < world_size - 1 and visible_world[r + 1][c + 1] == FLAG) +  # bottom right
                (c > 0 and visible_world[r][c - 1] == FLAG) +  # left
                (c < world_size - 1 and visible_world[r][c + 1] == FLAG)  # right
        )

        # only check if the user has flagged all nearby squares (to prevent accidental loss)
        if flagged == visible_world[valid_square[0]][valid_square[1]]:
            bomb = (
                    check((r - 1, c)) +  # top
                    check((r - 1, c - 1)) +  # top left
                    check((r - 1, c + 1)) +  # top right
                    check((r + 1, c)) +  # bottom
                    check((r + 1, c - 1)) +  # bottom left
                    check((r + 1, c + 1)) +  # bottom right
                    check((r, c - 1)) +  # left
                    check((r, c + 1))  # right
            )

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
                if mine_count >= MAX_WORLD_SIZE ** 2:
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
            if not enable_tkinter:
                print("Tkinter is not available, cannot use GUI.")
                sys.exit(1)
            global use_gui
            use_gui = True
        else:
            print(f"Unrecognized arguments: {arg}")
            print(HELP_STRING.format(args[0]))
            sys.exit(1)


def win():
    """Check for a win if the world has bombs left that aren't flags"""
    for r in range(len(world)):
        for c in range(len(world[r])):
            if world[r][c] == 1 and not visible_world[r][c] == FLAG:
                return False  # Bomb is not flagged
            if world[r][c] == 0 and visible_world[r][c] == FLAG:
                return False  # Something not a bomb is flagged
    for r in visible_world:
        for c in r:
            if c == HIDDEN:
                return False  # Square has not been revealed
    return True


def count_mines():
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


def gui_new_game():
    """Create a new game"""
    global gui_buttons, gui_has_played_first_move, random_seed, gui_counting_time
    gui_has_played_first_move = False
    gui_counting_time = False

    random_seed = time.time()

    # Actual world creation should be delayed until the user clicks a tile
    # clear the world
    for child in gui_world.winfo_children():
        child.destroy()

    if gui_lose_message is not None:
        gui_lose_message.destroy()

    if gui_win_message is not None:
        gui_win_message.destroy()

    gui_time_taken.configure(text="00:00:00")

    gui_buttons = []
    for i in range(world_size):
        gui_buttons.append([])
        for j in range(world_size):
            gui_buttons[i].append(ttk.Button(gui_world, takefocus=0, text="",
                                             command=lambda a=i, b=j: gui_click(a, b)))
            gui_buttons[i][j].bind("<Button-3>", lambda event=None, a=i, b=j: gui_flag(a, b))
            gui_buttons[i][j]["width"] = 2
            gui_buttons[i][j].grid(row=i, column=j)


def gui_lose():
    """Display a message to the user that they lost"""
    global gui_has_played_first_move, gui_lose_message, random_seed, gui_counting_time
    random_seed = time.time()

    gui_lose_message = tk.Label(gui_root, text="You have lost!")
    gui_lose_message.grid(row=0)

    update_gui()

    for child in gui_world.winfo_children():
        child.configure(state="disabled")

    gui_counting_time = False


def gui_win():
    """Display a message to the user that they won"""
    global gui_has_played_first_move, gui_win_message, random_seed, gui_counting_time
    random_seed = time.time()

    gui_win_message = tk.Label(gui_root, text="You have won!")
    gui_win_message.grid(row=0)

    for child in gui_world.winfo_children():
        child.configure(state="disabled")

    gui_counting_time = False


def update_gui():
    """Update the GUI"""
    for i in range(world_size):
        for j in range(world_size):
            if visible_world[i][j] == HIDDEN:
                gui_buttons[i][j].configure(text="")
            elif visible_world[i][j] == FLAG:
                gui_buttons[i][j].configure(text=CHARACTER_UNICODE["flag"])
            elif visible_world[i][j] == BOMB:
                gui_buttons[i][j].configure(text=CHARACTER_UNICODE["bomb"])
            else:
                gui_buttons[i][j].configure(text=str(visible_world[i][j]))
                if visible_world[i][j] == 0:
                    gui_buttons[i][j].configure(state="disabled")

    gui_mines_left.configure(text=str(count_mines()))


def gui_update_time():
    """Update the GUI timer"""
    if gui_counting_time:
        seconds = round(time.time() - start_time)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        seconds = str(seconds).zfill(2)
        minutes = str(minutes).zfill(2)
        hours = str(hours).zfill(2)
        gui_time_taken.configure(text=hours + ":" + minutes + ":" + seconds)

        gui_root.after(100, gui_update_time)


def gui_click(i, j):
    """Click a tile"""
    global gui_has_played_first_move, gui_counting_time, start_time

    # Initialize the world if it hasn't been initialized yet
    if not gui_has_played_first_move:
        create_world((i, j))
        gui_has_played_first_move = True

        update_gui()  # update the GUI

        # start game timer
        start_time = time.time()
        gui_counting_time = True
        gui_update_time()
        return

    if visible_world[i][j] > 0:
        if force_check((i, j)):
            gui_lose()
        else:
            update_gui()

            if win():
                gui_win()

        return

    if check((i, j)):
        gui_lose()
        return

    update_gui()  # update the GUI

    if win():
        gui_win()


def gui_flag(i, j):
    """Flag a tile"""
    global gui_has_played_first_move

    if not gui_has_played_first_move:
        # player can't flag a tile until they have played a move
        return

    flag(("f", i, j))  # flag the tile
    update_gui()  # update the GUI

    if win():
        gui_win()


def gui_main():
    """Alternative main loop for the GUI"""
    global start_time, gui_buttons, gui_world, gui_root, \
        gui_mines_left, gui_time_taken, gui_counting_time

    # Create the main window and run the event loop
    gui_root = tk.Tk()
    gui_root.geometry()
    gui_root.title('Minesweeper')

    # Create menu
    text_label = ttk.Label(gui_root, text="Minesweeper")
    text_label.grid(row=1)

    # Create main buttons
    buttons = ttk.Frame(gui_root)

    new_game_button = ttk.Button(buttons, text="New Game", command=gui_new_game)
    new_game_button.grid(column=0, row=0)

    quit_button = ttk.Button(buttons, text="Quit", command=gui_root.quit)
    quit_button.grid(column=1, row=0)

    buttons.columnconfigure(0, pad=15)
    buttons.rowconfigure(1, pad=15)

    buttons.grid(row=2)

    # Create game timer and remaining mine count
    counts = ttk.Frame(gui_root)

    timer_label = ttk.Label(counts, text="Timer")
    timer_label.grid(column=0, row=0)

    gui_time_taken = ttk.Label(counts, text="0:00")
    gui_time_taken.grid(column=0, row=1)

    gui_mine_count = ttk.Label(counts, text="Mines Left")
    gui_mine_count.grid(column=1, row=0)

    gui_mines_left = ttk.Label(counts, text=str(mine_count))
    gui_mines_left.grid(column=1, row=1)

    counts.grid(row=3)

    # Create world
    gui_world = ttk.Frame(gui_root)
    gui_world.configure(padding=10)

    gui_new_game()

    gui_world.grid(row=4)

    start_time = time.time()  # start game timer

    gui_root.mainloop()


def main(args):
    """Main function and entry point for the minesweeper program"""
    global start_time
    process_args(args)

    sys.setrecursionlimit(100 * world_size * world_size)  # might need rework in the future

    if use_gui:
        gui_main()  # start the GUI
        return

    # start game
    print("Welcome to Minesweeper!")
    square = input("Enter a starting square to begin: ").lower()

    start_time = time.time()  # start game timer

    validated_square = validate(square, False, world_size)
    while validated_square == -1:
        square = input("Enter a starting square to begin (Use algebraic notation): ").lower()
        validated_square = validate(square, False, world_size)

    create_world(validated_square)

    while True:
        print_world()

        square = input("Enter a square (type 'quit' for quit): ").lower()
        validated_square = validate(square, True, world_size)
        while validated_square == -1:
            square = input("Enter a square (Use algebraic notation): ").lower()
            validated_square = validate(square, True, world_size)

        if validated_square == -2:  # quit
            print("Quitting...")
            break
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
