"""PyCSL mock for Python's pty module — Pseudo-Terminal Handling for Unix."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def fork() -> int:
    """Mock: Fork. Connect the child's controlling terminal to a pseudo-terminal. Return value is ``(pid, fd)``. Note that the child ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def openpty() -> int:
    """Mock: Open a new pseudo-terminal pair, using :func:`os.openpty` if possible, or emulation code for generic Unix systems. Retur..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spawn(argv: int, master_read: int, stdin_read: int) -> int:
    """Mock: Spawn a process, and connect its controlling terminal with the current process's standard io. This is often used to baff..."""
    return 0
