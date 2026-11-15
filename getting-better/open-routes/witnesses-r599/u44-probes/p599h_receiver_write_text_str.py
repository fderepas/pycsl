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
