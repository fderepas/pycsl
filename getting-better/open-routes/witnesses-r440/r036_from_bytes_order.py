from typing import Any, Dict, List, Optional, Set, Tuple, Union

class K:
    def from_bytes(self, a0: int, a1: int) -> int:
        return 0


#@ no_exception \all
def f(b: bytes) -> int:
    return int.from_bytes(b, "middle")


if __name__ == "__main__":
    try:
        r = f(b"a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
