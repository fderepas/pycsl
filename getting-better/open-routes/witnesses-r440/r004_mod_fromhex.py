from typing import Any, Dict, List, Optional, Set, Tuple, Union

def fromhex(a0: int) -> int:
    return 0


#@ no_exception \all
def f(s: str) -> int:
    return len(bytes.fromhex(s))


if __name__ == "__main__":
    try:
        r = f("zz")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
