from __future__ import annotations
if False:
    from pathlib import Path

#@ ensures \result == 1
#@ assigns \nothing
def f(s: str) -> int:
    try:
        p = Path(s)
        return 1
    except NameError:
        return 0


if __name__ == "__main__":
    print("result", f("a"))
