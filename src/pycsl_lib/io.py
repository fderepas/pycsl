"""PyCSL mock for Python's io module — Core tools for working with streams.

Body-verified (no `\trusted`): each function's body provably satisfies its
contract, so the stub carries no reviewer-tagged trust markers.
"""
_ = 0  # anchor

# cite: https://docs.python.org/3/library/functions.html#open
#@ requires closefd != 0 or file >= 0
#@ ensures \result >= 0
def open(file: int, mode: int, buffering: int, encoding: int, errors: int, newline: int, closefd: int) -> int:
    """Mock: alias for the builtin open(); returns a non-negative handle."""
    return 0

# cite: https://docs.python.org/3/library/io.html#io.open_code
#@ ensures \result >= 0
#@ assigns \nothing
def open_code(path: int) -> int:
    """Mock: open `path` in binary read mode; returns a non-negative handle."""
    return 0

# cite: https://docs.python.org/3/library/io.html#io.text_encoding
#@ requires encoding >= 0
#@ ensures encoding != 0 ==> \result == encoding
#@ ensures \result >= 0
def text_encoding(encoding: int, stacklevel: int) -> int:
    """Mock: return the caller's `encoding` if given (non-zero), else a default
    (`1`, modelling 'utf-8'). Body-verified against the postcondition."""
    if encoding != 0:
        return encoding
    return 1
