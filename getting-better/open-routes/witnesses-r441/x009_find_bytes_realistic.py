from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(s: str, token: bytes) -> int:
    return 1 if s.find(token) >= 0 else 0


if __name__ == "__main__":
    try:
        r = f("abc", b"b")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
