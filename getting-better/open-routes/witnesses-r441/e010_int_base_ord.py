from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(c: str) -> int:
    return int(ord(c[0]), 10) if len(c) > 0 else 0


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
