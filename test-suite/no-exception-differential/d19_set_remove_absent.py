# pycsl-flags: --memory-model hoare
from typing import Set
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    t: Set[int] = {1, 2}
    t.remove(5)
    return 0

if __name__ == "__main__":
    f()
