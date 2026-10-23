# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 1}
    del d[5]
    return 0


if __name__ == "__main__":
    f()
