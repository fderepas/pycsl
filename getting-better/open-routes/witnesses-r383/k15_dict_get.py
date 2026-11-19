from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(m: Dict[str, D]) -> int:
    v = m.get("a")
    s = {v}
    return 1

if __name__ == "__main__":
    print(g({"a": D(1)}))
