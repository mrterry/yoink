from border import DeformableBorder
import pylab as plt


fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, axisbg='#FFFFCC')

im = plt.imread('test_img.png')
plt.imshow(im, interpolation='none')

border = DeformableBorder(plt.gca())

plt.show()
