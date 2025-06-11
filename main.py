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
* This game was originally designed to be a simple console-based, minesweeper
* implementation, but I decided to add a GUI and unicode support for fun.
*
*
* How to Play - Console Version -
* To play the console version of the game, enter a square to get started.
* Squares are denoted by a letter and a number respectively, for example, a1, b2, c3
* This is akin to algebraic notation from chess, which is a popular game I like.
* to flag a square, enter the letter f followed by the square number, for example, ff3.
* You may quit the game by typing 'quit' or by pressing Ctrl+C.
*
* How to Play - GUI Version -
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
* Last Modified June 10, 2025
"""
VERSION_STRING = "1.1.0.0"

import sys
import time
import random
import argparse

enable_tkinter: bool = True

try:
    import tkinter as tk
    import tkinter.ttk as ttk
except ImportError:
    enable_tkinter = False

    tk = None
    ttk = None

# ---------- Constants ----------

class Constants:
    MAX_GUI_WORLD_SIZE = 250

    FLAG = 'F'
    HIDDEN = 'X'
    BOMB = 'B'
    BAD_FLAG = 'L'
    EMPTY = '.'

    MENU_QUIT = 1
    MENU_DISPLAY = 2
    MENU_ERROR = 3
    MENU_HELP = 4
    MENU_ENABLE_COLOR = 5
    MENU_ENABLE_UNICODE = 6

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
        "hidden": "\033[34m",  # blue
        "reset": "\033[0m",  # reset
    }

    MENU_HELP_STRING = """Commands:
    help: Print this help message
    quit: Quit the game
    print: Reprint the current world
    color: Enable color
    unicode: Enable unicode

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

