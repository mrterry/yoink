from scipy import ndimage
import pylab as plt

from yoink.guess import guess_corners
from yoink.data import rotated_lena, rotated_parabola


def make_rotated_lenafig():
    from skimage.data import lena
    plt.imshow(lena())
    plt.xticks([])
    plt.yticks([])
    plt.savefig('lena.png', dpi=500)
    plt.clf()

    im = ndimage.imread('temp.png')
    im = ndimage.rotate(im, -15.3, cval=255)
    plt.subplot(111, frameon=False)
    plt.imshow(im)
    plt.xticks([])
    plt.yticks([])
    plt.savefig('rotated_lena.png', dpi=400)


def guess_corners_img_test():
    im = rotated_lena()

    # find corners on grayscale image
    # use negative so that boundary is 0
    bw = im[:, :, 0]
    bw = 255 - bw

    corners, outline = guess_corners(bw)
    assert False


def guess_corners_line_test():
    im = rotated_parabola()

    # find corners on grayscale image
    # use negative so that boundary is 0
    bw = im[:, :, 0]
    bw = 255 - bw

    corners, outline = guess_corners(bw)
    assert False
