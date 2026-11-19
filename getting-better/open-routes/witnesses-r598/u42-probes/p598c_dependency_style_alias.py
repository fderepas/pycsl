from typing import Any, Dict, List, Optional
import contextlib

VE = ValueError


#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    try:
        raise VE("a", q=1)
    except ValueError:
        return 1
    return 2


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
