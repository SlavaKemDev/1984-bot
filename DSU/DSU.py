from typing import Any


class DSU:
    def __init__(self):
        self._parent: list[int] = []
        self._size: list[int] = []
        self._data: list[Any] = []

    def find(self, v: int) -> int:
        if v == self._parent[v]:
            return v

        self._parent[v] = self.find(self._parent[v])
        return self._parent[v]

    def union(self, a: int, b: int) -> None:
        a = self.find(a)
        b = self.find(b)

        if a != b:
            if self._size[a] < self._size[b]:
                a, b = b, a

            self._parent[b] = a
            self._size[a] += self._size[b]

            try:
                self._data[a].merge(self._data[b])
            except AttributeError:
                raise AttributeError("Data type should have a 'merge' method")

    def get(self, v: int) -> int:
        return self.find(v)

    def size(self, v: int) -> int:
        return self._size[self.find(v)]

    def get_data(self, v: int) -> Any:
        return self._data[self.find(v)]

    def is_connected(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)

    def add_vertex(self, data: Any) -> int:
        vert_id = len(self._parent)
        self._parent.append(vert_id)
        self._size.append(1)
        self._data.append(data)

        return vert_id
