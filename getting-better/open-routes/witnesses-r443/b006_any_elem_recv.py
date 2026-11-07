from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(d: Dict[str, Any]) -> int:
    return len(d["a"].upper())


if __name__ == "__main__":
    try:
        r = f({"a": 1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
