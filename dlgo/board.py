from dlgo.gostring import GoString
from dlgo import zobrist_hash


class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}
        self._hash = zobrist_hash.EMPTY_BOARD

    def place_stone(self, player, point):
        self._check_point_validity(point)
        point_info = {
            'adjacent_same_color': [],
            'adjacent_opposite_color': [],
            'liberties': []
        }

        for neighbor in point.neighbors():
            if not self.is_point_on_grid(neighbor):
                continue
            self._update_point_info(player, neighbor, point_info)

        new_string = GoString(player, [point], point_info['liberties'])

        self._merge_with_adjacent_same_string(new_string, point_info)

        self._hash ^= zobrist_hash.HASH_CODE[point, player]

        for other_color_string in point_info['adjacent_opposite_color']:
            replacement = other_color_string.without_liberty(point)
            if replacement.num_liberties:
                self._replace_string(other_color_string.without_liberty(point))
            else:
                self._remove_string(other_color_string)

    def _replace_string(self, new_string):
        for point in new_string.stones:
            self._grid[point] = new_string

    def _remove_string(self, string):
        for point in string.stones:
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    self._replace_string(neighbor_string.with_liberty(point))
            self._grid[point] = None

            self._hash ^= zobrist_hash.HASH_CODE[point, string.color]

    def zobrist_hash(self):
        return self._hash

    def is_point_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get_color_on_point(self, point):
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def get_go_string_on_point(self, point):
        string = self._grid.get(point)
        if string is None:
            return None
        return string

    def _check_point_validity(self, point):
        assert self.is_point_on_grid(point)
        assert self._grid.get(point) is None

    def _update_point_info(self, player, neighbor, point_info):
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

    def _merge_with_adjacent_same_string(self, new_string, point_info):
        for same_color_string in point_info['adjacent_same_color']:
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string