class World:
    MAX_WORLD_SIZE_X = 26
    MAX_WORLD_SIZE_Y = 100

    EASY_SIZE_X = 9
    EASY_SIZE_Y = 9
    EASY_MINE_COUNT = 10

    def __init__(self, **kwargs):
        """
        :param kwargs:
            Potential defaults to edit while creating the world can be supplied here:
            mine_count - The mine count for the created world
            world_size_x - The width of the world
            world_size_y - The height of the world

            Display options can also be set:
            use_color - Use color while displaying the world
            use_unicode - Use Unicode while displaying the world
            use_gui - Use the tkinter GUI
        """
        self.has_generated = False
        self.visible: list[list[str]] = []
        self.mines: list[list[bool]] = []

        self.mine_count: int = 9 if "mine_count" not in kwargs.keys() else kwargs["mine_count"]
        self.world_size_x: int = 10 if "world_size_x" not in kwargs.keys() else kwargs["world_size_x"]
        self.world_size_y: int = 10 if "world_size_y" not in kwargs.keys() else kwargs["world_size_y"]

        self.use_color = False if "use_color" not in kwargs.keys() else kwargs["use_color"]
        self.use_unicode = False if "use_unicode" not in kwargs.keys() else kwargs["use_unicode"]
        # self.use_gui = False if "use_gui" not in kwargs.keys() else kwargs["use_gui"]

        self.display_empty = False if "display_empty" not in kwargs.keys() else kwargs["display_empty"]

        self.start_time = 0
        self.paused_for = 0

    def generate(self, start_square: tuple[int, int] | None) -> None:
        if start_square is not None:
            if not self.in_bounds(start_square[0], start_square[1]):
                print(f"Error occurred while generating world: Incorrect position for start square ({
                        start_square[0]}, {start_square[1]})")

        if self.mine_count >= ((self.world_size_x * self.world_size_y) - 1):
            print("Error occurred while generating world: Too many mines!")
            # print(f"{self.mine_count}, {self.world_size_x}, {self.world_size_y}")
            return

        self.mines = [[False for _ in range(self.world_size_x)] for _ in range(self.world_size_y)]
        self.visible = [[Constants.HIDDEN for _ in range(self.world_size_x)] for _ in range(self.world_size_y)]

        # Ensure start square does not have a mine on it
        if start_square:
            self.mines[start_square[1]][start_square[0]] = True

        for _ in range(self.mine_count):
            x, y = random.randint(0, self.world_size_x - 1), random.randint(0, self.world_size_y - 1)
            while self.mines[x][y]:
                x, y = random.randint(0, self.world_size_x - 1), random.randint(0, self.world_size_y - 1)

            self.mines[x][y] = True

        if start_square:
            self.mines[start_square[1]][start_square[0]] = False

            self.check_square(start_square[0], start_square[1])

        self.has_generated = True
        self.start_time = time.time()

    def display(self) -> None:
        """Display the world"""
        if not self.has_generated:
            raise Exception("World has not been generated")

        print("  ", end="")
        for i in range(self.world_size_x):
            if i < 26:
                print(f" {chr(i + ord('a'))}", end="")
            else:
                # TODO
                pass

        print()
        for y in range(self.world_size_y):
            print(f"{y + 1:2}", end="")
            for x in range(self.world_size_x):
                dp_value = self.visible[y][x]

                if dp_value == Constants.EMPTY and not self.display_empty:
                    dp_value = ' '

                display_set = {
                    "bomb": Constants.BOMB,
                    "flag": Constants.FLAG,
                    "hidden": Constants.HIDDEN,
                    "bad_flag": Constants.BAD_FLAG,
                }

                if self.use_unicode:
                    display_set = Constants.CHARACTER_UNICODE

                match dp_value:
                    case Constants.BOMB:
                        dp_value = display_set["bomb"]
                    case Constants.FLAG:
                        dp_value = display_set["flag"]
                    case Constants.HIDDEN:
                        dp_value = display_set["hidden"]
                    case Constants.BAD_FLAG:
                        dp_value = display_set["bad_flag"]
                print(" ", end="")

                if self.use_color:
                    match dp_value:
                        case Constants.BOMB:
                            print(Constants.CHARACTER_COLOR["bomb"], end="")
                        case Constants.FLAG:
                            print(Constants.CHARACTER_COLOR["flag"], end="")
                        case Constants.HIDDEN:
                            print(Constants.CHARACTER_COLOR["hidden"], end="")
                        case Constants.BAD_FLAG:
                            print(Constants.CHARACTER_COLOR["bad_flag"], end="")
                print(f"{dp_value}", end="")

                if self.use_color:
                    print(Constants.CHARACTER_COLOR["reset"], end="")
            print()

        print()

    def display_all(self):
        vis = self.visible
        for x in range(self.world_size_x):
            for y in range(self.world_size_y):
                self.check_square(x, y)

                if self.visible[y][x] == Constants.FLAG and self.mines[x][y]:
                    self.visible[y][x] = Constants.BAD_FLAG

        self.display()

        self.visible = vis

    def check_square(self, x: int, y: int) -> bool:
        """Check the given square for mines and clear it on the visible plane. Ignores flagged squares"""
        if not self.in_bounds(x, y):
            return False

        if self.visible[y][x] in [Constants.FLAG, Constants.EMPTY]:
            return False

        if self.visible[y][x] == Constants.HIDDEN:
            if self.mines[y][x]:
                self.visible[y][x] = Constants.BOMB
                return True

            count = self.count_nearby(x, y, Constants.BOMB)

            if count == 0:
                self.visible[y][x] = Constants.EMPTY
                for X in range(x - 1, x + 2):
                    for Y in range(y - 1, y + 2):
                        if (X == x and Y == y) or not self.in_bounds(X, Y):
                            continue

                        if self.visible[Y][X] == Constants.HIDDEN:
                            self.check_square(X, Y)
            else:
                self.visible[y][x] = str(count)

        elif self.visible[y][x].isnumeric():
            if self.count_nearby(x, y, Constants.FLAG) == int(self.visible[y][x]):
                for X in range(x - 1, x + 2):
                    for Y in range(y - 1, y + 2):
                        if (X == x and Y == y) or not self.in_bounds(X, Y):
                            continue

                        if self.visible[X][Y] == Constants.HIDDEN:
                            if self.check_square(X, Y):
                                return True

        return False

    def flag_square(self, x: int, y: int) -> None:
        """Toggle flag on the given square for mines"""
        if self.visible[y][x] == Constants.FLAG:
            self.visible[y][x] = Constants.HIDDEN
        elif self.visible[y][x] == Constants.HIDDEN:
            self.visible[y][x] = Constants.FLAG

    def check_win(self) -> bool:
        for x in range(self.world_size_x):
            for y in range(self.world_size_y):
                if self.visible[y][x] == Constants.HIDDEN:
                    return False
                if self.visible[y][x] == Constants.FLAG and not self.mines[y][x]:
                    return False

        return True

    def count_unflagged_mines(self) -> int:
        count = 0
        for x in range(self.world_size_x):
            for y in range(self.world_size_y):
                if self.mines[y][x] and self.visible[y][x] != Constants.FLAG:
                    count += 1

        return count

    def count_nearby(self, x: int, y: int, value: str) -> int:
        count = 0
        for X in range(x - 1, x + 2):
            for Y in range(y - 1, y + 2):
                if self.in_bounds(X, Y) and not (X == x and Y == y):
                    match value:
                        case Constants.FLAG:
                            count += self.visible[Y][X] == Constants.FLAG
                        case Constants.BOMB:
                            count += self.mines[Y][X]

        return count

    def in_bounds(self, x, y):
        return self.world_size_x > x >= 0 and self.world_size_y > y >= 0

