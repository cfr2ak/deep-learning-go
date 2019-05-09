import importlib


class Encoder:
    def name(self):
        raise NotImplementedError()

    def encode(self, game_state):
        """
        turn a Go board point  into an integer point
        :param game_state:
        :return:
        """
        raise NotImplementedError()

    def encode_point(self, point):
        """
        turns integer index back into go board point
        :param point:
        :return:
        """
        raise NotImplementedError()

    def decode_point_index(self, index):
        raise NotImplementedError()

    def num_points(self):
        raise NotImplementedError()

    def shape(self):
        raise NotImplementedError()


def get_encoder_by_name(name, board_size):
    if isinstance(board_size, int):
        board_size = (board_size, board_size)
    module = importlib.import_module('dlgo.encoder.' + name)
    constructor = getattr(module, 'create')
    return constructor(board_size)




