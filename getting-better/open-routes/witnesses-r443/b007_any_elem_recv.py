from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(d: Dict[str, Any]) -> int:
    return d["a"].bit_length()


if __name__ == "__main__":
    try:
        r = f({"a": "s"})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
