"""PyCSL mock for Python's code module — Facilities to implement read-eval-print loops."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/code.html#code.interact
#@ ensures True
def interact(banner: int, readfunc: int, local: int, exitmsg: int, local_exit: int) -> int:
    """Mock: Convenience function to run a read-eval-print loop.  This creates a new instance of :class:`InteractiveConsole` and sets..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/codeop.html#codeop.compile_command
#@ ensures True
def compile_command(source: int, filename: int, symbol: int) -> int:
    """Mock: This function is useful for programs that want to emulate Python's interpreter main loop (a.k.a. the read-eval-print loo..."""
    return 0
