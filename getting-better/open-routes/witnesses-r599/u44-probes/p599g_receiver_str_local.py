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
