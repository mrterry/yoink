Yoink
=====

Yoink is a tool for extracting data from scientific figures.  

I'm often faced with this problem: I have a scientific publication with data
that I want to use, however the raw data is not available.  It is only provided
in rasterized images.  The figures are of good quality.  The line plots provide
axes with labels and ticks; the pseudo-color figures have axes and a colorbar.
In theory all the needed information is there, it is just not particularly
convenient.

Yoink provides a set of matplotlib-based widgets that assist in extracting
useful numerical data from rasterized images.

Yoink does not require exotic dependencies, only numpy, scipy, and matplotlib.
