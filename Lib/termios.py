"""PyCSL mock for Python's termios module — POSIX style tty control."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def tcgetattr(fd: int) -> int:
    """Mock: Return a list containing the tty attributes for file descriptor *fd*, as follows: ``[iflag, oflag, cflag, lflag, ispeed,..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tcsetattr(fd: int, when: int, attributes: int) -> int:
    """Mock: Set the tty attributes for file descriptor *fd* from the *attributes*, which is a list like the one returned by :func:`t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tcsendbreak(fd: int, duration: int) -> int:
    """Mock: Send a break on file descriptor *fd*.  A zero *duration* sends a break for 0.25--0.5 seconds; a nonzero *duration* has a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tcdrain(fd: int) -> int:
    """Mock: Wait until all output written to file descriptor *fd* has been transmitted."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tcflush(fd: int, queue: int) -> int:
    """Mock: Discard queued data on file descriptor *fd*.  The *queue* selector specifies which queue: :const:`TCIFLUSH` for the inpu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tcflow(fd: int, action: int) -> int:
    """Mock: Suspend or resume input or output on file descriptor *fd*.  The *action* argument can be :const:`TCOOFF` to suspend outp..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tcgetwinsize(fd: int) -> int:
    """Mock: Return a tuple ``(ws_row, ws_col)`` containing the tty window size for file descriptor *fd*. Requires :const:`termios.TI..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tcsetwinsize(fd: int, winsize: int) -> int:
    """Mock: Set the tty window size for file descriptor *fd* from *winsize*, which is a two-item tuple ``(ws_row, ws_col)`` like the..."""
    return 0
