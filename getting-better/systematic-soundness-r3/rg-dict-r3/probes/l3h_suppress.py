from typing import Dict, Any
from contextlib import suppress

#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    r = 2
    with suppress(TypeError):
        s = {m.get("a")}
        r = 1
    return r

if __name__ == "__main__":
    print(f({"a": [1]}))
