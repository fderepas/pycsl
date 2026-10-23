r"""F1b — NoReturn in RETURN position (also not `stmt == "Expr"`)."""
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
    if n > 1000000:
        return 0
    return fatal(n)
