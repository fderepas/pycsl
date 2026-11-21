from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ assigns \nothing
def load(d: Dict[str, PyVal]) -> Dict[str, PyVal]:
    return d

class C:
    #@ assigns self.cfg
    def __init__(self, d: Dict[str, PyVal]) -> None:
        self.cfg = load(d)

    #@ ensures \result == 0
    #@ assigns \nothing
    def kind(self) -> int:
        x = self.cfg.get("a") or "z"
        if isinstance(x, str):
            return 0
        return 1

if __name__ == "__main__":
    r = C({"a": 5}).kind()
    print("VIOLATION contract" if r != 0 else "result", r)
