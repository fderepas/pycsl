r"""Test 9951 -- route #599 / lvQ PATH-RECEIVER (expected FAIL: PROVED at base 952bf7891 in the default model, full proof; REFUSED PYCSL-R7Q-EXT-PATH-RECEIVER at HEAD): the receiver of `.mkdir(..)` is a LOCAL bound to `str(p)` (a str, not a Path); CPython raises AttributeError, `argparse.ArgumentParser()` covers the handler; returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from __future__ import annotations
import argparse
from pathlib import Path


#@ ensures \result == 0
#@ assigns \nothing
def cli(p: Path) -> int:
    x = 0
    s = str(p)
    try:
        a = argparse.ArgumentParser()
        x = 1
        s.mkdir(parents=True, exist_ok=True)
    except AttributeError:
        return x
    return 0


if __name__ == "__main__":
    r = cli(Path("/tmp"))
    print("VIOLATION contract" if r != 0 else "result", r)
