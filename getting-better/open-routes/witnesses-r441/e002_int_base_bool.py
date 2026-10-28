from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(x: bool) -> int:
    return int(x, 10)


if __name__ == "__main__":
    try:
        r = f(True)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
