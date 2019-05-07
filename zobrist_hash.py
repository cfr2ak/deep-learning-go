import random

from dlgo.types import Player, Point


MAX_63 = 0x7fff_ffff_ffff_ffff

table = {}
empty_board = 0
for row in range(1, 20):
    for col in range(1, 20):
        for state in (Player.black, Player.white):
            code = random.randint(0, MAX_63)
            table[Point(row, col), state] = code


