from itertools import permutations
import numpy as np
from nose.tools import ok_

from yoink.interp import order_corners, get_corner_grid, invert_cmap


def order_corners_test():
    ordered = [(1, 1), (5, 1), (5, 5), (1, 5)]
    for shuffled in permutations(ordered):
        reord = order_corners(shuffled)
        yield ok_, ordered == reord


def get_corner_grid_test():
    ni, nj = 4, 5
    corners = [(1, 1), (ni-1, 1), (ni-1, nj-1), (1, nj-1)]
    get_corner_grid(corners, ni, nj)


def invert_cmap_test():
    k = 3
    colors = np.ones((20, k))
    l = np.linspace(0, 1, 20)
    colors *= l[:, None]

    ni, nj = 20, 20
    pix = np.random.random((ni, nj, k))
    z = invert_cmap(pix, l, colors)
    assert z.min() >= l[0]
    assert z.max() <= l[-1]
    assert z.shape == (ni, nj)
