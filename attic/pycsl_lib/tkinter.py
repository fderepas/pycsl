"""PyCSL mock for Python's tkinter module — Interface to Tcl/Tk for graphical user interfaces."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def Tcl(screenName: int, baseName: int, className: int, useTk: int) -> int:
    """Mock: The :func:`Tcl` function is a factory function which creates an object much like that created by the :class:`Tk` class, ..."""
    return 0
