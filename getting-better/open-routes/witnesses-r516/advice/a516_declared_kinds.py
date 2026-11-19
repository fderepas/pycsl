# advice of PYCSL-R508 (route #516 branch) applied to 8199 (`for k, v in d.items(): w = k * v`): the operands' types declared and one numeric type
from typing import Dict


#@ no_exception \all
#@ ensures \result == 1
def f(d: Dict[int, int]) -> int:
    for k, v in d.items():
        w = k * v
    return 1


if __name__ == "__main__":
    print("result", f({2: 3}))
