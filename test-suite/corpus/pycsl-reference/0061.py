"""Test 0061 — Multi-file: relative import (from .mod import name)"""
_ = 0  # anchor
from .multi_file_lib.rel_helper import inc

#@ ensures \result == x + 1
def call_inc(x: int) -> int:
    """Calls inc via relative import."""
    return inc(x)

if __name__ == "__main__":
    print("PASS")
