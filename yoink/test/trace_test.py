from yoink.trace import naive_trace
from numpy.testing import assert_almost_equal
from nose.tools import ok_

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
