import unittest

from src.gacm.gate.core import matches, unsafe_path


class GatePathTests(unittest.TestCase):
    def test_star_does_not_cross_segments(self):
        self.assertTrue(matches("src/gacm/x.py", ["src/gacm/*.py"]))
        self.assertFalse(matches("src/gacm/deep/x.py", ["src/gacm/*.py"]))

    def test_traversal_and_absolute_paths_are_unsafe(self):
        for path in ("src/../.github/x.yml", "/tmp/x", "C:/tmp/x"):
            with self.subTest(path=path):
                self.assertTrue(unsafe_path(path))


if __name__ == "__main__":
    unittest.main()
