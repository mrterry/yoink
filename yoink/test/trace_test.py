from numpy.testing import assert_almost_equal
from nose.tools import ok_
import numpy as np

from yoink.trace import naive_trace
from yoink.trace import (equispaced_colormapping, naive_colormapping,
                         bresenham_colormapping)

X0, Y0 = 4.2, 1.2


def naive_trace_right_test():
    path = naive_trace(X0, Y0, X0+1, Y0)
    oracle = [
        (4, 4.2, 1, 1.2),
        (5, 5.0, 1, 1.2),
        (5, 5.2, 1, 1.2),
    ]
    for (pj, px, pi, py), (oj, ox, oi, oy) in zip(path, oracle):
        yield ok_, pj == oj, "j doesn't match"
        yield ok_, pi == oi, "i doesn't match"
        yield assert_almost_equal, px, ox
        yield assert_almost_equal, py, oy


def naive_trace_left_test():
    path = naive_trace(X0, Y0, X0-1, Y0)
    oracle = [
        (4, 4.2, 1, 1.2),
        (4, 4.0, 1, 1.2),
        (3, 3.2, 1, 1.2), ]
    for (pj, px, pi, py), (oj, ox, oi, oy) in zip(path, oracle):
        yield ok_, pj == oj, "j doesn't match"
        yield ok_, pi == oi, "i doesn't match"
        yield assert_almost_equal, px, ox
        yield assert_almost_equal, py, oy


def naive_trace_up_test():
    path = naive_trace(X0, Y0, X0, Y0+1)
    oracle = [
        (4, 4.2, 1, 1.2),
        (4, 4.2, 2, 2.0),
        (4, 4.2, 2, 2.2),
    ]
    for (pj, px, pi, py), (oj, ox, oi, oy) in zip(path, oracle):
        yield ok_, pj == oj, "j doesn't match"
        yield ok_, pi == oi, "i doesn't match"
        yield assert_almost_equal, px, ox
        yield assert_almost_equal, py, oy


def naive_trace_down_test():
    path = naive_trace(X0, Y0, X0, Y0-1)
    oracle = [
        (4, 4.2, 1, 1.2),
        (4, 4.2, 1, 1.0),
        (4, 4.2, 0, 0.2),
    ]
    for (pj, px, pi, py), (oj, ox, oi, oy) in zip(path, oracle):
        yield ok_, pj == oj, "j doesn't match"
        yield ok_, pi == oi, "i doesn't match"
        yield assert_almost_equal, px, ox
        yield assert_almost_equal, py, oy


def naive_trace_endpoint_test():
    i_x_j_y = naive_trace(X0, Y0, X0+1, Y0+1)
    ii, x, jj, y = zip(*i_x_j_y)
    yield ok_, x[0] == X0
    yield ok_, y[0] == Y0
    yield ok_, x[-1] == X0+1
    yield ok_, y[-1] == Y0+1


def equispaced_colormapping_test1():
    ni, nj, nc = 2, 10, 3
    im = np.ones((ni, nj, nc)) * np.arange(nj, dtype=float)[None, :, None]
    x0, y0 = 0.1, 0.5
    x1, y1 = 9.9, 0.5
    l, c = equispaced_colormapping(x0, y0, x1, y1, im, N=20)
    assert_almost_equal(c[:, 0], c[:, 1])
    assert_almost_equal(c[:, 0], c[:, 2])
    r = c[:, 0]

    points = [0., 0.2, np.pi/10, 1]
    COLORS = [0., 2.06, 3.18, 9.]
    colors = np.interp(points, l, r)
    assert_almost_equal(colors, COLORS, 2)


def naive_colormapping_test1():
    ni, nj, nc = 2, 10, 3
    im = np.ones((ni, nj, nc)) * np.arange(nj, dtype=float)[None, :, None]
    x0, y0 = 0.1, 0.5
    x1, y1 = 9.9, 0.5
    l, c = naive_colormapping(x0, y0, x1, y1, im)
    assert_almost_equal(c[:, 0], c[:, 1])
    assert_almost_equal(c[:, 0], c[:, 2])
    r = c[:, 0]

    points = [0., 0.2, np.pi/10, 1]
    COLORS = [0., 2.06, 3.18, 9.]
    colors = np.interp(points, l, r)
    assert_almost_equal(colors, COLORS, 2)


def bresenham_colormapping_test1():
    ni, nj, nc = 2, 10, 3
    im = np.ones((ni, nj, nc)) * np.arange(nj, dtype=float)[None, :, None]
    x0, y0 = 0.1, 0.5
    x1, y1 = 9.9, 0.5
    l, c = bresenham_colormapping(x0, y0, x1, y1, im)
    assert_almost_equal(c[:, 0], c[:, 1])
    assert_almost_equal(c[:, 0], c[:, 2])
    r = c[:, 0]

    points = [0., 0.2, np.pi/10, 1]
    COLORS = [0., 2.06, 3.18, 9.]
    colors = np.interp(points, l, r)
    assert_almost_equal(colors, COLORS, 2)
