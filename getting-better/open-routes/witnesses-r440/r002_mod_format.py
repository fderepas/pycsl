from typing import Any, Dict, List, Optional, Set, Tuple, Union

def format(a0: int) -> int:
    return 0


#@ no_exception \all
def f(n: int) -> int:
    return len("{} {}".format(n))


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
