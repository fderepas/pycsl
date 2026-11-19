from typing import Any, Dict, List


#@ ensures \result == 1
def g(n: int) -> int:
    y = "{x}".format(n)
    return 1
