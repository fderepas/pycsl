r"""Test 9940 -- route #599 / lvQ PATH-RECEIVER (expected FAIL: PROVED at L9 952bf7891, REFUSED PYCSL-R7Q-EXT-PATH-RECEIVER at HEAD): red team rt58 c01: `argparse.ArgumentParser()` covers `except AttributeError`, then `s.mkdir(..)` on a `str` parameter (the path model erases Path to str) -- CPython raises AttributeError there and `cli("abc")` returns 1 under `ensures \result == 0`
"""
# argv: --n 3
# pycsl-expected: FAIL
from __future__ import annotations
import argparse
from pathlib import Path


#@ ensures \result == 0
#@ assigns \nothing
def cli(s: str) -> int:
    x = 0
    try:
        p = argparse.ArgumentParser()
        x = 1
        s.mkdir(parents=True, exist_ok=True)
    except AttributeError:
        return x
    return 0


if __name__ == "__main__":
    q = Path("/tmp")
    r = cli("abc")
    print("VIOLATION contract" if r != 0 else "result", r)
