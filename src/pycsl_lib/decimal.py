"""PyCSL mock for Python's decimal module — Implementation of the General Decimal Arithmetic Specification."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/decimal.html#decimal.getcontext
#@ ensures True
def getcontext() -> int:
    """Mock: Return the current context for the active thread."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/decimal.html#decimal.setcontext
#@ ensures True
def setcontext(c: int) -> int:
    """Mock: Set the current context for the active thread to *c*."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/decimal.html#decimal.localcontext
#@ ensures True
def localcontext(ctx: int) -> int:
    """Mock: Return a context manager that will set the current context for the active thread to a copy of *ctx* on entry to the with..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/decimal.html#decimal.IEEEContext
#@ requires bits % 32 == 0
#@ requires bits > 0
#@ requires bits < 512
#@ ensures \result >= 0
def IEEEContext(bits: int) -> int:
    """Mock: Return a context object initialized to the proper values for one of the IEEE interchange formats.  The argument must be ..."""
    return 0
