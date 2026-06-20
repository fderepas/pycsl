"""PyCSL mock for Python's tty module — Utility functions that perform common terminal control operations."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def cfmakeraw(mode: int) -> int:
    """Mock: Convert the tty attribute list *mode*, which is a list like the one returned by :func:`termios.tcgetattr`, to that of a ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cfmakecbreak(mode: int) -> int:
    """Mock: Convert the tty attribute list *mode*, which is a list like the one returned by :func:`termios.tcgetattr`, to that of a ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setraw(fd: int, when: int) -> int:
    """Mock: Change the mode of the file descriptor *fd* to raw. If *when* is omitted, it defaults to :const:`termios.TCSAFLUSH`, and..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setcbreak(fd: int, when: int) -> int:
    """Mock: Change the mode of file descriptor *fd* to cbreak. If *when* is omitted, it defaults to :const:`termios.TCSAFLUSH`, and ..."""
    return 0
