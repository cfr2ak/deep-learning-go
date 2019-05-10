import dlgo.gamestate
import dlgo.move
from dlgo.agent import naive_ai
from dlgo import board as board
from dlgo import types
from dlgo.utils import print_board, print_move, point_from_coords
from six.moves import input


def main():
    board_size = 9
    game = dlgo.gamestate.GameState.new_game(board_size)
    bot = naive_ai.RandomBot()

    while not game.is_over():
        print(chr(27) + "[2J")
        print_board(game.board)
        if game.next_player is types.Player.black:
            human_move = input('-- ')
            point = point_from_coords(human_move.strip())
            move = dlgo.move.Move.play(point)
        else:
            move = bot.select_move(game)
        print_move(game.next_player, move)
        game = game.apply_move(move)


if __name__ == "__main__":
    main()



