from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(n: int, b: int) -> int:
    return int(n, b)


if __name__ == "__main__":
    try:
        r = f(5, 10)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
