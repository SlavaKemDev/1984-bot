from typing import Any
from .Point import Point


class DataPair:
    def __init__(self, point: Point, data: Any, vert_id: int):
        self.point = point
        self.data = data
        self.vert_id = vert_id
