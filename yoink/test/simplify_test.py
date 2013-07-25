from yoink.simplify import rdp_indexes
import numpy as np


def test_rdp_indexes_bigeps():
    x = [0, 0.5, 3, 5, 7, 8, 9, 12]
    y = [5, 2.5, 0, 2.5, 4, 3.5, 2, 5]
    p = np.vstack([x, y]).T

    indexes = rdp_indexes(p, 0.9)
    assert indexes == [0, 2, 4, 6, 7]


def test_rdp_indexes_smalleps():
    x = [0, 0.5, 3, 5, 7, 8, 9, 12]
    y = [5, 2.5, 0, 2.5, 4, 3.5, 2, 5]
    p = np.vstack([x, y]).T

    indexes = rdp_indexes(p, 0.5)
    assert indexes == [0, 1, 2, 4, 6, 7]


def test_rdp_indexes_0eps():
    x = [0, 0.5, 3, 5, 7, 8, 9, 12]
    y = [5, 2.5, 0, 2.5, 4, 3.5, 2, 5]
    p = np.vstack([x, y]).T

    indexes = rdp_indexes(p, 0.)
    assert indexes == range(len(x))
