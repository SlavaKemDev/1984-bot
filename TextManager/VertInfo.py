from datetime import datetime, timedelta
from sortedcontainers import SortedSet


class VertInfo:
    def __init__(self, dt: datetime, is_banned: bool = False):
        self.set = SortedSet([dt])
        self.is_banned = is_banned

    def merge(self, other: "VertInfo"):
        if len(self.set) < len(other.set):
            self.set, other.set = other.set, self.set

        for x in other.set:
            self.set.add(x)

        other.set.clear()

        self.is_banned |= other.is_banned

    def can_merge_new(self, max_neighbours: int, messages_time_gap: timedelta, dt: datetime) -> bool:
        if self.is_banned:
            return False

        return len(self.set) < max_neighbours or dt - self.set[-max_neighbours] >= messages_time_gap
