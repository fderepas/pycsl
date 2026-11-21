# Route #545 advice probe: an `Optional[int]` parameter `v` (a value that may be None, as in
# witness g1234_am1207's `n += v`) narrowed first (`if v is not None:`) before `n += v` and
# `-v`, as PYCSL-R545-NONE-OPERAND advises.
from typing import Optional


#@ no_exception \all
def f(n: int, v: Optional[int]) -> int:
    if v is not None:
        n += v
        return -v
    return n


if __name__ == "__main__":
    print("result", f(1, None), f(1, 3))
