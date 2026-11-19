from typing import Any, Dict, List, Optional, Set, Tuple, Union

class K:
    def center(self, a0: int, a1: int) -> int:
        return 0


#@ no_exception \all
def f(s: str) -> int:
    return len(s.center(5, "ab"))


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
