"""PyCSL mock for Python's curses.panel module — A panel stack extension that adds depth to  curses windows."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def bottom_panel() -> int:
    """Mock: Returns the bottom panel in the panel stack."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def new_panel(win: int) -> int:
    """Mock: Returns a panel object, associating it with the given window *win*. Be aware that you need to keep the returned panel ob..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def top_panel() -> int:
    """Mock: Returns the top panel in the panel stack."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def update_panels() -> int:
    """Mock: Updates the virtual screen after changes in the panel stack. This does not call :func:`curses.doupdate`, so you'll have ..."""
    return 0
