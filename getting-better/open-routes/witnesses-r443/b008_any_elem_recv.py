from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(d: Dict[int, Any]) -> int:
    return len(d[1].lower())


if __name__ == "__main__":
    try:
        r = f({1: 1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
