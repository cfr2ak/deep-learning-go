import argparse
import numpy as np

from dlgo.encoder import get_encoder_by_name
from dlgo import board as board
from dlgo import mcts
from dlgo.utils import print_board, print_move