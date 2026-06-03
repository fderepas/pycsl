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


# ── BytesIO — in-memory byte buffer (io.BytesIO) ────────────────────
# Content is a fixed-capacity `array int` of byte values. Python
# `bytes`/`bytearray` literals lower to arrays of code points, so a byte
# string written here carries its actual CONTENT (not an opaque hash, as a
# `str` literal would). Body-verified, 0 \trusted; run under `--memory-model
# hoare`. `roundtrip` is the verified write→read-back property: whatever bytes
# you write are returned unchanged (`\array_eq`), proven in pure Why3 from
# Array.blit / Array.sub.
#
# Honest limit: a separate `write(...)` then `getvalue()` across two calls is
# not yet chained (the caller can't see the buffer's field state evolve through
# an uninterpreted method stub); the single-call `roundtrip` carries the proof.
BYTESIO_CAP = 4096


#@ class invariant \length(self.buf) >= 4096
class BytesIO:
    def __init__(self):
        # Literal size (not BYTESIO_CAP) so record construction from a driver
        # captures the initial length — `_array_init_size` resolves a literal
        # `bytearray(N)`, not a module-constant reference.
        self.buf: list = bytearray(4096)

    # cite: https://docs.python.org/3/library/io.html#io.BytesIO.write
    #@ requires \length(data) <= 512
    #@ assigns self.buf
    #@ ensures \array_eq(\result, data)
    def roundtrip(self, data: list) -> list:
        """Write `data` into the buffer and return it as stored — the bytes
        read back equal the bytes written (content preserved)."""
        n = len(data)
        self.buf[0:n] = data
        return self.buf[0:n]

    # cite: https://docs.python.org/3/library/io.html#io.IOBase.close
    #@ ensures \result == 0
    #@ assigns \nothing
    def close(self) -> int:
        return 0
