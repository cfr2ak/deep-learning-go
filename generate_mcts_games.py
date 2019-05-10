import argparse
import numpy as np

from dlgo.encoder import get_encoder_by_name
from dlgo import board as board
from dlgo import mcts
from dlgo.utils import print_board, print_move


def generate_game(board_size, rounds, max_moves, temperature):
    board_list, move_list = [], []
    encoder = get_encoder_by_name('oneplane', board_size)
    game = board.GameState.new_game(board_size)
    bot = mcts.MCTSAgent(rounds, temperature)
    num_moves = 0

    while not game.is_over():
        print_board(game.board)

        move = _input(game, encoder, bot, board_list, move_list)

        print_move(game.next_player, move)

        game, num_moves = _update(game, move, num_moves)

        if num_moves > max_moves:
            break

    return np.array(board_list), np.array(move_list)


def _update(game, move, num_moves):
    game = game.apply_move(move)
    num_moves += 1
    return game, num_moves


def _input(game, encoder, bot, board_list, move_list):
    move = bot.select_move(game)
    if move.is_play:
        board_list.append(game.board)

        one_hot_move = np.zeros(encoder.num_points())
        one_hot_move[encoder.encode_point(move.point)] = 1
        move_list.append(one_hot_move)
    return move



