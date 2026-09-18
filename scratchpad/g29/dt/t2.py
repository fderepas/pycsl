r"""inductive predicate misuse"""
from typing import List
_ = 0  # anchor


#@ inductive even(n: int):
#@   case zero: even(0)
#@   case step: forall k: int. even(k) ==> even(k + 2)


#@ requires even(3)
#@ ensures \result == 0
def probe() -> int:
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
