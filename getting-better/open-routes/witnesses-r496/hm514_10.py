from typing import Any, Dict, List


#@ ensures \result == 1
def g(n: int) -> int:
    q, r = divmod(5, n)
    return 1
