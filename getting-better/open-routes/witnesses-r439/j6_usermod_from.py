from typing import Any, Dict
from rt34helper import h

#@ no_exception \all
def f(m: Dict[str, Any]) -> int:
    return h(m)


if __name__ == "__main__":
    try:
        r = f({"a": [1]})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
