# Advice probe (route #438, PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM): witness 6601 with the advice
# followed -- the hashed tuple declared with its components, `Tuple[int, str]`. Expected: VERIFIES.
from typing import Tuple


#@ no_exception \all
#@ ensures \result == n + 1
def f(t: Tuple[int, str], n: int) -> int:
    s = {t}
    return n + 1
