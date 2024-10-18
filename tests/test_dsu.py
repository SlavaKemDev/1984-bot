import unittest
from DSU import DSU


class TestDSU(unittest.TestCase):
    def test_dsu(self):
        dsu = DSU(10)
        self.assertEqual(dsu.get(0), 0)
        dsu.union(0, 1)

        self.assertTrue(dsu.is_connected(0, 1))
        self.assertFalse(dsu.is_connected(0, 2))
        self.assertEqual(dsu.size(0), 2)


if __name__ == '__main__':
    unittest.main()
