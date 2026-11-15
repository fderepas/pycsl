# argv: --n 3
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
