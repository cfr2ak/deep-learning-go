import dlgo.gamestate
from dlgo.agent import naive_ai
from dlgo import board
from dlgo import types
from dlgo.utils import print_board, print_move
import time


def main():
    board_size = 9
    game = dlgo.gamestate.GameState.new_game(board_size)
    bots = {
        types.Player.black: naive_ai.RandomBot(),
        types.Player.white: naive_ai.RandomBot()
    }
    while not game.is_over():
        time.sleep(0.3)

        print(chr(27) + '[2J')
        print_board(game.board)
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)


if __name__ == '__main__':
    main()
