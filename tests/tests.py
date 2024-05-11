"""Tests for the minesweeper game"""
import unittest
import main as minesweeper


class MinesweeperTest(unittest.TestCase):
    def test_alph_to_coord(self):
        """Test if the alph_to_coord function works"""
        for i in range(26):
            self.assertEqual(minesweeper.alph_to_coord(minesweeper.ALPHABET[i]), i)

    def test_validate(self):
        """Test if the validate function works"""
        minesweeper.world_size = 26
        self.assertEqual(minesweeper.validate("fa1", True), ("f", 0, 0))
        self.assertEqual(minesweeper.validate("faa1", True), -1)
        self.assertEqual(minesweeper.validate("fa10", True), ("f", 9, 0))
        self.assertEqual(minesweeper.validate("fa1", False), -1)
        self.assertEqual(minesweeper.validate("faa1", False), -1)
        self.assertEqual(minesweeper.validate("f10", False), (9, 5))
        for b in (True, False):
            self.assertEqual(minesweeper.validate("a1", b), (0, 0))
            self.assertEqual(minesweeper.validate("aa1", b), -1)
            self.assertEqual(minesweeper.validate("z1", b), (0, 25))
            self.assertEqual(minesweeper.validate("zaa", b), -1)
            self.assertEqual(minesweeper.validate("1z", b), -1)
            self.assertEqual(minesweeper.validate("1a", b), -1)
            self.assertEqual(minesweeper.validate("[1", b), -1)

    def test_create_world(self):
        """Test if the create world function works"""
        minesweeper.world_size = 26
        minesweeper.create_world((0, 0))
        self.assertEqual(minesweeper.world[0][0], 0)
        self.assertEqual(len(minesweeper.world), 26)
        self.assertEqual(len(minesweeper.world[1]), 26)
        self.assertEqual(len(minesweeper.visible_world), 26)
        self.assertEqual(len(minesweeper.visible_world[0]), 26)

    def test_flag(self):
        """Test if the flag function works"""
        minesweeper.world_size = 3
        minesweeper.mine_count = 8
        minesweeper.create_world((2, 2))

        minesweeper.flag(("f", 0, 0))

        self.assertEqual(minesweeper.visible_world[0][0], minesweeper.FLAG)

        minesweeper.flag(("f", 0, 0))

        self.assertEqual(minesweeper.visible_world[0][0], minesweeper.HIDDEN)

    def test_win(self):
        """Test if the game win check works"""
        minesweeper.world_size = 3
        minesweeper.mine_count = 9
        minesweeper.create_world((2, 2))

        self.assertEqual(minesweeper.win(), False)

        for i in range(3):
            for j in range(3):
                if i == 2 and j == 2:
                    pass
                minesweeper.flag(("f", i, j))

        self.assertEqual(minesweeper.win(), True)


if __name__ == '__main__':
    unittest.main()
