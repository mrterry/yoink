Extracting colormapped data
###########################
Say you have a color-mapped image that contains data that you want.  For
illustration purposes, we'll use this strangely colored elevation map of the
Yosemite valley.

.. figure:: _images/yosemite.png
    :height: 250px

Content-wise, the image provides all the information you need:

*  unrotated, rectangular frame
*  x-axis scale
*  y-axis scale
*  colorbar

Preparing you image
===================
If your image is rotated, (because the office printer-scanner-copier has a tilt
to it), you will have to correct for that using something like
`rotate in scikit-image <http://scikit-image.org/docs/dev/api/skimage.transform.html#rotate>`_
Also, if your image is distorted, (because it is a picture of someones
presentation slides) you will also need to fix the perspective manually.
Scikit-image has an nice 
`example <http://scikit-image.org/docs/dev/auto_examples/applications/plot_geometric.html>`_
of how to do these kinds of transformations.

Create Select & Annotate Figures
================================
Once your image is prepared, yoink can be used as a command line tool or
within an interactive python session.

*  For command line use, yoink provides the executable :code:`yoink`.

   .. code::

       $ yoink image -o image_data.npz path/to/image/file 

    
*  For interactive Python usage, use the :class:`yoink.cmap_app.CmapExtractor` class.
   If you are using an ipython session with an interactive matplotlib event
   loop (e.g. :code:`%pylab` magic in ipython), :code:`plt.show()` will not be
   necessary.

   .. code:: python
   
       from yoink import cmapextractor
       from yoink.data import yosemite
   
       im = yosemite()
       ext = cmapextractor(im, 'image_data.npz')
   
       import matplotlib.pyplot as plt
       plt.show()


Two windows should be visible.  Use the selector figure to identify your data
within the image and the annotate figure to set the limits of the x-axis,
y-axis, and colorbar.


.. figure:: _images/select_fig.png
    :height: 250px

    Use this figure to select the frame of your data and to select the
    colorbar.


.. figure:: _images/annoate_fig.png
    :height: 250px

    Use this window to annotate the axes limits and the colorbar limits.


Select Colorbar
===============
First identify the colorbar.  Activate the colorbar selector widget by
picking "Select Colorbar" radio button.  Then drag the endpoints of the newly
visible line to the endpoints of the colorbar on the image.  Yoink shows you
the colorbar you've selected to the right of the image.

.. figure:: _images/select_cbar.png
    :height: 250px


Crop Image
==========
Next crop the image.  Activate the image cropper by selecting "Crop Image".
Drag the shutters so that only the image within the image is not obscured.
Note that the image in annotate figure updates as you drag the shutters.

.. figure:: _images/select_crop.png
    :height: 250px

    This figure has correctly select the top of the colorbar


During the data selection exercises, the annotate window will update to show
you how yoink is interpreting your selected data.  The picture in the annotate
figure should look like the figure you are selecting.  If the colors are off,
there is something wrong with the colorbar selection.

.. figure:: _images/annotate_crop.png
    :height: 250px


Annoate and Dump
================
Now use the textboxes in the annotate figure to set the x-axis, y-axis,
and colorbar limits.  The ticks on the figure should update automatically.

Now the image in the annotate figure should look very similar to the original
image, still shown in the select figure.  (It should, this is the data you are
yoinking).  If you are running yoink from the command line, click the 
"Dump to file" button to text files or a single numpy npz file (depending of
the suffix of the output file name).  If running yoink from an interactive
Python session, :func:`yoink.cmap_app.CmapExtractor.get_data` will return a
dictionary of extracted data.  It provides the `x`, `y`, and `z` data as
well as the discrete colormapping: `l`, and `rgb`.
