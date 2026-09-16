r"""F1 — deferral site 12 (core_ir_semantic.py:899): NR3 matches only `stmt == "Expr"`, so a
NoReturn call in ASSIGNMENT position is never reported dead, yet Module 6 still lowers it as
`(let _ = <call> in absurd)` and everything after it is vacuous."""
from typing import NoReturn

_ = 0  # anchor


#@ assigns \nothing
def fatal(n: int) -> NoReturn:
    while n >= 0:
        n = n + 1
    raise ValueError


#@ requires n >= 0
#@ ensures \result == 999
#@ assigns \nothing
def probe(n: int) -> int:
    x = fatal(n)
    return 0
