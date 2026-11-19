from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(xs: List[Any]) -> int:
    return xs[0].bit_length()


if __name__ == "__main__":
    try:
        r = f(["a"])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
