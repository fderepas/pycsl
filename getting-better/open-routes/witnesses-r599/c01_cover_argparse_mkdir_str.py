# argv: --n 3
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
