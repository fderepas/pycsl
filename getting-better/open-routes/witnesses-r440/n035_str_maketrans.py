from typing import Any, Dict, List, Optional, Set, Tuple, Union

class K:
    def maketrans(self, a0: int, a1: int) -> int:
        return 0


#@ no_exception \all
def f(a: str, b: str) -> int:
    return len(str.maketrans(a, b))


if __name__ == "__main__":
    try:
        r = f("ab", "c")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