if enable_tkinter:
    gui_buttons: list[list[tk.Button]] = []
    gui_world: tk.Frame | None = None
    gui_root: tk.Tk | None = None
    gui_lose_message: tk.Label | None = None
    gui_win_message: tk.Label | None = None
    gui_mines_left: tk.Label | None = None
    gui_time_taken: tk.Label | None = None
    gui_has_played_first_move = False
    gui_counting_time = False

    # New game gui elements
    gui_new_window: tk.Tk | None = None
    gui_mine_count: tk.Entry | None = None
    gui_world_size: tk.Entry | None = None
    gui_lose_state: bool = False

random_seed: float = time.time()


def process_args(args: list[str]) -> dict:
    """Process command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", help="Print the version")
    parser.add_argument("-s", "--seed", help="Set the random seed", type=int)
    parser.add_argument("-m", "--mine-count", help="Set the number of mines", type=int)
    parser.add_argument("--world-size-x", help="Set the width of the world", type=int)
    parser.add_argument("--world-size-y", help="Set the height of the world", type=int)
    parser.add_argument("--no-white-space", help="Print '.' instead of spaces", action="store_true")
    parser.add_argument("--use-unicode", help="Use unicode characters", action="store_true")
    parser.add_argument("--use-color", help="Use color characters", action="store_true")
    parser.add_argument("--use-gui", help="Use the GUI", action="store_true")

    args = parser.parse_args()

    if args.version:
        print(VERSION_STRING)
        sys.exit(0)

    if args.seed:
        random.seed(args.seed)

    return {
        "mine-count": args.mine_count if args.mine_count else World.EASY_MINE_COUNT,
        "world-size-x": args.world_size_x if args.world_size_x else World.EASY_SIZE_X,
        "world-size-y": args.world_size_y if args.world_size_y else World.EASY_SIZE_Y,
        "no-white-space": args.no_white_space,
        "use-unicode": args.use_unicode,
        "use-color": args.use_color,
        "use-gui": args.use_gui
    }


def gui_new_game() -> None:
    """Create a new game"""
    global gui_buttons, gui_has_played_first_move, random_seed, gui_counting_time, gui_lose_state
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

    gui_lose_state = False


def gui_lose(world: World) -> None:
    """Display a message to the user that they lost"""
    global gui_has_played_first_move, gui_lose_message, random_seed, gui_counting_time, gui_lose_state
    random_seed = time.time()

    gui_lose_message = tk.Label(gui_root, text="You have lost!")
    gui_lose_message.grid(row=0)

    gui_lose_state = True
    update_gui(world)

    child: tk.Widget
    for child in gui_world.winfo_children():
        child.configure(state="disabled")

    gui_counting_time = False


def gui_win() -> None:
    """Display a message to the user that they won"""
    global gui_has_played_first_move, gui_win_message, random_seed, gui_counting_time
    random_seed = time.time()

    gui_win_message = tk.Label(gui_root, text="You have won!")
    gui_win_message.grid(row=0)

    for child in gui_world.winfo_children():
        child.configure(state="disabled")

    gui_counting_time = False


def update_gui(world) -> None:
    """Update the GUI"""
    for i in range(world_size):
        for j in range(world_size):
            if world.visible[i][j] == Constants.HIDDEN:
                gui_buttons[i][j].configure(text="")
            elif world.visible[i][j] == Constants.FLAG:
                gui_buttons[i][j].configure(text=Constants.CHARACTER_UNICODE["flag"])
            elif world.visible[i][j] == Constants.BOMB:
                gui_buttons[i][j].destroy()
                gui_buttons[i][j] = ttk.Label(gui_world, text=Constants.CHARACTER_UNICODE["bomb"])
                gui_buttons[i][j].grid(row=i, column=j)
            else:
                if world.visible[i][j] == 0:
                    if not isinstance(gui_buttons[i][j], ttk.Label):
                        gui_buttons[i][j].destroy()
                        gui_buttons[i][j] = ttk.Label(gui_world, text="")
                        gui_buttons[i][j].grid(row=i, column=j)

                    # gui_buttons[i][j].configure(text="")
                    # gui_buttons[i][j].configure(state="disabled")
                else:
                    gui_buttons[i][j].configure(text=str(world.visible[i][j]))
                    gui_buttons[i][j].configure(state="normal")
            if gui_lose_state:
                if world.visible[i][j] == Constants.FLAG and world[i][j] == 0:
                    gui_buttons[i][j].destroy()
                    gui_buttons[i][j] = ttk.Label(gui_world, text=Constants.CHARACTER_UNICODE["bad_flag"], foreground="red")
                    gui_buttons[i][j].grid(row=i, column=j)
                if world.visible[i][j] == Constants.HIDDEN and world[i][j] == 1:
                    gui_buttons[i][j].destroy()
                    gui_buttons[i][j] = ttk.Label(gui_world, text=Constants.CHARACTER_UNICODE["bomb"], foreground="red")
                    gui_buttons[i][j].grid(row=i, column=j)
                # elif world.visible[i][j] == 0:
                #    gui_buttons[i][j].destroy()
                #    gui_buttons[i][j] = ttk.Label(gui_world, text="")
                #    gui_buttons[i][j].grid(row=i, column=j)

    gui_mines_left.configure(text=str(world.count_unflagged_mines()))


def gui_update_time(world: World) -> None:
    """Update the GUI timer"""
    if gui_counting_time:
        seconds = round(time.time() - world.start_time)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        seconds = str(seconds).zfill(2)
        minutes = str(minutes).zfill(2)
        hours = str(hours).zfill(2)
        gui_time_taken.configure(text=hours + ":" + minutes + ":" + seconds)

        gui_root.after(100, gui_update_time)


def gui_click(world: World, i: int, j: int) -> None:
    """Click a tile"""
    global gui_has_played_first_move, gui_counting_time

    # Initialize the world if it hasn't been initialized yet
    if not gui_has_played_first_move:
        world.generate((i, j))
        gui_has_played_first_move = True

        update_gui(world)  # update the GUI

        # start game timer
        gui_counting_time = True
        gui_update_time(world)
        return

    if world.visible[i][j] == Constants.HIDDEN:
        if world.check_square(i, j):
            gui_lose(world)
        else:
            update_gui(world)

            if world.check_win():
                gui_win()

        return

    if world.check_square(i, j):
        gui_lose(world)
        return

    update_gui(world)  # update the GUI

    if world.check_win():
        gui_win()


def gui_flag(world: World, i: int, j: int) -> None:
    """Flag a tile"""
    global gui_has_played_first_move

    if not gui_has_played_first_move:
        # player can't flag a tile until they have played a move
        return

    world.flag_square(i, j)  # flag the tile
    update_gui(world)  # update the GUI

    if world.check_win():
        gui_win()


def gui_change_mine_count(new_count: str) -> bool:
    """Change the mine count"""
    if new_count == "":
        return True  # Enable an empty text input
    if not new_count.isnumeric():
        return False
    return True


def gui_change_world_size(new_size: str) -> bool:
    """Change the world size"""
    if new_size == "":
        return True  # Enable an empty text input
    if not new_size.isnumeric():
        return False
    return True


def gui_process_new_game_input() -> None:
    """Process the new game input"""
    global mine_count, world_size

    # validation
    if gui_mine_count.get() == "" or not gui_mine_count.get().isnumeric() \
            or int(gui_mine_count.get()) < 1 or int(gui_mine_count.get()) > Constants.MAX_GUI_WORLD_SIZE ** 2:
        return
    if gui_world_size.get() == "" or not gui_world_size.get().isnumeric() \
            or int(gui_world_size.get()) < 3 or int(gui_world_size.get()) > Constants.MAX_GUI_WORLD_SIZE:
        return

    mine_count = int(gui_mine_count.get())
    world_size = int(gui_world_size.get())

    # close popup window
    gui_new_window.destroy()

    gui_new_game()


def gui_new_game_window() -> None:
    """Create a new game window"""
    global gui_new_window, gui_mine_count, gui_world_size

    gui_new_window = tk.Toplevel()
    gui_new_window.title("New Game")

    reg_change_world_size = gui_new_window.register(gui_change_world_size)
    reg_change_mine_count = gui_new_window.register(gui_change_mine_count)

    # gui_new_window.geometry("400x100")

    ttk.Label(gui_new_window, text="New Game Settings",
              font=(ttk.Style().lookup("TButton", "font"), 10, "bold")).pack(pady=5)

    layout = ttk.Frame(gui_new_window)

    ttk.Label(layout, text="Mine Count", justify="left", width=12).grid(row=0, column=0)

    # Create the entry field for the mine count
    gui_mine_count = ttk.Entry(layout, width=12)
    gui_mine_count.insert(0, str(mine_count))
    gui_mine_count.config(validate="key", validatecommand=(reg_change_mine_count, "%P"))
    gui_mine_count.grid(row=1, column=0, padx=5)

    ttk.Label(layout, text="World Size", justify="left", width=12).grid(row=0, column=1)

    # Create the entry field for the world size
    gui_world_size = ttk.Entry(layout, width=12)
    gui_world_size.insert(0, str(world_size))
    gui_world_size.config(validate="key", validatecommand=(reg_change_world_size, "%P"))
    gui_world_size.grid(row=1, column=1)

    button = ttk.Button(layout, text="New Game", command=gui_process_new_game_input)
    button.grid(row=1, column=2, padx=5, pady=5)

    layout.pack()

    gui_new_window.configure(padx=10, pady=10)

    gui_new_window.focus_set()


def gui_main() -> None:
    """Alternative main loop for the GUI"""
    global gui_buttons, gui_world, gui_root, \
        gui_mines_left, gui_time_taken, gui_counting_time

    # Create the main window and run the event loop
    gui_root = tk.Tk()
    gui_root.geometry()
    gui_root.title('Minesweeper')

    # Create menu
    # Create main buttons
    buttons = ttk.Frame(gui_root)

    new_game_button = ttk.Button(buttons, text="New Game", command=gui_new_game_window)
    new_game_button.grid(column=0, row=0, pady=5)

    quit_button = ttk.Button(buttons, text="Quit", command=gui_root.quit)
    quit_button.grid(column=1, row=0)

    buttons.columnconfigure(0, pad=15)
    buttons.rowconfigure(1, pad=15)

    buttons.grid(row=2)

    # Create game timer and remaining mine count
    counts = ttk.Frame(gui_root)

    ttk.Label(counts, text="Timer").grid(column=0, row=0)

    gui_time_taken = ttk.Label(counts, text="0:00")
    gui_time_taken.grid(column=0, row=1)

    ttk.Label(counts, text="Mines Left").grid(column=1, row=0)

    gui_mines_left = ttk.Label(counts, text=str(mine_count))
    gui_mines_left.grid(column=1, row=1)

    counts.grid(row=3)

    # Create world
    gui_world = ttk.Frame(gui_root)
    gui_world.configure(padding=10)

    gui_new_game()

    gui_world.grid(row=4)

    gui_root.mainloop()

def process_square(world: World, square: str):
    if square in ["quit", "exit"]:
        return Constants.MENU_QUIT, False, 0, 0
    if square in ["display", "print"]:
        return Constants.MENU_DISPLAY, False, 0, 0
    if square == "color":
        return Constants.MENU_ENABLE_COLOR, False, 0, 0
    if square == "unicode":
        return Constants.MENU_ENABLE_UNICODE, False, 0, 0

    if len(square) < 2:
        return Constants.MENU_ERROR, False, 0, 0

    flagging = False
    x, y = 0, 0

    if not square[0].isalpha():
        print("Error: no valid letter found in square")
        return Constants.MENU_ERROR, False, 0, 0

    if square[1].isalpha():
        if square[0] == 'f':
            flagging = True
        else:
            # error
            return Constants.MENU_ERROR, False, 0, 0

        if not square[1].isalpha():
            print("Error: no valid letter found in square")
            return Constants.MENU_ERROR, False, 0, 0
        x = int(ord(square[1]) - ord('a'))
        if len(square) < 3:
            print("Error: no valid number found in square")
            return Constants.MENU_ERROR, False, 0, 0

        y = square[2:]
    else:
        x = int(ord(square[0]) - ord('a'))
        y = square[1:]

    if not y.isnumeric():
        print("Error: no valid number found in square")
        return Constants.MENU_ERROR, False, 0, 0

    y = int(y) - 1

    if not world.in_bounds(x, y):
        print("Error: square is not in world ({}, {})".format(x, y))
        return Constants.MENU_ERROR, False, 0, 0

    return 0, flagging, x, y

def get_input(world: World) -> tuple[int, bool, int, int]:
    ps = Constants.MENU_ERROR, False, 0, 0
    while ps[0] in [Constants.MENU_ERROR, Constants.MENU_QUIT, Constants.MENU_DISPLAY,
                        Constants.MENU_ENABLE_COLOR, Constants.MENU_ENABLE_UNICODE]:
        square = input("Enter a starting square to begin (type 'help' for help): ").lower()
        ps = process_square(world, square)
        if ps[0] == Constants.MENU_QUIT:
            print("Quitting...")
            return Constants.MENU_QUIT, False, 0, 0
        if ps[0] == Constants.MENU_HELP:
            print(Constants.MENU_HELP_STRING)
            continue
        if ps[0] == Constants.MENU_DISPLAY:
            if world.has_generated:
                world.display()
        if ps[0] == Constants.MENU_ENABLE_COLOR:
            world.use_color = True
        if ps[0] == Constants.MENU_ENABLE_UNICODE:
            world.use_unicode = True

    return ps[0], ps[1], ps[2], ps[3]

def main(args: list[str]) -> None:
    """Main function and entry point for the minesweeper program"""
    args = process_args(args)
    sys.setrecursionlimit(2 * args["world-size-x"] * args["world-size-y"])

    if args["use-gui"]:
        gui_main()  # start the GUI
        return

    # start console game
    print("Welcome to Minesweeper!")

    world = World(
        world_size_x=args["world-size-x"],
        world_size_y=args["world-size-y"],
        mine_count=args["mine-count"],
        use_color=args["use-color"],
        use_unicode=args["use-unicode"]
    )

    # get user input
    ps = get_input(world)
    while ps[1]:
        print("Can't flag on the first move!")
        ps = get_input(world)

    if ps[0] == Constants.MENU_QUIT:
        return

    world.generate((ps[2], ps[3]))

    # begin game loop
    while True:
        world.display()

        # get user input
        ps = get_input(world)
        if ps[0] == Constants.MENU_QUIT:
            return

        if ps[1]:  # flag
            world.flag_square(ps[2], ps[3])
        else:
            x = world.check_square(ps[2], ps[3])

            if x:
                print("Oh No! You hit a bomb!")
                world.display()
                world.display_all()
                print("Oh No! You hit a bomb!")
                print("You have lost!")
                break
        if world.check_win():
            print("Congrats! You win!")
            break

    finish_time = time.time() - world.start_time
    print(f"Finished in {round(finish_time)} seconds.")


if __name__ == '__main__':
    try:
        main(sys.argv)  # runs the program
    except KeyboardInterrupt:
        print("\n\nReceived KeyboardInterrupt")
        print("Quitting...")
        sys.exit(0)
