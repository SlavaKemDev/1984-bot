from typing import Any
from .Point import Point


class DataPair:
    def __init__(self, point: Point, data: Any):
        self.point = point
        self.data = data
