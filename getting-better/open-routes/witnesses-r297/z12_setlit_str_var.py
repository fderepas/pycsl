from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 2
#@ assigns \nothing
def f(a: str) -> int:
    s = {"x", a}
    return len(s)
if __name__ == "__main__":
    assert f("x") == 2, f("x")
