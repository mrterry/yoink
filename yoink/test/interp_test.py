from itertools import permutations
from nose.tools import ok_

from yoink.interp import order_corners, get_corner_grid


def order_corners_test():
    ordered = [(1, 1), (5, 1), (5, 5), (1, 5)]
    for shuffled in permutations(ordered):
        reord = order_corners(shuffled)
        yield ok_, ordered == reord


def get_corner_grid_test():
    ni, nj = 4, 5
    corners = [(1, 1), (ni-1, 1), (ni-1, nj-1), (1, nj-1)]
    get_corner_grid(corners, ni, nj)
