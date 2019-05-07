import random

from dlgo.types import Player, Point


def state_to_string(player_state):
    if player_state is None:
        return 'None'
    elif player_state is Player.black:
        return Player.black
    elif player_state is Player.white:
        return Player.white
    else:
        return 'undefined'


MAX_63 = 0x7fff_ffff_ffff_ffff

table = {}
empty_board = 0
for row in range(1, 20):
    for col in range(1, 20):
        for state in (Player.black, Player.white):
            code = random.randint(0, MAX_63)
            table[Point(row, col), state] = code

print('from .types import Player, Point')
print('')
print("__all__ = ['HASH_CODE', 'EMPTY_BOARD']")
print('')
print('HASH_CODE = {')
for (point, state), hash_code in table.items():
    print('    (%r, %s): %r,' % (point, state_to_string(state), hash_code))
print("}")
print('')
print('EMPTY_BOARD = %d' % (empty_board,))
