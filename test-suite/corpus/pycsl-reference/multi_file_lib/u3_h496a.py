from typing import Any, Dict, List


#@ ensures \result == 1
def g(s: str) -> int:
    y = s.index("z")
    return 1
