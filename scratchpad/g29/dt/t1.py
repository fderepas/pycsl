r"""lemma proving a false general fact"""
from typing import List
_ = 0  # anchor


#@ lemma
#@ requires n >= 0
#@ ensures n * n >= n
def sq_ge(n: int) -> None:
    pass


#@ ensures \result == 0
def probe() -> int:
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
