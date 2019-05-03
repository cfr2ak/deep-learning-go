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
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def _get_color_on_point(self, point):
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def _get_go_string_on_point(self, point):
        string = self._grid.get(point)
        if string is None:
            return None
        return string

    def _check_point_validity(self, point):
        assert self._is_point_on_grid(point)
        assert self._grid.get(point) is None

    def _update_neighbor_point_info(self, player, neighbor, point_info):
        neighbor_string = self._grid.get(neighbor)
        if neighbor_string is None:
            point_info['liberties'].append(neighbor)
        elif neighbor_string.color == player:
            self._append_neighbor(neighbor_string, point_info['adjacent_same_color'])
        else:
            self._append_neighbor(neighbor_string, point_info['adjacent_opposite_color'])

    @staticmethod
    def _append_neighbor(neighbor_string, adjacent_list):
        if neighbor_string not in adjacent_list:
            adjacent_list.append(neighbor_string)

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
            self._update_neighbor_point_info(player, neighbor, point_info)

        new_string = GoString(player, [point], point_info['liberties'])

        for same_color_string in point_info['adjacent_same_color']:
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string
        for other_color_string in point_info['adjacent_opposite_color']:
            other_color_string.remove_liberty(point)
        for other_color_string in point_info['adjacent_opposite_color']:
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)


