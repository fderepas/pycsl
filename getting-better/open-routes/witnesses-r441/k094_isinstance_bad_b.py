from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(x: int, t: Any) -> int:
    return 1 if (isinstance(x, t)) else 0


if __name__ == "__main__":
    try:
        r = f(1, 3)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
