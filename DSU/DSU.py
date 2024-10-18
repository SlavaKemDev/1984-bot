from sortedcontainers import SortedSet
from typing import Any


class DSU:
    def __init__(self):
        self._parent: list[int] = []
        self._elements: list[SortedSet] = []

    def find(self, v: int) -> int:
        if v == self._parent[v]:
            return v

        self._parent[v] = self.find(self._parent[v])
        return self._parent[v]

    def union(self, a: int, b: int) -> None:
        a = self.find(a)
        b = self.find(b)

        if a != b:
            if len(self._elements[a]) < len(self._elements[b]):
                a, b = b, a

            self._parent[b] = a

            for elem in self._elements[b]:
                self._elements[a].add(elem)

            self._elements[b].clear()

    def get(self, v: int) -> int:
        return self.find(v)

    def size(self, v: int) -> int:
        return len(self._elements[self.find(v)])

    def get_elements(self, v: int) -> SortedSet:
        return self._elements[self.find(v)]

    def is_connected(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)

    def add_vertex(self, data: Any) -> int:
        vert_id = len(self._parent)
        self._parent.append(vert_id)
        self._elements.append(SortedSet([data]))

        return vert_id
