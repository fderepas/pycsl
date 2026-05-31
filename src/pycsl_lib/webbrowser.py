"""PyCSL mock for Python's webbrowser module — Easy-to-use controller for web browsers."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def open(url: int, new: int, autoraise: int) -> int:
    """Mock: Display *url* using the default browser. If *new* is 0, the *url* is opened in the same browser window if possible.  If ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def open_new(url: int) -> int:
    """Mock: Open *url* in a new window of the default browser, if possible, otherwise, open *url* in the only browser window. Return..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def open_new_tab(url: int) -> int:
    """Mock: Open *url* in a new page ('tab') of the default browser, if possible, otherwise equivalent to :func:`open_new`. Returns ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get(using: int) -> int:
    """Mock: Return a controller object for the browser type *using*.  If *using* is ``None``, return a controller for a default brow..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def register(name: int, constructor: int, instance: int, preferred: int) -> int:
    """Mock: Register the browser type *name*.  Once a browser type is registered, the :func:`get` function can return a controller f..."""
    return 0
