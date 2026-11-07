from typing import Any, Dict, List, Optional, Set, Tuple, Union

class K:
    def rpartition(self, a0: int) -> int:
        return 0


#@ no_exception \all
def f(s: str, t: str) -> int:
    return len(s.rpartition(t))


if __name__ == "__main__":
    try:
        r = f("a", "")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
