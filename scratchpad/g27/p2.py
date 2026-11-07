r"""P2 (a2) — a def's BODY is outside the module-executed region; the def is CALLED at
module scope and patches a CLASS CONSTANT (a value that types)."""
_ = 0  # anchor


class C:
    N = 3


def patch(k) -> None:
    k.N = 5


patch(C)


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return C.N
