Yoink
=====

Yoink is a tool for extracting data from scientific figures.  

I'm often faced with this problem: I have a scientific publication with data
that I want to use, however the raw data is not available.  It is only provided
in rasterized images.  The figures are of good quality.  The line plots provide
axes with labels and ticks; the pseudocolor (false-color) images have axes and
a colorbar.  In theory all the needed information is there, it is just not
particularly convenient.

Yoink provides a set of matplotlib-based widgets that assist in extracting
set of matplotlib-based widgets that assist in doing so.

Yoink does not require exotic dependencies, only `numpy`, `scipy`, and
`matplotlib`.  (planned) If `scikit-image` is available, yoink can guess the
cropping and rotation of a figure.

The easiest way to use yoink is to use the executables `yoink_cmap` and
`yoink_points` (planned).

$ yoink_cmap wacky_figure.png -o output.txt
