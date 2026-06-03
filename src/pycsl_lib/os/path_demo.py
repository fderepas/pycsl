"""Demo driver for os.path pure path algebra stubs.

Exercises join, dirname, basename, splitext, normpath.
Verified end-to-end (no \\trusted) via
``pycsl src/pycsl_lib/os/path_demo.py``.
"""
from .path import join, dirname, basename, normpath, splitext


#@ requires a >= 0 and b >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_join(a: int, b: int) -> int:
    """Join two path segments; returns non-negative path handle."""
    return join(a, b)


#@ requires path >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_dirname(path: int) -> int:
    """Return the directory portion of path."""
    return dirname(path)


#@ requires path >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_basename(path: int) -> int:
    """Return the final component of path."""
    return basename(path)


#@ requires path >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_normpath(path: int) -> int:
    """Normalize path by collapsing redundant separators."""
    return normpath(path)


#@ requires path >= 0
#@ ensures \result == 0
#@ assigns \nothing
def demo_splitext(path: int) -> int:
    """Split path into (root, ext) pair; modeled as int 0."""
    return splitext(path)
