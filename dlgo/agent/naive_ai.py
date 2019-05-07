"""
Playing about 30 kyu
randomly select any valid move that doesn't fill in one of its own eyes
"""

import random
from dlgo.agent.base import Agent
from dlgo.agent.helper import is_point_and_eye
from dlgo.board_slow import Move
from dlgo.types import Point


class RandomBot(Agent):
    def select_move(self, game_state):
        """
        Choose a random valid move that preserves own eyes
        :param game_state: current state of the board
        :return: random move from candidate points
        """
        move_candidates = []

        for r in range(1, game_state.board.num_rows + 1):
            for c in range(1, game_state.board.num_cols + 1):
                candidate = Point(row=r, col=c)

                if game_state.is_valid_move(Move.play(candidate)) and \
                    not is_point_and_eye(game_state.board,
                                         candidate,
                                         game_state.next_player):
                    move_candidates.append(candidate)

                if not move_candidates:
                    return Move.pass_turn()
                return Move.play(random.choice(move_candidates))
