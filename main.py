import sys
import time
import random

alphabet = "abcdefghijklmnopqrstuvwxyz"
visible_world = []
world = []

mine_count = 25
world_size = 15


def alph_to_coord(letter):
    if isinstance(letter, str) or letter.isalpha():
        return int(ord(letter) - ord("a"))
    print("Internal Error! Bad string given!")
    sys.exit(1)


def print_world():
    if len(visible_world) > world_size or len(visible_world[1]) > world_size:
        return

    print("\n" * 15)  # add some space

    # print header
    print(" " * 4, end="")
    for letter in range(len(visible_world)):
        print(alphabet[letter], end=" ")
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
                print("X", end=" ")
            elif item == -1:  # -1 is flagged
                print("F", end=" ")
            elif item == 0:  # 0  means nothing
                print(" ", end=" ")
            else:  # Remaining items are numbers to print
                print(str(item), end=" ")
        print()
    print("Printed current field.", end="\n\n")


def validate(square, world_created):
    if (square[0] in "Ff") and (len(square) == 3 or len(square) == 4) and (not square[1].isnumeric()) and \
            world_created:  # flag a square
        if not square[1] in alphabet:
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

    if len(square) != 2 and len(square) != 3:
        return -1

    # check for letter
    if not square[0] in alphabet:
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
    global visible_world, world
    visible_world = [[-2 for _i in range(world_size)] for _j in range(world_size)]
    world = [[0 for _i in range(world_size)] for _j in range(world_size)]

    for i in range(mine_count):
        r = random.randint(0, world_size - 1)
        c = random.randint(0, world_size - 1)
        while c == starting_square[0] and r == starting_square[1]:
            r = random.randint(0, world_size - 1)
            c = random.randint(0, world_size - 1)

        world[r][c] = 1

    check(starting_square)


def flag(valid_square):
    global visible_world
    if visible_world[valid_square[1]][valid_square[2]] == -2:
        visible_world[valid_square[1]][valid_square[2]] = -1
        print(visible_world[valid_square[1]][valid_square[2]])
    elif visible_world[valid_square[1]][valid_square[2]] == -1:
        visible_world[valid_square[1]][valid_square[2]] = -2


def check(valid_square):
    global visible_world
    if visible_world[valid_square[0]][valid_square[1]] == -1:
        # square is flagged, ignore
        return False

    if world[valid_square[0]][valid_square[1]] == 1:
        return True

    bombs_nearby = 0
    if valid_square[0] > 0:
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
        if valid_square[0] > 0 and visible_world[valid_square[0] - 1][valid_square[1]] == -2:
            check((valid_square[0] - 1, valid_square[1]))  # top
        if valid_square[0] > 0 and valid_square[1] > 0 and \
                visible_world[valid_square[0] - 1][valid_square[1] - 1] == -2:
            check((valid_square[0] - 1, valid_square[1] - 1))  # top left
        if valid_square[0] > 0 and valid_square[1] < world_size - 1 and \
                visible_world[valid_square[0] - 1][valid_square[1] + 1] == -2:
            check((valid_square[0] - 1, valid_square[1] + 1))  # top right
        if valid_square[0] < world_size - 1 and visible_world[valid_square[0] + 1][valid_square[1]] == -2:
            check((valid_square[0] + 1, valid_square[1]))  # bottom
        if valid_square[0] < world_size - 1 and valid_square[1] > 0 and \
                visible_world[valid_square[0] + 1][valid_square[1] - 1] == -2:
            check((valid_square[0] + 1, valid_square[1] - 1))  # bottom left
        if valid_square[0] < world_size - 1 and valid_square[1] < world_size - 1 and \
                visible_world[valid_square[0] + 1][valid_square[1] + 1] == -2:
            check((valid_square[0] + 1, valid_square[1] + 1))  # bottom right
        if valid_square[1] > 0 and visible_world[valid_square[0]][valid_square[0] - 1] == -2:
            check((valid_square[0], valid_square[1] - 1))  # left
        if valid_square[1] < world_size - 1 and visible_world[valid_square[0]][valid_square[1] + 1] == -2:
            check((valid_square[0], valid_square[1] + 1))  # right

    return False


def win():
    for r, row in enumerate(world):
        for c, col in enumerate(row):
            if world[r][c] == 1 and not visible_world[r][c] == -1:
                return False
    return True


def main():
    global world, visible_world
    sys.setrecursionlimit(100 * world_size * world_size)
    start_time = time.time()

    # start game
    print("Welcome to Minesweeper!")
    square = input("Enter a starting square to begin: ").lower()
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
            x = check(validated_square)
            if x:
                print("Oh No! You hit a bomb!")
                break
        if win():
            print("Congrats! You win!")
            break

    finish_time = time.time() - start_time
    print(f"Finished in {finish_time}.")


if __name__ == '__main__':
    main()

