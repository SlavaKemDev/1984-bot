class DSU:
    def __init__(self, n: int = 0):
        self._parent = [i for i in range(n)]
        self._size = [1] * n

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

    def get(self, v: int) -> int:
        return self.find(v)

    def size(self, v: int) -> int:
        return self._size[self.find(v)]

    def is_connected(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)

    def add_vertex(self) -> int:
        vert_id = len(self._parent)
        self._parent.append(vert_id)
        self._size.append(1)

        return vert_id
