from typing import Dict, Optional

#@ no_exception \all
def f(d: Dict[str, Optional[str]]) -> int:
    return len(" ".join(d.values()))


if __name__ == "__main__":
    try:
        r = f({"a": None})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
