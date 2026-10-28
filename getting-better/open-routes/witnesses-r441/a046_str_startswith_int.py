from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(s: str, t: int) -> int:
    return 1 if s.startswith(t) else 0


if __name__ == "__main__":
    try:
        r = f("a", 1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
