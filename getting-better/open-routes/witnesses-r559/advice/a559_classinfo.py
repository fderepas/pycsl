# advice probe (route #559): the classinfo tuple at the `isinstance` call itself
from typing import List


#@ no_exception \all
def f(k: int, xs: List[int]) -> int:
    return 1 if isinstance(k, (int, bool)) else 0
