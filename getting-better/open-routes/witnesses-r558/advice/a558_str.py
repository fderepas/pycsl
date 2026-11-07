# advice probe (route #558): witness g1400/da1296 storing a value of the element kind, `xs.append("b")`.
from typing import List


#@ no_exception \all
def f(k: int, s: str) -> int:
    xs: List[str] = ["a"]
    xs.append("b")
    return len(xs)
