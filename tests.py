"""Tests for the minesweeper game"""
import main as minesweeper


def test_alph_to_coord():
    """Test if the alph_to_coord function works"""
    for i in range(26):
        assert minesweeper.alph_to_coord(minesweeper.ALPHABET[i]) == i, "Alphabet to coords test failed."


def test_validate():
    """Test if the validate function works"""
    minesweeper.world_size = 26
    assert minesweeper.validate("fa1", True) == ("f", 0, 0), "Square validation failed"
    assert minesweeper.validate("faa1", True) == -1, "Square validation failed"
    assert minesweeper.validate("fa10", True) == ("f", 9, 0), "Square validation failed"
    assert minesweeper.validate("fa1", False) == -1, "Square validation failed"
    assert minesweeper.validate("faa1", False) == -1, "Square validation failed"
    assert minesweeper.validate("f10", False) == (9, 5), "Square validation failed"

    for b in (True, False):
        assert minesweeper.validate("a1", b) == (0, 0), "Square validation failed"
        assert minesweeper.validate("aa1", b) == -1, "Square validation failed"
        assert minesweeper.validate("z1", b) == (0, 25), "Square validation failed"
        assert minesweeper.validate("zaa", b) == -1, "Square validation failed"
        assert minesweeper.validate("1z", b) == -1, "Square validation failed"
        assert minesweeper.validate("1a", b) == -1, "Square validation failed"
        assert minesweeper.validate("[1", b) == -1, "Square validation failed"


def test_create_world():
    """Test if the create world function works"""
    minesweeper.world_size = 26
    minesweeper.create_world((0, 0))

    assert minesweeper.world[0][0] == 0, "World creation test failed"
    assert len(minesweeper.world) == 26, "World creation test failed"
    assert len(minesweeper.world[1]) == 26, "World creation test failed"
    assert len(minesweeper.visible_world) == 26, "World creation test failed"
    assert len(minesweeper.visible_world[0]) == 26, "World creation test failed"


def test_flag():
    """Test if the flag function works"""
    minesweeper.world_size = 3
    minesweeper.mine_count = 8
    minesweeper.create_world((2, 2))

    minesweeper.flag(("f", 0, 0))

    assert minesweeper.visible_world[0][0] == minesweeper.FLAG, "Flagging test failed"

    minesweeper.flag(("f", 0, 0))

    assert minesweeper.visible_world[0][0] == minesweeper.HIDDEN, "Flagging test failed"


def test_win():
    """Test if the game win check works"""
    minesweeper.world_size = 4
    minesweeper.mine_count = 15
    minesweeper.create_world((0, 0))

    assert minesweeper.win() is False, "Win check test failed"

    for i in range(3):
        for j in range(3):
            if i == 0 and j == 0:
                pass
            minesweeper.flag(("f", i, j))

    assert minesweeper.win() is True, "Win check test failed"

    minesweeper.flag(("f", 0, 0))
    minesweeper.flag(("f", 2, 2))
    assert minesweeper.win() is True, "Win check test failed"
