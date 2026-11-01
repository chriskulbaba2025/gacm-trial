import unittest

from src.gacm.gate.core import matches, tranche_id_from_trailers, unsafe_path


class GatePathTests(unittest.TestCase):
    def test_star_does_not_cross_segments(self):
        self.assertTrue(matches("src/gacm/x.py", ["src/gacm/*.py"]))
        self.assertFalse(matches("src/gacm/deep/x.py", ["src/gacm/*.py"]))

    def test_traversal_and_absolute_paths_are_unsafe(self):
        for path in ("src/../.github/x.yml", "/tmp/x", "C:/tmp/x"):
            with self.subTest(path=path):
                self.assertTrue(unsafe_path(path))

    def test_later_tranche_identity_comes_from_one_committed_trailer(self):
        self.assertEqual("MA-1B", tranche_id_from_trailers(["MA-1B"]))
        with self.assertRaisesRegex(ValueError, "MIXED_OR_MISMATCHED_TRAILER"):
            tranche_id_from_trailers(["MA-1A", "MA-1B"])


if __name__ == "__main__":
    unittest.main()
