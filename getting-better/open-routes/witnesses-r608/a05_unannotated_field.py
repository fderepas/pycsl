from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

class C:
    #@ assigns self.cfg
    def __init__(self, cfg: Dict[str, PyVal]) -> None:
        self.cfg = cfg

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
