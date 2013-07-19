from skimage.color import rgb2lab
import numpy as np

from yoink.color import unpack_last, deltaE_cmc, deltaE_cie76, deltaE_ciede94, deltaE_ciede2000


def test_unpack_list():
    a = [1, 2, 3]
    x, y, z = unpack_last(a)
    assert x == 1
    assert y == 2
    assert z == 3


def test_unpack_array():
    a = np.array([1, 2, 3])
    x, y, z = unpack_last(a)
    assert x == 1
    assert y == 2
    assert z == 3


def test_unpack_arraylist():
    a = np.array([[1, 2, 3]])
    x, y, z = unpack_last(a)
    assert x[0] == 1
    assert y[0] == 2
    assert z[0] == 3


def get_colors():
    rgb1 = np.zeros((2, 2, 3))
    rgb1[:, :] = [1, 0, 0]
    lab1 = rgb2lab(rgb1)

    rgb2 = np.array(rgb1)
    rgb2[0, 1, 2] += 0.1
    rgb2[1, 0, 2] += 0.5
    rgb2[1, 1, 2] += 1.e-0
    lab2 = rgb2lab(rgb2)
    return lab1, lab2


def test_cmc():
    lab1, lab2 = get_colors()
    oracle = np.array([[0., 1.26874821], [5.95561801, 7.05602917]])
    ans = deltaE_cmc(lab1, lab2)
    assert ans == oracle


def test_cie76():
    lab1, lab2 = get_colors()
    oracle = np.array([[0., 7.32084628], [63.0161865, 129.49648305]])
    ans = deltaE_cie76(lab1, lab2)
    assert ans == oracle


def test_ciede94():
    lab1, lab2 = get_colors()
    oracle = np.array([[0., 3.40872722], [26.01559953, 51.05794486]])
    ans = deltaE_ciede94(lab1, lab2)
    assert ans == oracle


def test_ciede2000():
    lab1, lab2 = get_colors()
    oracle = np.array([[0., 3.00112921], [29.1280938, 48.50997063]])
    ans = deltaE_ciede2000(lab1, lab2)
    assert ans == oracle
