from collections import defaultdict


on_f_docstring = """\
    When {actioned} call `f` with positional and keyword args and kw

    Parameters
    ----------
    f : callable
        Function to call when object changes
    args : tuple
        sequence of positional args to f
    kw : dict
        dict of keyword args to f

    Returns
    -------
    cid : int
        connection id which can be used to disconnect.
    """

fed_docstring = "Call {on_action} observers with appropriate arguments"

disf_docstring = """\
    remove {on_action} observers with connection id *cid*

    Parameters
    ----------
    cid : int
        remove observer with given connection id
    """


class ActionableMeta(type):
    """Metaclass for populating boilerplate callback methods

    Consumes the class attribute ACTIONS, where ACTIONS is a list of
    3-element tuples.  The elements are the names of the on_ACTION, ACTIONED,
    and disconnect_ACTION methods.
    """
    def __new__(meta, name, bases, dct):
        actions = dct.pop('ACTIONS', [])
        for on_action, actioned, disconnect in actions:
            def on_f(self, f, args=None, kw=None):
                args = args if args is not None else tuple()
                kw = kw if kw is not None else dict()
                cid = self.cid
                self._callbacks[on_action][cid] = (f, args, kw)
                self.cid += 1
                return cid
            on_f.__doc__ = on_f_docstring.format(actioned=actioned)
            on_f.__name__ = on_action
            dct[on_action] = on_f

            def fed(self):
                for f, args, kw in self._callbacks[on_action].values():
                    f(*args, **kw)
            fed.__doc__ = fed_docstring.format(on_action=on_action)
            fed.__name__ = actioned
            dct[actioned] = fed

            def disf(self, cid):
                try:
                    del self._callbacks[on_action][cid]
                except KeyError:
                    pass
            disf.__doc__ = disf_docstring.format(on_action=on_action)
            disf.__name__ = disconnect
            dct[disconnect] = disf

        return super(ActionableMeta, meta).__new__(meta, name, bases, dct)


class Actionable(object):
    """Class for managing callbacks functions.

    Populates the class with functions for registering callbacks (on_ACTION),
    un-registering callbacks (disconnect_ACTION), and calling the registered
    callback function (ACTIONED).

    Subclasses must define a class attribute ACTIONS that contains a list of
    tuples.  Each tuple should be three elements long and contain the names of
    the on_ACTION, ACTIONED, and disconnect_ACTION functions.
    """
    __metaclass__ = ActionableMeta

    def __init__(self):
        self._callbacks = defaultdict(dict)
        self.cid = 0
