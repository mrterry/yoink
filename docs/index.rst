Welcome to Yoink's documentation!
=================================
Yoink is a tool for extracting data from rasterized images.

At SciPy 2013, Matt Terry gave a humorous `lighting talk`__ demonstrating
yoink pulling data from an image despite an especially obnoxious colormap.

__ http://www.youtube.com/watch?v=ywHqIEv3xXg&t=31m42s


Dependencies
------------
Yoink currently depends on numpy, scipy, and matplotlib.  The custom widgets
provided by yoink are designed to work independent of the backend.  Yes, even
with the quirky macosx backend.


Extracting colormapped data
---------------------------
Say you have a color-mapped image that contains data that you want.  For
illustration purposes, we'll use this strangely colored elevation map of the
Yosemite valley.

.. image:: yosemite.png

Content-wise, the image provides all the information you need:

-  rectangular canvas
-  x-axis scale
-  y-axis scale
-  colorbar

If your image is rotated, (because the office printer-scanner-copier has a tilt
to it), you will have to correct for that using something like `skimage.rotate()`_.
Also, if your image is distorted, (because it is a picture of someones
presentation slides) you will also need to fix the perspective with XXX and
compensate for distortion using XXX.

Once your image is prepared, yoink can be used as a command line tool or
within an interactive python session.

-  For command line use, yoink provides the executable :code:`yoink`.

.. code::

    $ yoink image -o image_data.npz path/to/image/file 

    
-  For interactive Python usage, use the :class:`yoink.CmapExtractor` class.
   If you are using an ipython session with an interactive matplotlib event
   loop (e.g. :code:`%pylab` magic in ipython), :code:`plt.show()` will not be
   necessary.

.. code:: python

    from yoink import CmapExtractor
    from yoink.data import yosemite

    im = yosemite()
    ext = CmapExtractor(im, 'image_data.npz')

    import matplotlib.pyplot as plt
    plt.show()


Two windows should be visible.  Use the selector figure to identify your data
within the image and the annotate figure to set the limits of the x-axis,
y-axis, and colorbar.

.. image:: annotator.png
    :height: 250px

.. image:: selector.png
    :height: 250px



First identify the colorbar.  Activate the colorbar selector widget by
picking "Select Colorbar" radio button.  Then drag the endpoints of the newly
visible line to the endpoints of the colorbar on the image.  Yoink shows you
the colorbar you've selected to the right of the image.

.. image:: cbar_half_select.png
    :height: 250px


Next crop the image.  Activate the image cropper by selecting "Crop Image".
Drag the shutters so that only the image within the image is not obscured.
Note that the image in annotate figure updates as you drag the shutters.

.. image:: sel_half_crop.png
    :height: 250px
    :caption: this figure has correctly select the top of the colorbar


During the data selection exercises, the annotate window will update to show
you how yoink is interpreting your selected data.  The picture in the annotate
figure should look like the figure you are selecting.  If the colors are off,
there is something wrong with the colorbar selection.

.. image:: annotate_cropped.png
    :height: 250px


Helpful Links
-------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. toctree::
   :maxdepth: 2

.. _`skimage.rotate()`: scikit-image.com
