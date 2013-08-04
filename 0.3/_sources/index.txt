Welcome to Yoink's documentation!
=================================
Yoink is a tool for extracting data from rasterized images.

Say you have an academic paper with an figure containing data you would like
to use.  Unfortunately, the raw data is not available.  All you have is the
image on the page.  Fortunately, the image contains all the information you
need: clear lines, axis labels, and colorbar (if a colormapped image).  Yoink
helps you extract ("yoink!") the data from your picture.

Yoink is pure Python and has a minimal set of dependencies (which you probably
already have installed), to help you get your data instead of installing
software.

At SciPy 2013, Matt Terry gave a humorous `lighting talk`__ demonstrating
yoink pulling data from an image despite an especially obnoxious colormap.

__ http://www.youtube.com/watch?v=ywHqIEv3xXg&t=31m42s

.. youtube:: ywHqIEv3xXg?start=1902

Follow the development on GitHub: `https://github.com/mrterry/yoink`.  Feedback
and pull requests are welcome.

Dependencies
------------
Yoink currently depends on:

*  numpy
*  scipy
*  matplotlib
*  scikit-image
   


Helpful Links
-------------
.. toctree::
   :maxdepth: 2

   notebooks/notebooks
   walkthrough
   known_issues
   modules


Thanks
------

The image of the beautiful, yet deadly mantis 
`shrimp <http://www.flickr.com/photos/jayvee/8766788164/>`_
courtesy
`Jayvee Fernandez <http://abuggedlife.com>`_,
licensed under a Creative Commons CC-By-2.0 license.
