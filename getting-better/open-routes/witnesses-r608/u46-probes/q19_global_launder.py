from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

G: str = "q"

#@ assigns G
def setg(d: Dict[str, PyVal]) -> None:
    global G
    G = d.get("a") or "z"

#@ ensures \result == 1
#@ assigns \nothing
def h() -> int:
    if len(G) > 0:
        return len(G[0])
    return 1

if __name__ == "__main__":
    setg({"a": ["ab"]})
    r = h()
    print("VIOLATION contract" if r != 1 else "result", r)
