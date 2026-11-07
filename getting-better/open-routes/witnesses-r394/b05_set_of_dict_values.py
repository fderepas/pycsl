from typing import Any, Dict, List, Set, Tuple


#@ no_exception \all
def f(d: Dict[str, List[int]]) -> int:
    s = set(d.values())
    return len(s)


if __name__ == "__main__":
    try:
        print("no violation", f({"a": [1]}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
