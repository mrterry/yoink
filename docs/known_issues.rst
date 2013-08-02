Known Issues
============

`key_press_event` handling in matplotlib is quirky.  It's being worked on, but
here on the known issues.  Please contact matt dot terry at gmail dot com if
you find others. 

QT Backend
----------
As of matplotlib 1.3.0, the Qt4Agg and Qt backends do not handle backspace key
events.  This severely limits the usefulness of :class:`yoink.widgets.TextBox`
widgets.  There is a `PR <http://github.com/matplotlib/matplotlib/pull/2273>`
to fix this, but it is not in a matplotlib release.

MacOSX Backend
--------------
Event handling on MacOSX is a little finicky, particularly handling `key_press_events`.
This mainly affects text entry in TextBox widgets.  To receive events from the
OS, you must use a framework python build that also links to the Mac OS stuff
that fires event.  tldr; you must use `pythonw` if you want `key_press_events`
to work.
