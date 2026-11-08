# Route #561 advice probe: dx1200 (`sum(1 for x in p)` of a dataclass `p: P`) with the advice
# followed -- iterate a container: `sum(1 for x in xs)` of `xs: List[int]`.
from typing import List
from dataclasses import dataclass


@dataclass
class P:
    a: int


#@ no_exception \all
def f(k: int, p: P, xs: List[int]) -> int:
    return sum(1 for x in xs)


if __name__ == "__main__":
    print(f(1, P(1), [1, 2]))
