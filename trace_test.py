from yoink.trace import naive_trace

def naive_trace_test1():
    path = naive_trace(-10.1, 10.1,-3.4, -5.3)
    assert len(path) == 24


def naive_trace_test2():
    path = naive_trace(-3.4, -5.3, 10.1, 10.1)
    assert len(path) == 30


def naive_trace_test3():
    path = naive_trace(3.4, 5.3, 10.1, 10.1)
    assert len(path) == 14


def naive_trace_test4():
    path = naive_trace(3.4, 5.3, -10.1, 10.1)
    assert len(path) == 20


def naive_trace_test5():
    x0, y0, x1, y1 = 632.596774194, 534.983870968, 636.596774194, 64.0161290323
    i_j_x_y = naive_trace(x0, y0, x1, y1)
    ii, jj, x, y = zip(*i_j_x_y)


def naive_trace_endpoint_test():
    x0, y0, x1, y1 = 632.596774194, 534.983870968, 636.596774194, 64.0161290323
    i_j_x_y = naive_trace(x0, y0, x1, y1)
    ii, jj, x, y = zip(*i_j_x_y)
    assert x[0] == x0
    assert y[0] == y0
    assert x[1] == x1
    assert y[1] == y1
