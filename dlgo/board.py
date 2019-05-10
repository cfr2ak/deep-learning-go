import copy
from dlgo.types import Player, Point
from dlgo import zobrist_hash


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
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    def without_liberty(self, point):
        new_liberties = self.liberties - {point}
        return GoString(self.color, self.stones, new_liberties)

    def with_liberty(self, point):
        new_liberties = self.liberties | {point}
        return GoString(self.color, self.stones, new_liberties)

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


class GameState:
    def __init__(self, board, next_player, previous_state, last_move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous_state
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous_state.previous_states |
                {(previous_state.next_player, previous_state.board.zobrist_hash())}
            )
        self.last_move = last_move

    def apply_move(self, move):
        """
        :param move: move applied to Board
        :return: new GameState after applying the move
        """
        if move.is_play:
            next_board = self._get_next_board(move, self.next_player)
        else:
            next_board = self.board

        return GameState(next_board, self.next_player.other, self, move)

    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def _does_both_sides_passed(self):
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass

    def is_over(self):
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True

        return self._does_both_sides_passed()

    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False
        next_board = self._get_next_board(move, player)
        new_string = next_board.get_go_string_on_point(move.point)
        return new_string.num_liberties == 0

    def _get_next_board(self, move, player):
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        return next_board

    @property
    def state(self):
        return self.next_player, self.board

    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False
        next_board = self._get_next_board(move, player)
        next_state = player.other, next_board.zobrist_hash()
        return next_state in self.previous_states

    @staticmethod
    def _check_state_exist_ever_before(next_state, past_state):
        while past_state is not None:
            if past_state.state == next_state:
                return True
            past_state = past_state.previous_state
        return False

    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return (
            self.board.get_color_on_point(move.point) is None and
            not self.is_move_self_capture(self.next_player, move) and
            not self.does_move_violate_ko(self.next_player, move)
        )

    def get_legal_moves(self):
        move_list = []
        for row in range(1, self.board.num_rows + 1):
            for col in range(1, self.board.num_cols + 1):
                move = Move.play(Point(row,  col))
                if self.is_valid_move(move):
                    move_list.append(move)

        move_list.append(Move.pass_turn())
        move_list.append(Move.resign())

        return move_list

    # def get_winner(self):
    #     if not self.is_over():
    #         return None
    #     if self.last_move.is_resign:
    #         return self.next_player
    #     game_result = compute_game_result(self)
    #     return game_result.winner




