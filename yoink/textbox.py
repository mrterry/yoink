from matplotlib.widgets import AxesWidget


class TextBox(AxesWidget):
    def __init__(self, ax, s='', allowed_chars=None, type=str,
                 enter_callback=None, **text_kwargs):
        """
        Editable text box

        Creates a mouse-click callback such that clicking on the text box will
        activate the cursor.

        *WARNING* Activating a textbox will remove all other key-press
        bindings! They'll be stored in TextBox.old_callbacks and restored
        when TextBox.end_text_entry() is called.

        The default widget assumes only numerical data and will not
        allow text entry besides numerical characters and ('e','-','.')

        Parameters
        ----------
        *ax* : :class:`matplotlib.axes.Axes`
            The parent axes for the widget

        *s* : str
            The initial text of the TextBox.

        *allowed_chars* : seq
            TextBox will only respond if event.key in allowed_chars.  Defaults
            to None, which accepts anything.

        *type* : type
            Construct self.value using this type.  self.value is only updated
            if self.type(<text>) succeeds.

        *enter_callback* : function
            A function of one argument that will be called with
            TextBox.value passed in as the only argument when enter is
            pressed

        *text_kwargs* :
            Additional keywork arguments are passed on to self.ax.text()
        """
        AxesWidget.__init__(self, ax)
        self.ax.set_navigate(False)
        self.ax.set_yticks([])
        self.ax.set_xticks([])

        self.type = type
        self.allowed_chars = allowed_chars
        self.value = self.type(s)
        self.text = self.ax.text(0.025, 0.2, s,
                                 transform=self.ax.transAxes, **text_kwargs)

        self.enter_callback = enter_callback
        self._cid = None
        self._cursor = None
        self._cursorpos = len(self.text.get_text())
        self.old_callbacks = {}

        self.connect_event('button_press_event', self._mouse_activate)
        self.redraw_callbacks = []
        self.redraw()

    @property
    def cursor(self):
        # macosx does not provide render objects until the first fram is done.
        # Lazily generating the cursor avoids issues
        if self._cursor is None:
            x, y = self._get_cursor_endpoints()  # needs a renderer
            self._cursor, = self.ax.plot(x, y, transform=self.ax.transAxes)
            self._cursor.set_visible(False)
        return self._cursor

    def redraw(self):
        for f in self.redraw_callbacks:
            f()
        self.canvas.draw()

    def _mouse_activate(self, event):
        if self.ignore(event):
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
            self.redraw()

    def end_text_entry(self):
        keypress_cbs = self.canvas.callbacks.callbacks['key_press_event']
        if self._cid in keypress_cbs:
            self.canvas.mpl_disconnect(self._cid)
            for k in self.old_callbacks.keys():
                keypress_cbs[k] = self.old_callbacks.pop(k)

        self.cursor.set_visible(False)
        self.redraw()

    def keypress(self, event):
        """
        Parse a keypress - only allow #'s!
        """
        if self.ignore(event):
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
            if self.enter_callback is not None:
                self.enter_callback(self.value)
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
        self.redraw()

    def set_text(self, text):
        try:
            # only try to update if there's a real value
            self.value = self.type(text)
        except ValueError:
            pass
        # but always change the text
        self.text.set_text(text)

    def _get_cursor_endpoints(self):
        # to get cursor position
        # change text to chars left of the cursor
        text = self.text.get_text()
        self.text.set_text(text[:self._cursorpos])
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


def TextBoxFloat(*args, **kwargs):
    """
    TextBox that produces float values
    """
    kwargs['allowed_chars'] = '0123456789.eE-+'
    kwargs['type'] = float
    return TextBox(*args, **kwargs)
