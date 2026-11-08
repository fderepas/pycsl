r"""P11 — #136 sibling: CONSTANT exec whose text names a module-level DEF (not a builtin,
import or folded constant), so the #132 exec-token rule does not fire."""
_ = 0  # anchor


#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


#@ ensures \result == y - 1
#@ assigns \nothing
def dec(y: int) -> int:
    return y - 1


exec("inc = dec")


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
