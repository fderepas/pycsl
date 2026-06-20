"""PyCSL mock for Python's pdb module — The Python debugger for interactive interpreters."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def run(statement: int, globals: int, locals: int) -> int:
    """Mock: Execute the *statement* (given as a string or a code object) under debugger control.  The debugger prompt appears before..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def runeval(expression: int, globals: int, locals: int) -> int:
    """Mock: Evaluate the *expression* (given as a string or a code object) under debugger control.  When :func:`runeval` returns, it..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def runcall(function_: int) -> int:
    """Mock: Call the *function* (a function or method object, not a string) with the given arguments.  When :func:`runcall` returns,..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_trace(header: int, commands: int) -> int:
    """Mock: Enter the debugger at the calling stack frame.  This is useful to hard-code a breakpoint at a given point in a program, ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def post_mortem(t: int) -> int:
    """Mock: Enter post-mortem debugging of the given exception or :ref:`traceback object <traceback-objects>`. If no value is given,..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pm() -> int:
    """Mock: Enter post-mortem debugging of the exception found in :data:`sys.last_exc`."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_default_backend(backend: int) -> int:
    """Mock: There are two supported backends for pdb: ``'settrace'`` and ``'monitoring'``. See :class:`bdb.Bdb` for details. The use..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_default_backend() -> int:
    """Mock: Returns the default backend for pdb. .. versionadded:: 3.14"""
    return 0
