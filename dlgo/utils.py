from dlgo.types import Point


def is_point_and_eye(board, point, color):
    if board.get(point) is not None:
        return False

    for neighbor in point.neighbors():
        if board.is_point_on_grid(neighbor)