from typing import Any, Dict, List, Optional, Set, Tuple, Union

class K:
    def to_bytes(self, a0: int, a1: int) -> int:
        return 0


#@ no_exception \all
def f(n: int) -> int:
    return len(n.to_bytes(2, "big"))


if __name__ == "__main__":
    try:
        r = f(-1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
