import unittest
from DSU import DSU


class TestDSU(unittest.TestCase):
    def test_dsu(self):
        dsu = DSU()
        for i in range(10):
            dsu.add_vertex(i)

        self.assertEqual(dsu.get(0), 0)
        dsu.union(0, 1)

        self.assertTrue(dsu.is_connected(0, 1))
        self.assertFalse(dsu.is_connected(0, 2))
        self.assertEqual(dsu.size(0), 2)

        vert = dsu.add_vertex(10)

        dsu.union(0, vert)

        self.assertTrue(dsu.is_connected(0, vert))
        self.assertTrue(dsu.is_connected(1, vert))
        self.assertEqual(dsu.size(0), 3)


if __name__ == '__main__':
    unittest.main()
