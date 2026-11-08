from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(n: int) -> int:
    k = 0
    for i, v in enumerate(n):
        k += 1
    return k


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
