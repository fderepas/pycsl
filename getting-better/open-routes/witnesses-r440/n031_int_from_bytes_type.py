from typing import Any, Dict, List, Optional, Set, Tuple, Union

class K:
    def from_bytes(self, a0: int, a1: int) -> int:
        return 0


#@ no_exception \all
def f(s: str) -> int:
    return int.from_bytes(s, "big")


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
