r"""Test 9944 -- route #599 (expected FAIL: PROVED at L9, REFUSED PYCSL-R599-HANDLER-UNMODELLED-RAISER at HEAD): rt58 c12: the modelled `p.parse_args()` covers `except SystemExit`, then `sys.exit(k)` (a facade) raises it only in CPython; `cli(2)` returns 1 under `ensures \result == 0`
"""
# argv: --n 3
# pycsl-expected: FAIL
from __future__ import annotations
import argparse
import sys


#@ ensures \result == 0
#@ assigns \nothing
def cli(k: int) -> int:
    x = 0
    p = argparse.ArgumentParser()
    p.add_argument("--n", default="1")
    try:
        a = p.parse_args()
        x = 1
        sys.exit(k)
    except SystemExit:
        return x
    return 0


if __name__ == "__main__":
    r = cli(2)
    print("VIOLATION contract" if r != 0 else "result", r)
