from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(d: Dict[int, int]) -> int:
    return len(d.keys(1))


if __name__ == "__main__":
    try:
        r = f({})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
