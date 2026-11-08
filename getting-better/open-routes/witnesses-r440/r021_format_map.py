from typing import Any, Dict, List, Optional, Set, Tuple, Union

class K:
    def format_map(self, a0: int) -> int:
        return 0


#@ no_exception \all
def f(s: str) -> int:
    return len("{x}".format_map({}))


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
