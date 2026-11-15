from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

class K:
    #@ assigns \nothing
    def name(self, d: Dict[str, PyVal]) -> str:
        return d.get("n") or "anon"

    #@ no_exception \all
    #@ ensures \result >= 0
    #@ assigns \nothing
    def f(self, d: Dict[str, PyVal]) -> int:
        return len(self.name(d))


if __name__ == "__main__":
    try:
        print("result", K().f({"n": 5}))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
