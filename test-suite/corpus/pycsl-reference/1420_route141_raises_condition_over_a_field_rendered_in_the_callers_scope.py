r"""Test 1420 — ROUTE #141: `_wrap_call_with_callee_raises_assert` substitutes actuals for FORMAL PARAMETERS, and `formal_params` has no `self`. A callee `raises ValueError when self.tag < 0` on an object whose `tag` is -1, called from a method of a DIFFERENT class whose own `tag` is 5, emitted `assert { not ((self.g_tag < 0)) }` — discharged from the CALLER`s field — and `no_exception ValueError` PROVED while CPython raises. A condition mentioning `self` no longer renders at all; the caller gets the honest `assert { false }`.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class H:
    tag: int

    def __init__(self) -> None:
        self.tag = -1

    #@ raises ValueError when self.tag < 0
    #@ assigns \nothing
    def f(self, k: int) -> int:
        if self.tag < 0:
            raise ValueError
        return k


class G:
    tag: int

    def __init__(self) -> None:
        self.tag = 5

    #@ requires self.tag >= 0
    #@ assigns \nothing
    #@ no_exception ValueError
    def caller(self, k: int) -> int:
        h = H()
        return h.f(k)