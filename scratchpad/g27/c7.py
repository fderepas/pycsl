r"""C7 — carrier of MY OWN draft-3: `vars()` with an ARGUMENT is deliberately untouched
(`vars(self)` is an ordinary object dict). `vars(f)` is the module namespace."""
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


def g() -> None:
    vars(f).update({"N": 5})


g()
