import random
import time
import unittest
from QuadTree import QuadTree, Point


class TestQuadTree(unittest.TestCase):
    def test_base_cases(self):
        tree = QuadTree(Point([0, 0]), Point([10, 10]))

        tree.add_point(Point([1, 1]), 1)
        tree.add_point(Point([2, 2]), 2)

        self.assertEqual(tree.find_nearest(Point([1, 1])).point, Point([1, 1]))
        self.assertEqual(tree.find_nearest(Point([2, 2])).point, Point([2, 2]))

    def test_data_storage(self):
        tree = QuadTree(Point([0, 0]), Point([10, 10]))

        tree.add_point(Point([1, 1]), 1)
        tree.add_point(Point([2, 2]), 2)

        self.assertEqual(tree.find_nearest(Point([1, 1])).data, 1)

    def test_random(self):
        for dim in [2, 3, 4, 5, 100]:
            self.random_with_params(dim, 10000, 10)

    def random_with_params(self, dim: int, objects: int, queries: int):
        print(f"Testing dim = {dim}")
        qt = QuadTree(Point([0] * dim), Point([10] * dim))

        p = []

        error_sum = 0
        tree_time = 0
        brute_time = 0

        for i in range(objects):
            pt = Point([10 * random.random() for _ in range(dim)])
            p.append(pt)

            qt.add_point(pt, random.randint(1, 10000000))

        for _ in range(queries):
            need = Point([10 * random.random() for _ in range(dim)])

            # print(f"Solving {need}")

            tm1 = time.perf_counter()
            pt = qt.find_nearest(need).point
            tm2 = time.perf_counter()

            tm3 = time.perf_counter()
            best = p[0]
            for x in p:
                if (x - need).length() < (best - need).length():
                    best = x
            tm4 = time.perf_counter()

            pt_dist = (pt - need).length()
            best_dist = (best - need).length()

            # print("Found: ", pt, "->", pt_dist, "| time =", tm2 - tm1, "s")
            # print("Best: ", best, "->", best_dist, "| time =", tm4 - tm3, "s")
            error_sum += pt_dist / best_dist
            tree_time += tm2 - tm1
            brute_time += tm4 - tm3

        print(f"error: {error_sum / queries}")
        print(f"tree_time: {tree_time / queries}")
        print(f"brute_time: {brute_time / queries}")
        print()

        self.assertLess(error_sum / queries, 2 * (2 ** 0.5))


if __name__ == '__main__':
    unittest.main()
