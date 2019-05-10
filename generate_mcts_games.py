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


def main():
    args = _parse_argument()
    x_list = []
    y_list = []

    for i in range(args.num_games):
        print('Generating game %d/%d...' % (i + 1, args.num_games))
        x, y = generate_game(args.board_size, args.rounds, args.max_moves, args.temperature)
        x_list.append(x)
        y_list.append(y)

    x = np.concatenate(x_list)
    y = np.concatenate(y_list)

    np.save(args.board_out, x)
    np.save(args.move_out, y)


def _parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board-size', '-b', type=int, default=9)
    parser.add_argument('--rounds', '-r', type=int, default=1000)
    parser.add_argument('--temperature', '-t', type=float, default=0.8)
    parser.add_argument('--max-moves', '-m', type=int, default=60, help='Max moves per game.')
    parser.add_argument('--num-games', '-n', type=int, default=10)
    parser.add_argument('--board-out')
    parser.add_argument('--move-out')
    args = parser.parse_args()
    return args


if __name__ == '__main__ ':
    main()
