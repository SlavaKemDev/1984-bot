from typing import Any, Union
from .Point import Point
from .Vert import Vert
from .DataPair import DataPair
from copy import deepcopy


class QuadTree:
    def __init__(self, left_top_coords: Point, right_bottom_coords: Point):
        assert left_top_coords.size() == right_bottom_coords.size()  # check if dims are equal

        self.dim = left_top_coords.size()
        self.vert = [Vert(left_top_coords, right_bottom_coords)]  # add root

    def _push_point(self, point: Point, vert_id: int, h: int = 0, return_only_if_exist=False) -> Union[int, None]:
        # return SubHyperRectangle which contains given point
        # creates new SubHyperRectangle if need and not return_only_if_exist

        # divide current dimension into 2 halves
        mid = (self.vert[vert_id].left_top_coords[h % self.dim] + self.vert[vert_id].right_bottom_coords[h % self.dim]) / 2
        is_left = point[h % self.dim] < mid

        self.vert[vert_id].is_leaf = False  # now in this vertex we can't hold any point

        if (is_left and not self.vert[vert_id].left) or (not is_left and not self.vert[vert_id].right):
            # if SubHyperRectangle is not exist

            if return_only_if_exist:
                return None

            # new SubHyperRectangle border coordinates
            left_top_coords = deepcopy(self.vert[vert_id].left_top_coords)
            right_bottom_coords = deepcopy(self.vert[vert_id].right_bottom_coords)

            if is_left:
                right_bottom_coords[h % self.dim] = mid
                self.vert[vert_id].left = len(self.vert)
            else:
                left_top_coords[h % self.dim] = mid
                self.vert[vert_id].right = len(self.vert)

            self.vert.append(Vert(left_top_coords, right_bottom_coords))  # create new vertex

        return self.vert[vert_id].left if is_left else self.vert[vert_id].right

    def _rec_add_point(self, point: Point, vert_id: int, h: int = 0) -> int:  # recursively push point to new leaf
        if self.vert[vert_id].point:  # if this vertex already has point, push it to child
            if self.vert[vert_id].point == point:  # break if points are equal
                self.vert[vert_id].data = self.vert[vert_id].data
                return vert_id

            # clone data, then remove
            new_vert = self._push_point(self.vert[vert_id].point, vert_id, h)
            self.vert[new_vert].point = self.vert[vert_id].point
            self.vert[new_vert].data = self.vert[vert_id].data

            self.vert[vert_id].point = None
            self.vert[vert_id].data = None

        self.vert[vert_id].subtree_size += 1

        if not self.vert[vert_id].is_leaf:  # if not in leaf
            new_vert = self._push_point(point, vert_id, h)
            return self._rec_add_point(point, new_vert, h + 1)

        # save and break if in leaf
        self.vert[vert_id].point = point
        return vert_id

    def add_point(self, point: Point, data: Any = None):  # add point to tree
        vert_id = self._rec_add_point(point, 0)
        self.vert[vert_id].data = data

    def _rec_find_nearest(self, point: Point, vert_id, h: int = 0) -> int:  # recursively fin nearest point
        if self.vert[vert_id].point:  # return point if in leaf
            return vert_id

        # create candidates to check them
        now_vert = self._push_point(point, vert_id, h, True)
        ans = None

        now_vert_list = [self.vert[vert_id].left, self.vert[vert_id].right] if not now_vert else [now_vert]

        for vert in now_vert_list:
            if not vert:
                continue

            rec_ans = self._rec_find_nearest(point, vert, h + 1)

            if not rec_ans:
                continue

            if not ans:
                ans = rec_ans
                continue

            if (self.vert[rec_ans].point - point).length() < (self.vert[ans].point - point).length():  # found new min
                ans = rec_ans

        return ans

    def find_nearest(self, point: Point) -> DataPair:  # find nearest point
        vert_id = self._rec_find_nearest(point, 0)
        vert = self.vert[vert_id]
        return DataPair(vert.point, vert.data, vert_id)
