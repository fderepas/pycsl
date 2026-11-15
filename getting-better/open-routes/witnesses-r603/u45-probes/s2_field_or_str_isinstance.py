from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


class C:
    def __init__(self, cfg: Dict[str, PyVal]) -> None:
        self.cfg: Dict[str, PyVal] = cfg

    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self) -> int:
        x = self.cfg.get("a") or "z"
        if isinstance(x, str):
            return 0
        return 1


if __name__ == "__main__":
    r = C({"a": 5}).f()
    print("VIOLATION contract" if r != 0 else "result", r)
