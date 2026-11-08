r"""P10 — #136 widen: DYNAMIC exec rebinding a module-level def at module scope."""
_ = 0  # anchor


#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


exec("in" + "c = lambda y: y - 1")


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
