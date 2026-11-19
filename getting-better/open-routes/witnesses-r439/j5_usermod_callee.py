from typing import Any, Dict
import rt34helper

#@ no_exception \all
def f(m: Dict[str, Any]) -> int:
    return rt34helper.h(m)


if __name__ == "__main__":
    try:
        r = f({"a": [1]})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
