"""TextBox widget.  This is inteded for inclusion in matplotlib, but copied
here until that day arrives."""
from matplotlib.widgets import AxesWidget


class TextBox(AxesWidget):
    """Editable text box

    Creates a mouse-click callback such that clicking on the text box will
    activate the cursor.

    *WARNING* Activating a textbox will remove all other key-press
    bindings! They'll be stored in TextBox.old_callbacks and restored
    when TextBox.end_text_entry() is called.

    The default widget assumes only numerical data and will not
    allow text entry besides numerical characters and ('e','-','.')

    Use :meth:`on_changed` to connect to TextBox updates

    Parameters
    ----------
    ax : :class:`matplotlib.axes.Axes`
        The parent axes for the widget
    s : str
        The initial text of the TextBox.
    allowed_chars : sequence, optional
        sequence of characters that are valid TextBox text
        Defaults to None, which accepts anything.
    type : type, optional, default=str
        Construct self.value using this type.  self.value is only updated
        if self.type(<text>) succeeds.
    **text_kwargs : dict
        Additional keyword arguments are passed on to self.ax.text()

    Attributes
    ----------
    ax : :class:`matplotlib.axes.Axes`
        The parent axes for the widget
    type : callable
        callable that is used to set self.value
    allowed_chars
        TextBox will only respond if event.key in allowed_chars.  Defaults
        to None, which accepts anything.
    value : value
        Current value of the textbox.
    text : Text artist
        The Text artist that TextBox modifies
    """
    def __init__(self, ax, s='', allowed_chars=None, type=str, **text_kwargs):
        AxesWidget.__init__(self, ax)
        self.ax.set_navigate(False)
        self.ax.set_yticks([])
        self.ax.set_xticks([])

        self.type = type
        self.allowed_chars = allowed_chars
        self.value = self.type(s)
        self.text = self.ax.text(0.025, 0.2, s,
                                 transform=self.ax.transAxes, **text_kwargs)

        self._cid = None
        self._cursor = None
        self._cursorpos = len(self.text.get_text())
        self.old_callbacks = {}

        self.cnt = 0
        self.observers = {}

        self.exit_cnt = 0
        self.exit_observers = {}

        self.connect_event('button_press_event', self._mouse_activate)

    def on_changed(self, func):
        """
        When the textbox changes self.value, call *func* with the new value.

        A connection id is returned with can be used to disconnect.
        """
        cid = self.cnt
        self.observers[cid] = func
        self.cnt += 1
        return cid

    def on_exit(self, func):
        """
        When exiting TextBox entry, call *func* with the new value.

        A connection id is returned with can be used to disconnect.
        """
        cid = self.cnt
        self.exit_observers[cid] = func
        self.cnt += 1
        return cid

    def disconnect_exit(self, cid):
        try:
            del self.exit_observers[cid]
        except KeyError:
            pass

    def disconnect(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass

    @property
    def cursor(self):
        # macosx does not provide render objects until the first frame is done.
        # Lazily generating the cursor avoids issues
        if self._cursor is None:
            x, y = self._get_cursor_endpoints()  # needs a renderer
            self._cursor, = self.ax.plot(x, y, transform=self.ax.transAxes)
            self._cursor.set_visible(False)
        return self._cursor

    def _mouse_activate(self, event):
        if self.ignore(event) or not self.eventson:
            return
        if self.ax == event.inaxes:
            self.begin_text_entry()
        else:
            self.end_text_entry()

    def begin_text_entry(self):
        keypress_cbs = self.canvas.callbacks.callbacks['key_press_event']
        if self._cid not in keypress_cbs:
            # remove all other key bindings
            for k in keypress_cbs.keys():
                self.old_callbacks[k] = keypress_cbs.pop(k)

            self._cid = self.canvas.mpl_connect('key_press_event',
                                                self.keypress)
            self.cursor.set_visible(True)
            if self.drawon:
                self.canvas.draw()

    def end_text_entry(self):
        keypress_cbs = self.canvas.callbacks.callbacks['key_press_event']
        if self._cid in keypress_cbs:
            self.canvas.mpl_disconnect(self._cid)
            for k in self.old_callbacks.keys():
                keypress_cbs[k] = self.old_callbacks.pop(k)

        self.cursor.set_visible(False)

        for func in self.exit_observers.items():
            func(self.value)

        if self.drawon:
            self.canvas.draw()

    def keypress(self, event):
        """Parse a keypress and update the value if possible"""
        if self.ignore(event) or not self.eventson:
            return

        newt = t = self.text.get_text()
        assert self._cursorpos >= 0
        assert self._cursorpos <= len(t)
        # TODO numeric keypad

        if not isinstance(event.key, str):
            # event.key may be None
            return
        elif event.key == 'backspace':  # simulate backspace
            if self._cursorpos > 0:
                newt = t[:self._cursorpos - 1] + t[self._cursorpos:]
                self._cursorpos -= 1
        elif event.key == 'delete':  # forward delete
            newt = t[:self._cursorpos] + t[self._cursorpos + 1:]
        elif event.key == 'left':
            if self._cursorpos > 0:
                self._cursorpos -= 1
        elif event.key == 'right':
            if self._cursorpos < len(t):
                self._cursorpos += 1
        elif event.key == 'enter':
            self.end_text_entry()
        elif self.allowed_chars is None:
            newt = t[:self._cursorpos] + event.key + t[self._cursorpos:]
            self._cursorpos += len(event.key)
        elif event.key in self.allowed_chars:
            newt = t[:self._cursorpos] + event.key + t[self._cursorpos:]
            self._cursorpos += 1
        else:
            return  # do not allow abcdef...

        self.set_text(newt)
        x, y = self._get_cursor_endpoints()
        self.cursor.set_xdata(x)
        if self.drawon:
            self.canvas.draw()

    def set_text(self, text):
        """Set the text"""
        success = False
        try:
            # only try to update if there's a real value
            self.value = self.type(text)
            success = True
        except ValueError:
            pass
        # but always change the text
        self.text.set_text(text)
        if success and self.eventson:
            for func in self.observers.values():
                func(self.value)

    def _get_cursor_endpoints(self):
        import matplotlib as mpl
        # to get cursor position:
        #   1) change text to chars left of the cursor
        #   2) if macos, redraw
        #   3) get extent of temporary text box
        #   4) place cursor at appropriate place

        text = self.text.get_text()
        self.text.set_text(text[:self._cursorpos])
        if mpl.get_backend() == 'MacOSX':
            # self.text can't get_window_extent() until drawn
            # this introduces some lag, so only do it on macos
            # apparently the GCContext gets invalidated when you set_text, so
            # you always have to do this
            self.canvas.draw()
        bbox = self.text.get_window_extent()
        l, b, w, h = bbox.bounds  # in pixels
        r = l + w
        # now restore correct text
        self.text.set_text(text)

        # cursor line in data coordinates
        bx, by = self.ax.transAxes.inverted().transform((r, b))
        tx, ty = self.ax.transAxes.inverted().transform((r, b + h))
        dy = 0.5 * (ty - by)
        return [bx, tx], [by - dy, ty + dy]


class TextBoxFloat(TextBox):
    """TextBox for floating point numbers"""
    def __init__(self, *args, **kwargs):
        kwargs['allowed_chars'] = '0123456789.eE-+'
        kwargs['type'] = float
        TextBox.__init__(self, *args, **kwargs)
