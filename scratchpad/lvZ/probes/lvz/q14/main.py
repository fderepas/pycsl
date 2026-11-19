from __future__ import annotations
import h


#@ ensures \result == 1
def f(s: str) -> int:
    t = s
    if h.first([s]) != t:
        return 0
    return 1


if __name__ == "__main__":
    print("result", f("a"))
