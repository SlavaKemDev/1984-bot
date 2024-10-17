from typing import List, Dict, Tuple, Any, Union
from .Point import Point


class Vert:
    left_top_coords: Point
    right_bottom_coords: Point

    def __init__(self, left_top_coords: Point, right_bottom_coords: Point):
        self.left_top_coords = left_top_coords
        self.right_bottom_coords = right_bottom_coords

        self.left: Union[int, None] = None
        self.right: Union[int, None] = None

        self.is_leaf: bool = True
        self.subtree_size = 0

        self.point: Union[Point, None] = None
        self.data: Any = None
