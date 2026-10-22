from typing import Any, Dict, List

PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    g: Dict[str, PyVal] = {"G": {"m": []}}
    h: Dict[str, PyVal] = {"G": {"m": []}}
    h, k = g, 1
    h["G"]["m"].append("x")
    return len(g["G"]["m"])

if __name__ == "__main__":
    assert f(0) == 0, f(0)
