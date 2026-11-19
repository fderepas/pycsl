r"""lemma with false body"""
from typing import List
_ = 0  # anchor


#@ lemma
#@ ensures 1 == 2
def bad() -> None:
    pass


#@ ensures \result == 0
def probe() -> int:
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
