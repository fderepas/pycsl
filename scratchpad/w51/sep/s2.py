# pycsl-flags: --memory-model hoare
"""Probe: `\separated` is answered `true` under value semantics (27th plane, arm
`_handle_separated_expr`+`_value_semantic`). Python ALIASES `b = a` — they are the SAME
list object — so a contract asserting they are separated is FALSE of the program."""
from typing import List


#@ requires len(a) >= 1
#@ ensures \result == 0
def probe(a: List[int]) -> int:
    b = a
    b[0] = 99
    if a[0] == 99:
        return 1
    return 0


if __name__ == "__main__":
    x = [0, 0]
    assert probe(x) == 1
