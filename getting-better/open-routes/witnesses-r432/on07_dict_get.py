from typing import Optional
from typing import Dict

#@ no_exception \all
def f(d: Optional[Dict[str, int]]) -> int:
    return d.get("a", 0)


if __name__ == "__main__":
    try:
        r = f(None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
