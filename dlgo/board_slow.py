import copy
from dlgo.types import Player


class Move:
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    @classmethod
    def resign(cls):
        return Move(is_resign=True)


class GoString:
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    def remove_liberty(self, point):
        self.liberties.remove(point)

    def add_liberty(self, point):
        self.liberties.add(point)

    def merged_with(self, go_string):
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones
        )

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties


class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}

    def _is_point_on_grid(self, point):
        if self.is_on_grid(point):
            return True
        else:
            return False

    def _check_point_validity(self, point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None

    def _update_neighbor_point(self, player, neighbor, point_info):
        neighbor_string = self._grid.get(neighbor)
        if neighbor_string is None:
            point_info['liberties'].append(neighbor)
        elif neighbor_string.color == player:
            self._append_same_color_neighbor(neighbor_string, point_info['adjacent_same_color'])
        else:
            self._append_opposite_color_neighbor(neighbor_string, point_info['adjacent_opposite_color'])

    @staticmethod
    def _append_same_color_neighbor(neighbor_string, adjacent_same_color):
        if neighbor_string not in adjacent_same_color:
            adjacent_same_color.append(neighbor_string)

    @staticmethod
    def _append_opposite_color_neighbor(neighbor_string, adjacent_opposite_color):
        if neighbor_string not in adjacent_opposite_color:
            adjacent_opposite_color.append(neighbor_string)

    def place_stone(self, player, point):
        self._check_point_validity(point)
        point_info = {
            'adjacent_same_color': [],
            'adjacent_opposite_color': [],
            'liberties': []
        }

        for neighbor in point.neighbors():
            if not self._is_point_on_grid(neighbor):
                continue
            self._update_neighbor_point(player, neighbor, point_info)

        new_string = GoString(player, [point], point_info['liberties'])


