from typing import Dict, Any

#@ no_exception TypeError
#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    s = {m.get("a")}
    return 1
