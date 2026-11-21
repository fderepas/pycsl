from typing import Tuple

# route #538 advice probe: g1105/bf1047 with the comparison moved to components declared
# with a totally ordered type (`t[0] < u[0]` of `Tuple[int, int]`); expected to VERIFY.


#@ no_exception \all
def f(t: Tuple[int, int], u: Tuple[int, int]) -> int:
    return 1 if t[0] < u[0] else 0
