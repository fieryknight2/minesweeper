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
import os
import json

enable_gui: bool = True
try:
    import PyQt6
except ImportError:
    enable_gui = False


class Settings:
    Preferences = {}

    @staticmethod
    def LoadPreferences(path):
        """Load preferences from a JSON file, only do this before creating a world"""
        if os.path.isfile(path):
            try:
                with open(path, "r") as file:
                    data = json.load(file)
                    preferences = data
                    for key in data.keys():
                        match key:
                            case "constants":
                                if "MAX_GUI_WORLD_SIZE" in data[key].keys():
                                    Settings.MaxGuiWorldSize = data[key]["MAX_GUI_WORLD_SIZE"]
                            case "game_symbols":
                                if "flag" in data[key].keys():
                                    Settings.Flag = data[key]["flag"]
                                if "hidden" in data[key].keys():
                                    Settings.Hidden = data[key]["hidden"]
                                if "bomb" in data[key].keys():
                                    Settings.Bomb = data[key]["bomb"]
                                if "bad_flag" in data[key].keys():
                                    Settings.BadFlag = data[key]["bad_flag"]
                                if "empty" in data[key].keys():
                                    Settings.Empty = data[key]["empty"]
                            case "unicode_characters":
                                if "flag" in data[key].keys():
                                    Settings.CharacterUnicode[Settings.Flag] = data[key]["flag"]
                                if "hidden" in data[key].keys():
                                    Settings.CharacterUnicode[Settings.Hidden] = data[key]["hidden"]
                                if "bomb" in data[key].keys():
                                    Settings.CharacterUnicode[Settings.Bomb] = data[key]["bomb"]
                                if "bad_flag" in data[key].keys():
                                    Settings.CharacterUnicode[Settings.BadFlag] = data[key]["bad_flag"]
                            case "defaults":
                                if "use_color" in data[key].keys():
                                    Settings.DefaultUseColor = data[key]["use_color"]
                                if "use_unicode" in data[key].keys():
                                    Settings.DefaultUseUnicode = data[key]["use_unicode"]

            except Exception as e:
                print("Failed to load prefences file:", e)

    @staticmethod
    def PrintHelp():
        print(Settings.MENU_HELP_STRING.format(bomb=Settings.Bomb,
                                               hidden=Settings.Hidden,
                                               flag=Settings.Flag,
                                               wrong_flag=Settings.BadFlag))

    MaxGuiWorldSize = 50

    Flag = 'F'
    Hidden = '#'
    Bomb = 'B'
    BadFlag = 'L'
    Empty = '.'

    DefaultUseColor = True
    DefaultUseUnicode = False

    MENU_QUIT = 1
    MENU_DISPLAY = 2
    MENU_ERROR = 3
    MENU_HELP = 4
    MENU_ENABLE_COLOR = 5
    MENU_ENABLE_UNICODE = 6

    CharacterUnicode = {
        Bomb: "\u2620",
        Flag: "\u2691",
        Hidden: "\u25A0",
        BadFlag: "\u2690",
        ' ': '',
    }

    CharacterColor = {
        Bomb: "\033[31m",  # red
        Flag: "\033[32m",  # green
        BadFlag: "\033[35m",  # pink
        Hidden: "\033[34m",  # blue
        # utility
        ' ': '',
        "reset": "\033[0m",
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
        - Bomb: {bomb}
        - Hidden: {hidden}
        - Flag: {flag}
        - Wrong Flag: {wrong_flag}
"""

class World:
    MAX_WORLD_SIZE_X = 52
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

        self.use_color = Settings.DefaultUseColor if "use_color" not in kwargs.keys() else kwargs["use_color"]
        self.use_unicode = Settings.DefaultUseUnicode if "use_unicode" not in kwargs.keys() else kwargs["use_unicode"]

        self.display_empty = False if "display_empty" not in kwargs.keys() else kwargs["display_empty"]

        self.start_time = 0
        self.paused_for = 0

        self.preferences = {}

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
        self.visible = [[Settings.Hidden for _ in range(self.world_size_x)] for _ in range(self.world_size_y)]

        # Ensure start square does not have a mine on it
        if start_square:
            self.mines[start_square[1]][start_square[0]] = True

        for _ in range(self.mine_count):
            x, y = random.randint(0, self.world_size_x - 1), random.randint(0, self.world_size_y - 1)
            while self.mines[y][x]:
                x, y = random.randint(0, self.world_size_x - 1), random.randint(0, self.world_size_y - 1)

            self.mines[y][x] = True

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
            elif i < 52:
                print(f" {chr(i - 26 + ord('A'))}", end="")
            else:
                pass

        print()
        for y in range(self.world_size_y):
            print(f"{y + 1:2}", end="")
            for x in range(self.world_size_x):
                dp_value = self.visible[y][x]

                if self.use_color and not (dp_value.isnumeric() or dp_value == Settings.Empty):
                    print(Settings.CharacterColor[dp_value], end="")

                if self.use_unicode and not (dp_value.isnumeric() or dp_value == Settings.Empty):
                    dp_value = Settings.CharacterUnicode[dp_value]

                if dp_value == Settings.Empty and not self.display_empty:
                    dp_value = ' '


                print(f" {dp_value}", end="")

                if self.use_color:
                    print(Settings.CharacterColor["reset"], end="")
            print()

        print()

    def display_all(self):
        vis = self.visible
        for x in range(self.world_size_x):
            for y in range(self.world_size_y):
                self.check_square(x, y)

                if self.visible[y][x] == Settings.Flag and not self.mines[y][x]:
                    self.visible[y][x] = Settings.BadFlag

        self.display()

        self.visible = vis

    def check_square(self, x: int, y: int) -> bool:
        """Check the given square for mines and clear it on the visible plane. Ignores flagged squares"""
        if not self.in_bounds(x, y):
            return False

        if self.visible[y][x] in [Settings.Flag, Settings.Empty]:
            return False

        if self.visible[y][x] == Settings.Hidden:
            if self.mines[y][x]:
                self.visible[y][x] = Settings.Bomb
                return True

            count = self.count_nearby(x, y, Settings.Bomb)

            if count == 0:
                self.visible[y][x] = Settings.Empty
                for X in range(x - 1, x + 2):
                    for Y in range(y - 1, y + 2):
                        if (X == x and Y == y) or not self.in_bounds(X, Y):
                            continue

                        if self.visible[Y][X] == Settings.Hidden:
                            self.check_square(X, Y)
            else:
                self.visible[y][x] = str(count)

        elif self.visible[y][x].isnumeric():
            if self.count_nearby(x, y, Settings.Flag) == int(self.visible[y][x]):
                for X in range(x - 1, x + 2):
                    for Y in range(y - 1, y + 2):
                        if (X == x and Y == y) or not self.in_bounds(X, Y):
                            continue

                        if self.visible[Y][X] == Settings.Hidden:
                            if self.check_square(X, Y):
                                return True

        return False

    def flag_square(self, x: int, y: int) -> None:
        """Toggle flag on the given square for mines"""
        if self.visible[y][x] == Settings.Flag:
            self.visible[y][x] = Settings.Hidden
        elif self.visible[y][x] == Settings.Hidden:
            self.visible[y][x] = Settings.Flag

    def check_win(self) -> bool:
        for x in range(self.world_size_x):
            for y in range(self.world_size_y):
                if self.visible[y][x] == Settings.Hidden and not self.mines[y][x]:
                    return False

        return True

    def count_unflagged_mines(self) -> int:
        count = 0
        for x in range(self.world_size_x):
            for y in range(self.world_size_y):
                if self.mines[y][x] and self.visible[y][x] != Settings.Flag:
                    count += 1

        return count

    def count_nearby(self, x: int, y: int, value: str) -> int:
        count = 0
        for X in range(x - 1, x + 2):
            for Y in range(y - 1, y + 2):
                if self.in_bounds(X, Y) and not (X == x and Y == y):
                    match value:
                        case Settings.Flag:
                            count += self.visible[Y][X] == Settings.Flag
                        case Settings.Bomb:
                            count += self.mines[Y][X]

        return count

    def in_bounds(self, x, y):
        return self.world_size_x > x >= 0 and self.world_size_y > y >= 0

if enable_gui:
    from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QDialogButtonBox, QSlider, QWidget
    from PyQt6.QtWidgets import QVBoxLayout, QDialog, QHBoxLayout, QGridLayout, QVBoxLayout, QMessageBox, QSpinBox
    from PyQt6.QtCore import QTimer, Qt, QObject, QEvent
    from PyQt6.QtGui import QPalette

    class GButton(QLabel):
        pressPosR = None
        pressPosL = None

        styleSheet = """
*[theme="dark"] {
    background-color: #2c2c2c;
    color: #eee;
    border: 1px solid #444;
}

*[theme="dark-disabled"] {
    background-color: #1e1e1e;
    color: #eee;
    border: 1px solid #333;
}

*[theme="light"] {
    background-color: #f7f7f7;
    color: #1e1e1e;
    border: 1px solid #b5b5b5;
}

*[theme="light-disabled"] {
    background-color: #ececec;
    color: #666666;
    border: 1px solid #cccccc;
}

*[warning="true"] {
    background-color: #ffdddd;
    color: #b00020;
    border: 1px solid #b00020;               
}
"""

        def __init__(self, theme=False, text=""):
            super().__init__(text)

            self.right_click_action = None
            self.left_click_action = None

            self.theme = theme
            self.warning = False
            self.revealed = False

            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setStyleSheet(self.styleSheet)
            self.setProperty("theme", "dark" if self.theme else "light")

        def mousePressEvent(self, e):
            if e.button() == Qt.MouseButton.RightButton:
                self.pressPosR = e.pos()
            elif e.button() == Qt.MouseButton.LeftButton:
                self.pressPosL = e.pos()

        def mouseReleaseEvent(self, e):
            if e.button() == Qt.MouseButton.RightButton and self.pressPosR is not None and e.pos() in self.rect():
                self.right_click_action()
            if e.button() == Qt.MouseButton.LeftButton and self.pressPosL is not None and e.pos() in self.rect():
                self.left_click_action()

            self.pressPosR = None
            self.pressPosL = None

        def reveal(self):
            self.revealed = True
            self.setProperty("theme", "dark-disabled" if self.theme else "light-disabled")
            self.style().unpolish(self)
            self.style().polish(self)

        def set_warning(self, value: bool):
            if self.warning == value:
                return

            self.warning = value
            self.setProperty("warning", "true" if value else "false")

            self.style().unpolish(self)
            self.style().polish(self)

        def change_theme(self, dark: bool):
            if self.theme == dark:
                return
            self.theme = dark

            theme_base = "dark" if dark else "light"
            theme_suffix = "-disabled" if self.revealed else ""
            self.setProperty("theme", theme_base + theme_suffix)

            self.style().unpolish(self)
            self.style().polish(self)

    class GUIWindow(QMainWindow):
        """GUI window for the minesweeper game"""
        def __init__(self, theme=False):
            super().__init__()

            self.setWindowTitle("Minesweeper")

            self.buttons = []

            self.theme = theme

            self.lose_message = None
            self.win_message = None
            self.time_taken = None
            self.mines_left = None

            self.root = None
            self.button_grid = None

        def update_theme(self, dark: bool):
            self.theme = dark

            for y in range(len(self.buttons)):
                for x in range(len(self.buttons[y])):
                    self.buttons[y][x].change_theme(dark)

        def create_layout(self, new_game_window, quit_action):
            self.root = QVBoxLayout()
            buttons = QHBoxLayout()

            new_game = QPushButton("New Game")
            new_game.clicked.connect(new_game_window)
            buttons.addWidget(new_game)

            quit_button = QPushButton("Quit")
            quit_button.clicked.connect(quit_action)
            buttons.addWidget(quit_button)

            info = QGridLayout()
            info.setAlignment(Qt.AlignmentFlag.AlignTop)

            info.addWidget(QLabel("Timer"), 0, 0)
            info.addWidget(QLabel("Mines Left"), 1, 0)

            self.time_taken = QLabel("0:00:00")
            self.mines_left = QLabel("0")

            info.addWidget(self.time_taken, 0, 1)
            info.addWidget(self.mines_left, 1, 1)

            self.button_grid = QGridLayout()

            self.root.addLayout(buttons)
            self.root.addLayout(info)
            self.root.addLayout(self.button_grid)

            root_widget = QWidget()
            root_widget.setLayout(self.root)
            self.setCentralWidget(root_widget)

        def create_buttons(self, world):
            if self.button_grid is not None:
                self.root.removeItem(self.button_grid)
                while self.button_grid.count():
                    item = self.button_grid.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                self.button_grid.deleteLater()
                self.button_grid = None

            self.button_grid = QGridLayout()
            self.button_grid.setSpacing(1)
            self.button_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.root.addLayout(self.button_grid)

            self.buttons.clear()
            for y in range(world.world_size_y):
                self.buttons.append([])
                for x in range(world.world_size_x):
                    self.buttons[y].append(GButton(self.theme, ""))
                    self.buttons[y][x].setFixedSize(20, 20)
                    self.button_grid.addWidget(self.buttons[y][x], y, x)

        def show_lose(self):
            pass

        def show_win(self):
            pass

    class NewGameDialog(QDialog):
        def __init__(self, parent, world, accept):
            super().__init__(parent)
            self.setWindowTitle("New Game")

            self.mine_count = 10
            self.world_size_x = 9
            self.world_size_y = 9

            vlayout = QVBoxLayout()

            # noinspection PyTypeChecker
            qbtn = QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
            self.buttonBox = QDialogButtonBox(qbtn)
            self.buttonBox.accepted.connect(accept)
            self.buttonBox.rejected.connect(lambda: self.close())

            self.message = QLabel("Choose the size of the world and the number of mines.")
            vlayout.addWidget(self.message)

            self.error = QLabel("Too many mines for the world size!")
            self.error.setStyleSheet("QLabel { color: red; }")
            self.error.hide()
            vlayout.addWidget(self.error)

            layout = QGridLayout()

            self.mine_count = world.mine_count
            self.gui_mine_count = QSlider(Qt.Orientation.Horizontal)
            self.gui_mine_count.setValue(self.mine_count)
            self.gui_mine_count.setRange(10,int(Settings.MaxGuiWorldSize*Settings.MaxGuiWorldSize*0.3))
            self.gui_mine_count.valueChanged.connect(self.update_mine_count)
            self.gui_mine_countv = QSpinBox()
            self.gui_mine_countv.setValue(self.mine_count)
            self.gui_mine_countv.setRange(10,int(Settings.MaxGuiWorldSize*Settings.MaxGuiWorldSize*0.3))
            self.gui_mine_countv.valueChanged.connect(self.update_mine_count)
            self.gui_mine_countv.setMinimumWidth(30)

            self.world_size_x = world.world_size_x
            self.gui_world_size_x = QSlider(Qt.Orientation.Horizontal)
            self.gui_world_size_x.setValue(self.world_size_x)
            self.gui_world_size_x.setRange(3, Settings.MaxGuiWorldSize)
            self.gui_world_size_x.valueChanged.connect(self.update_world_size_x)
            self.gui_world_sizev_x = QSpinBox()
            self.gui_world_sizev_x.setValue(self.world_size_x)
            self.gui_world_sizev_x.setRange(3, Settings.MaxGuiWorldSize)
            self.gui_world_sizev_x.valueChanged.connect(self.update_world_size_x)
            self.gui_world_sizev_x.setMinimumWidth(30)

            self.world_size_y = world.world_size_y
            self.gui_world_size_y = QSlider(Qt.Orientation.Horizontal)
            self.gui_world_size_y.setValue(self.world_size_y)
            self.gui_world_size_y.setRange(3, Settings.MaxGuiWorldSize)
            self.gui_world_size_y.valueChanged.connect(self.update_world_size_y)
            self.gui_world_sizev_y = QSpinBox()
            self.gui_world_sizev_y.setValue(self.world_size_y)
            self.gui_world_sizev_y.setRange(3, Settings.MaxGuiWorldSize)
            self.gui_world_sizev_y.valueChanged.connect(self.update_world_size_y)
            self.gui_world_sizev_y.setMinimumWidth(30)

            layout.addWidget(QLabel("Mine Count"), 0, 0)
            layout.addWidget(self.gui_mine_count, 0, 1)
            layout.addWidget(self.gui_mine_countv, 0, 3)
            layout.addWidget(QLabel("World Width"), 1, 0)
            layout.addWidget(self.gui_world_size_x, 1, 1)
            layout.addWidget(self.gui_world_sizev_x, 1, 3)
            layout.addWidget(QLabel("World Height"), 2, 0)
            layout.addWidget(self.gui_world_size_y, 2, 1)
            layout.addWidget(self.gui_world_sizev_y, 2, 3)

            vlayout.addLayout(layout)
            vlayout.addWidget(self.buttonBox)

            self.setLayout(vlayout)

        def update_errors(self):
            if self.mine_count > self.world_size_x * self.world_size_y / 3:
                self.buttonBox.setDisabled(True)
                self.error.show()
            else:
                self.buttonBox.setDisabled(False)
                self.error.hide()

        def update_mine_count(self, value):
            self.mine_count = value
            self.gui_mine_countv.setValue(value)
            self.gui_mine_count.setValue(value)

            self.update_errors()

        def update_world_size_x(self, value):
            self.world_size_x = value
            self.gui_world_sizev_x.setValue(value)
            self.gui_world_size_x.setValue(value)

            self.update_errors()

        def update_world_size_y(self, value):
            self.world_size_y = value
            self.gui_world_sizev_y.setValue(value)
            self.gui_world_size_y.setValue(value)

            self.update_errors()

    class ErrorDialog(QDialog):
        def __init__(self, parent, message):
            super().__init__()
            self.setWindowTitle("Error")

            vlayout = QVBoxLayout()
            label = QLabel(message)
            vlayout.addWidget(label)

            qbtn = QDialogButtonBox.StandardButton.Ok
            button_box = QDialogButtonBox(qbtn)
            button_box.accepted.connect(self.accept)
            vlayout.addWidget(button_box)

            self.setLayout(vlayout)
            self.exec()

        def accept(self):
            self.close()

    class ThemeWatcher(QObject):
        """Class to watch for theme changes and update the GUI"""
        def __init__(self, gui, action=None):
            super().__init__()
            self.gui = gui
            self.last_theme = self.detect_theme()
            self.action = action

        def detect_theme(self) -> bool:
            """Detect the current theme"""
            palette = self.gui.application.palette()
            bg = palette.color(QPalette.ColorRole.Window)
            brightness = bg.value()
            return brightness < 128

        def eventFilter(self, obj: QObject, event: QEvent) -> bool:
            if event.type() == QEvent.Type.ApplicationPaletteChange:
                new_theme = self.detect_theme()
                if new_theme != self.last_theme:
                    self.last_theme = new_theme
                    if self.action is not None:
                        self.action(new_theme)
            return super().eventFilter(obj, event)

    class GUI:
        """GUI for the minesweeper game"""
        def __init__(self):
            super().__init__()
            self.world = World()

            self.application = None
            self.gui_window = None
            self.new_game_window = None
            self.eventFilter = None

            self.counting_time = False
            self.lose_state: bool = False
            self.win_state: bool = False

            self.world_size_x = 9
            self.world_size_y = 9
            self.mine_count = 10

        def new_game(self) -> None:
            """Create a new game"""
            self.counting_time = False

            self.gui_window.hide()
            self.world = World()
            self.world.world_size_y = self.world_size_y
            self.world.world_size_x = self.world_size_x
            self.world.mine_count = self.mine_count
            sys.setrecursionlimit(4 * self.world_size_y * self.world_size_x)

            self.gui_window.create_buttons(self.world)
            self.gui_window.mines_left.setText(str(self.world.mine_count))
            self.gui_window.layout().update()
            self.gui_window.show()

            for y in range(self.world.world_size_y):
                for x in range(self.world.world_size_x):
                    self.gui_window.buttons[y][x].left_click_action = lambda a=x, b=y: self.click(a, b)
                    self.gui_window.buttons[y][x].right_click_action = lambda a=x, b=y: self.flag(a, b)

            self.lose_state = False

        def lose(self) -> None:
            """Display a message to the user that they lost"""
            self.gui_window.show_lose()

            self.lose_state = True
            self.update_gui()

            self.counting_time = False

            dlg = QMessageBox()
            dlg.setWindowTitle("Game Over")
            dlg.setText("You Lost!")
            dlg.setIcon(QMessageBox.Icon.Critical)
            dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
            dlg.exec()

        def win(self) -> None:
            """Display a message to the user that they won"""
            self.gui_window.show_win()
            self.counting_time = False
            self.win_state = True

            for x in range(self.world.world_size_x):
                for y in range(self.world.world_size_y):
                    if self.world.visible[y][x] == Settings.Hidden:
                        self.world.flag_square(x, y)
            self.update_gui()

            dlg = QMessageBox()
            dlg.setWindowTitle("Congratulations!")
            dlg.setText("You Win!")
            dlg.setIcon(QMessageBox.Icon.Information)
            dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
            dlg.exec()

        def update_gui(self) -> None:
            """Update the GUI"""
            for y in range(self.world.world_size_y):
                for x in range(self.world.world_size_x):
                    if self.world.visible[y][x] not in [Settings.Hidden, Settings.Flag]:
                        self.gui_window.buttons[y][x].reveal()

                    if self.world.visible[y][x].isnumeric():
                        self.gui_window.buttons[y][x].setText(self.world.visible[y][x])
                        self.gui_window.buttons[y][x].set_warning(self.world.count_nearby(x, y, Settings.Flag) > int(self.world.visible[y][x]))
                        continue

                    match self.world.visible[y][x]:
                        case Settings.Hidden:
                            self.gui_window.buttons[y][x].setText("")
                        case Settings.Flag:
                            self.gui_window.buttons[y][x].setText(Settings.CharacterUnicode[Settings.Flag])
                        case Settings.Bomb:
                            pass
                        case Settings.Empty:
                            self.gui_window.buttons[y][x].setText("")
                        case _:
                            self.gui_window.buttons[y][x].setText(str(self.world.visible[y][y]))

                    if self.lose_state:
                        value = self.world.visible[y][x]
                        if value == Settings.Empty:
                            value = ' '
                        elif value == Settings.Flag:
                            if self.world.mines[y][x]:
                                value = Settings.CharacterUnicode[Settings.Flag]
                            else:
                                value = Settings.CharacterUnicode[Settings.BadFlag]
                        elif value == Settings.Hidden and self.world.mines[y][x]:
                            value = Settings.CharacterUnicode[Settings.Bomb]
                            self.gui_window.buttons[y][x].reveal()
                        elif value == Settings.Bomb:
                            value = Settings.CharacterUnicode[Settings.Bomb]
                            self.gui_window.buttons[y][x].reveal()
                        elif value == Settings.Hidden:
                            value = ' '
                        else:
                            value = self.world.visible[y][x]

                        self.gui_window.buttons[y][x].setText(value)
                        self.gui_window.buttons[y][x].setDisabled(True)

            # self.world.display()
            self.gui_window.mines_left.setText(str(self.world.count_unflagged_mines()))

        def update_time(self) -> None:
            """Update the GUI timer"""
            if self.counting_time:
                seconds = round(time.time() - self.world.start_time)
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)
                self.gui_window.time_taken.setText(f"{str(hours)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}")

                QTimer.singleShot(1, self.update_time)

        def click(self, x: int, y: int) -> None:
            """Click a tile"""
            # Initialize the world if it hasn't been initialized yet
            if not self.world.has_generated:
                self.world.generate((x, y))
                self.counting_time = True
                self.win_state = False
                self.update_gui()
                self.update_time()
                return

            if self.win_state:
                return

            if self.world.check_square(x, y):
                self.lose()
                return

            self.update_gui()  # update the GUI

            if self.world.check_win():
                self.win()

        def flag(self, x: int, y: int) -> None:
            """Flag a tile"""
            if self.win_state or not self.world.has_generated:
                # player can't flag a tile until the world has generated
                return

            self.world.flag_square(x, y)
            self.update_gui()

        def process_new_game_input(self) -> None:
            """Process the new game input"""
            self.mine_count = self.new_game_window.mine_count
            self.world_size_x = self.new_game_window.world_size_x
            self.world_size_y = self.new_game_window.world_size_y
            self.new_game_window.close()
            self.new_game_window = None
            self.win_state = False

            self.new_game()

        def new_game_dialog(self) -> None:
            """Create a new game window"""
            self.new_game_window = NewGameDialog(self.gui_window, self.world, self.process_new_game_input)
            self.new_game_window.exec()

        def on_quit(self) -> None:
            self.application.quit()

        def main(self) -> None:
            """Alternative main loop for the GUI"""
            self.application = QApplication([])
            self.gui_window = GUIWindow()
            self.gui_window.create_layout(self.new_game_dialog, self.on_quit)
            self.eventFilter = ThemeWatcher(self, self.gui_window.update_theme)
            self.application.installEventFilter(self.eventFilter)

            self.eventFilter.detect_theme()
            self.gui_window.update_theme(self.eventFilter.last_theme)

            self.new_game()

            self.gui_window.show()
            self.application.exec()

def process_args() -> dict:
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
    parser.add_argument("--preferences", help="Describe alternate preferences file path", type=str)

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
        "use-gui": args.use_gui,
        "preferences": args.preferences if args.preferences else "prefs.json",
    }

def process_square(world: World, square: str):
    flagging = False
    x, y = 0, 0

    match square.lower():
        case "quit" | "exit":
            return Settings.MENU_QUIT, False, 0, 0
        case "display" | "print":
            return Settings.MENU_DISPLAY, False, 0,
        case "help":
            return Settings.MENU_HELP, False, 0, 0
        case "color":
            return Settings.MENU_ENABLE_COLOR, False, 0, 0
        case "unicode":
            return Settings.MENU_ENABLE_UNICODE, False, 0, 0

    if len(square) < 2 or not square[0].isalpha():
        return Settings.MENU_ERROR, False, 0, 0

    alpha_loc = 0
    if square[1].isalpha():
        if square[0] != 'f':
            return Settings.MENU_ERROR, False, 0, 0

        flagging = True

        if not square[1].isalpha() or len(square) < 3:
            print("Error: Invalid location")
            return Settings.MENU_ERROR, False, 0, 0

        alpha_loc = 1
        y = square[2:]
    else:
        alpha_loc = 0
        y = square[1:]

    if ord(square[alpha_loc]) >= ord('a'):
        x = int(ord(square[alpha_loc]) - ord('a'))
    else:
        x = int(ord(square[alpha_loc]) - ord('A')) + 26

    if not y.isnumeric():
        print("Error: no valid number found in square")
        return Settings.MENU_ERROR, False, 0, 0
    y = int(y) - 1

    if not world.in_bounds(x, y):
        print("Error: square is not in world ({}, {})".format(x, y))
        return Settings.MENU_ERROR, False, 0, 0

    return 0, flagging, x, y

def get_input(world: World) -> tuple[int, bool, int, int]:
    ps = [-1]
    while ps[0] != 0:
        square = input("Enter a starting square to begin (type 'help' for help): ")
        ps = process_square(world, square)
        match ps[0]:
            case Settings.MENU_QUIT:
                print("Quitting...")
                return Settings.MENU_QUIT, False, 0, 0
            case Settings.MENU_HELP:
                Settings.PrintHelp()
            case Settings.MENU_DISPLAY:
                if world.has_generated:
                    world.display()
            case Settings.MENU_ENABLE_COLOR:
                world.use_color = not world.use_color
            case Settings.MENU_ENABLE_UNICODE:
                world.use_unicode = not world.use_unicode
            case _:
                pass

    return ps[0], ps[1], ps[2], ps[3]

def main() -> None:
    """Main function and entry point for the minesweeper program"""
    args = process_args()
    sys.setrecursionlimit(4 * args["world-size-x"] * args["world-size-y"])

    Settings.LoadPreferences(args["preferences"])

    if args["use-gui"] :
        if enable_gui:
            gui = GUI()
            gui.main()  # start the GUI
            return
        else:
            print("GUI not available. Please install PyQt6.")
            return

    # start console game
    print("Welcome to Minesweeper!")

    world = World(
        world_size_x=args["world-size-x"],
        world_size_y=args["world-size-y"],
        mine_count=args["mine-count"],
        use_color=True if args["use-color"] or Settings.DefaultUseColor else False,
        use_unicode=True if args["use-unicode"] or Settings.DefaultUseUnicode else False,
    )

    # get user input
    ps = get_input(world)
    while ps[1]:
        print("Can't flag on the first move!")
        ps = get_input(world)

    if ps[0] == Settings.MENU_QUIT:
        return

    world.generate((ps[2], ps[3]))

    # begin game loop
    while True:
        world.display()

        # get user input
        ps = get_input(world)
        if ps[0] == Settings.MENU_QUIT:
            return

        if ps[1]:  # flag
            world.flag_square(ps[2], ps[3])
        else:
            x = world.check_square(ps[2], ps[3])

            if x:
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
        main()  # runs the program
    except KeyboardInterrupt:
        print("\n\nReceived KeyboardInterrupt")
        print("Quitting...")
        sys.exit(0)
