from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(s: str) -> int:
    return round(s)


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
