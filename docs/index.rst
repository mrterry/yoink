Welcome to Yoink's documentation!
=================================
Yoink is a tool for extracting data from rasterized images.

Say you have an academic paper with an figure containing data you would like
to use.  Unfortunalely, the raw data is not available.  All you have is the
image on the page.  Fortunatley, the image contains all the information you
need: clear lines, axis labels, and colorbar (if a colormapped image).  Yoink
helps you extract ("yoink!") the data from your picture.

Yoink is pure Python and has a minimal set of dependencies (which you probably
already have installed), to help you get your data instead of installing
software.

At SciPy 2013, Matt Terry gave a humorous `lighting talk`__ demonstrating
yoink pulling data from an image despite an especially obnoxious colormap.

__ http://www.youtube.com/watch?v=ywHqIEv3xXg&t=31m42s

.. youtube:: ywHqIEv3xXg?start=1902


Dependencies
------------
Yoink currently depends on:

*  numpy
*  scipy
*  matplotlib
*  scikit-image
   
The custom widgets provided by yoink are designed to work independent of the
backend.  Yes, even with the quirky macosx backend.  That said, we recommend
running with matplotlib *not* in interactive mode.  Some drawing operations are
expensive and automatic figure updating can be slow.


Helpful Links
-------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. toctree::
   :maxdepth: 2

   walkthrough
