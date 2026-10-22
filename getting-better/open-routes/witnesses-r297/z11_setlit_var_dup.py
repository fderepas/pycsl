from typing import List, Dict, Set, Tuple, Optional

#@ requires a == b
#@ ensures \result == 2
#@ assigns \nothing
def f(a: int, b: int) -> int:
    s = {a, b}
    return len(s)
if __name__ == "__main__":
    assert f(1, 1) == 2, f(1, 1)
