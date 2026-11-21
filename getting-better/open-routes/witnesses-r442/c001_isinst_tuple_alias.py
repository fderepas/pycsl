from typing import Any, Dict, List, Optional, Set, Tuple, Union

T = (str, object)

#@ no_exception \all
def f(x: Optional[str], n: int) -> int:
    if isinstance(x, T):
        return len(x.upper())
    return 0


if __name__ == "__main__":
    try:
        r = f(None, 1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
