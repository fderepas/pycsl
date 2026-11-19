from typing import Any, Dict, List, Optional, Set, Tuple, Union

class K:
    def rindex(self, a0: int) -> int:
        return 0


#@ no_exception \all
def f(s: str) -> int:
    r = s.rindex("z")
    return 0


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
