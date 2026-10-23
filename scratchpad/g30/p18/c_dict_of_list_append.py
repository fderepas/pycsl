from typing import Dict, List


def g(d: Dict[str, List[int]]) -> int:
    d["k"].append(1)
    return 0


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, List[int]] = {"k": []}
    _ = g(d)
    return len(d["k"])
