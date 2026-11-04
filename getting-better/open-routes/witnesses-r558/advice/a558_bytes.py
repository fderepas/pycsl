# advice probe (route #558): witness g1400/da1296 declaring the container as holding bytes.
from typing import List


#@ no_exception \all
def f(k: int, s: str) -> int:
    xs: List[bytes] = []
    xs.append(bytes(2))
    return len(xs)
