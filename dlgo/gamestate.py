import copy

from dlgo.board import Board
from dlgo.move import Move
from dlgo.types import Player, Point


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
                move = Move.play(Point(row, col))
                if self.is_valid_move(move):
                    move_list.append(move)

        move_list.append(Move.pass_turn())
        move_list.append(Move.resign())

        return move_list

    def get_winner(self):
        if not self.is_over():
            return None
        if self.last_move.is_resign:
            return self.next_player
        game_result = compute_game_result(self)
        return game_result.winner
