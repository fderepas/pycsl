"""Formal driver for the io stub: thin annotated wrappers over io's stream
helpers, each contract discharged from the callee's `ensures`. Verified
end-to-end (no `\trusted`) via `pycsl src/pycsl_lib/io_demo.py`."""
import io


#@ requires file >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_open(file: int) -> int:
    """Open a file descriptor; returns a non-negative handle."""
    return io.open(file, 0, 0, 0, 0, 0, 1)


#@ requires path >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_open_code(path: int) -> int:
    """Open a path in binary read mode; returns a non-negative handle."""
    return io.open_code(path)


#@ requires encoding >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_text_encoding(encoding: int) -> int:
    """Resolve a text encoding; returns a non-negative result."""
    return io.text_encoding(encoding, 0)
