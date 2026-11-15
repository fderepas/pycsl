r"""Test 9952 -- route #599 / lvQ PATH-RECEIVER (expected FAIL: PROVED at base 952bf7891 in the default model, full proof; REFUSED PYCSL-R7Q-EXT-PATH-RECEIVER at HEAD): `.write_text(..)` on a `str` parameter (CPython AttributeError) under an argparse-covered `except AttributeError`; returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from __future__ import annotations
import argparse
from pathlib import Path


#@ ensures \result == 0
#@ assigns \nothing
def cli(s: str) -> int:
    x = 0
    try:
        a = argparse.ArgumentParser()
        x = 1
        s.write_text("abc")
    except AttributeError:
        return x
    return 0


if __name__ == "__main__":
    r = cli("/tmp/u44-never")
    print("VIOLATION contract" if r != 0 else "result", r)
