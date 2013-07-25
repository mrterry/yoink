"""Conveniently pre-packaged images for testing."""
from os.path import dirname, abspath, join as pjoin
from matplotlib.image import imread

DIR = dirname(abspath(__file__))


def rotated_lena():
    return imread(pjoin(DIR, 'rotated_lena.png'))


def rotated_parabola():
    return imread(pjoin(DIR, 'rotated_parabola.png'))


def test_cmap():
    return imread(pjoin(DIR, 'test_cmap.png'))


def square_lena():
    return imread(pjoin(DIR, 'square_lena.png'))


def yosemite():
    return imread(pjoin(DIR, 'yosemite.png'))


def squiggle():
    return imread(pjoin(DIR, 'squiggle.png'))
