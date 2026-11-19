from typing import Any, Dict, List, Set, Tuple

#@ ensures \result == 1
#@ assigns \nothing
def g(c: int, e: Dict[str, int]) -> int:
    d = e
    for i in range(c):
        d = {"a": 1}
    return len(d)
if __name__ == "__main__":
    assert g(0, {}) == 1
