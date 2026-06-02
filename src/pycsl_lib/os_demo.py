"""Formal driver for the os-like low-level API in `os.py`.

The `my_os_demo.py` analog: each function is a thin, annotated wrapper over a
low-level `os` call, with a contract discharged from the callee's `ensures`.
Verified end-to-end (no `\trusted`) via `pycsl src/pycsl_lib/os_demo.py`.

(Reconstructed after the per-phase rollback deleted the original untracked file;
mirrors the delegate's `demo_write` shape over the stub API.)
"""
import os


#@ requires path >= 0 and flags >= 0 and mode >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_open(path: int, flags: int, mode: int) -> int:
    """Open a path; returns a non-negative file descriptor."""
    return os.open(path, flags, mode)


#@ requires fd >= 0 and data >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_write(fd: int, data: int) -> int:
    """Write bytes to fd; returns byte count written (>= 0)."""
    return os.write(fd, data)


#@ requires fd >= 0 and n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_read(fd: int, n: int) -> int:
    """Read up to n bytes from fd; returns bytes read (>= 0)."""
    return os.read(fd, n)


#@ requires fd >= 0
#@ ensures \result == 0
#@ assigns \nothing
def demo_close(fd: int) -> int:
    """Close fd; returns 0."""
    return os.close(fd)


#@ requires fd >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_dup(fd: int) -> int:
    """Duplicate fd; returns a new non-negative descriptor."""
    return os.dup(fd)


#@ requires fd >= 0 and pos >= 0 and how >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_lseek(fd: int, pos: int, how: int) -> int:
    """Reposition fd; returns the resulting offset (>= 0)."""
    return os.lseek(fd, pos, how)


#@ requires path >= 0 and flags >= 0 and mode >= 0 and data >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_roundtrip(path: int, flags: int, mode: int, data: int) -> int:
    """Open → write → close → reopen → read → close; returns bytes read."""
    fd: int = os.open(path, flags, mode)
    os.write(fd, data)
    os.close(fd)
    fd2: int = os.open(path, flags, mode)
    n: int = os.read(fd2, data)
    os.close(fd2)
    return n
