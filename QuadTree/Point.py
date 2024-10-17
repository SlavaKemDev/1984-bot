from typing import List


class Point:
    def __init__(self, coords: List[float]):
        self.coords = coords

    def size(self):
        return len(self.coords)

    def __str__(self):
        return str(self.coords)

    def __eq__(self, other):
        for i in range(len(self.coords)):
            if self[i] != other[i]:
                return False

        return True

    def __getitem__(self, item):
        return self.coords[item]

    def __setitem__(self, key, value):
        self.coords[key] = value

    def __add__(self, other):
        assert len(self.coords) == len(other)
        ans = [self[i] + other[i] for i in range(len(other))]

        return Point(ans)

    def __sub__(self, other):
        assert len(self.coords) == len(other.coords)
        ans = [self[i] - other[i] for i in range(len(other.coords))]

        return Point(ans)

    def length(self):
        ans = sum(map(lambda x: x ** 2, self.coords))
        return ans ** 0.5
