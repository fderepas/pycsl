r"""Test 9713 -- lvQ open-world model (expected FAIL, refused PYCSL-R7Q-EXT-ARGPARSE-RECEIVER): a
parser passed in as a parameter is not an ARGPARSE LOCAL (its binding is not a modelled
`argparse.ArgumentParser(..)`), so the law-free handle model does not apply to it.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import argparse


#@ ensures \result == 0
#@ assigns \nothing
def add(p: argparse.ArgumentParser) -> int:
    p.add_argument("--k", help="k")
    p.add_argument("--k", help="k again")
    return 0


if __name__ == "__main__":
    try:
        add(argparse.ArgumentParser())
        print("result 0")
    except argparse.ArgumentError as e:
        print("VIOLATION contract", e)
