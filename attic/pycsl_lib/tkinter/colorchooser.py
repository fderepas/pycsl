"""PyCSL mock for Python's tkinter.colorchooser module — Color choosing dialog."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def askcolor(color: int) -> int:
    """Mock: Create a color choosing dialog. A call to this method will show the window, wait for the user to make a selection, and r..."""
    return 0
