r"""H1 — carrier of MY OWN #141 repair: the condition may name a MODULE GLOBAL, which the rule
allows because it denotes the same object in both scopes — unless the CALLER SHADOWS it with a
local of the same name."""
_ = 0  # anchor
LIMIT = -1


#@ raises ValueError when LIMIT < 0
#@ assigns \nothing
def f(k: int) -> int:
    if LIMIT < 0:
        raise ValueError
    return k


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    LIMIT = 5
    return f(k) + LIMIT
