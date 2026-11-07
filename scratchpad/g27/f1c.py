r"""F1c — a NoReturn function that DOES return: the annotation is a lie and NR2a is supposed
to catch it. Here the loop is bounded, so CPython returns normally."""
from typing import NoReturn

_ = 0  # anchor


#@ assigns \nothing
def fatal(n: int) -> NoReturn:
    if n >= 0:
        raise ValueError
    return


#@ ensures \result == 999
#@ assigns \nothing
def probe() -> int:
    fatal(-1)
    return 0
