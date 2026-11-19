from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(s: str, t: bytes) -> int:
    return s.find("a", t)


if __name__ == "__main__":
    try:
        r = f("a", b"x")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
