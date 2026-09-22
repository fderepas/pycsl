r"""Test 1800 — MEASUREMENT (expected PASS): an EXPLICITLY-CALLED DUNDER loses its contract.

Found while auditing the `with ... as` refusal's advice, which used to say "Call
`__enter__` explicitly and assign its result". It does not work, and this file records the
shape so the gap has a name in the corpus rather than only in a commit message.

THE DIFFERENTIAL, two files identical except for ONE IDENTIFIER:

    def enter(self) -> int:  #@ ensures \result == 7   -> caller proves `\result == 7`
    def __enter__(self) -> int:  (same)                -> caller CANNOT

The emission says why: the dunder method is not emitted as a `let` at all, and its call
site becomes a CONTRACTLESS abstract op —

    val c___enter___0 () : int          (* no ensures, and no receiver argument *)

— so the caller learns nothing about the result. `__len__` behaves the same way and
`_enter_` (single underscores) does not.

SOUND, NOT UNSOUND: a contractless `val` is fresh and unconstrained at every call, so the
caller can prove LESS, never more. This file therefore states only what the model can
carry, and it PASSES. The claim it does NOT make — `\result == 7` — is the gap.

POPULATION (measured): 49 non-`__init__` dunder defs in the corpus, 10 in the mirror, 14
in the live tree, 8 in `src/pycsl_lib`; 31 / 6 / 8 / 2 explicit dunder CALLS respectively.
"""
# pycsl-expected: PASS
_ = 0  # anchor


class CM:
    def __init__(self) -> None:
        self.v: int = 7

    #@ ensures \result == 7
    def __enter__(self) -> int:
        return 7


#@ ensures \result >= 0
def read() -> int:
    c = CM()
    v = c.__enter__()
    if v >= 0:
        return v
    return 0
