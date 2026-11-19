from typing import Any, Dict, List, Optional, Set, Tuple, Union

class K:
    def rpartition(self, a0: int) -> int:
        return 0


#@ no_exception \all
def f(b: bytes, t: bytes) -> int:
    return len(b.rpartition(t))


if __name__ == "__main__":
    try:
        r = f(b"a", b"")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
