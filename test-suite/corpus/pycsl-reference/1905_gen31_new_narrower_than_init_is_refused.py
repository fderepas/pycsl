r"""Test 1905 — gen #31 (expected FAIL): a trivial `__new__` NARROWER than `__init__`.

`C(k)` is `type.__call__`, which passes the arguments to BOTH `__new__` and `__init__`.
A `__new__(cls)` beside an `__init__(self, n)` therefore makes EVERY construction a
TypeError in CPython:

    TypeError: Holder.__new__() takes 1 positional argument but 2 were given

The model built the record from `__init__` alone and never compared `__new__`'s arity with
the construction it was about to allow, so `#@ ensures \result == k` VERIFIED for a
function with no run at all. That is vacuity one level below where every vacuity
instrument in this repo looks: the clause is as contentful as a clause gets, and the proof
is empty because the normal exit it constrains does not exist.

This was found in `0496.py`, a driver the suite expected to PASS, by
`bin/check-corpus-contract-truth-args.py` once it stopped BREAKING out of its argument loop
on the first raise — a `break` cannot tell "raises on THIS argument" from "has no normal
exit on ANY". 0496 has since been repaired to `def __new__(cls, n: int)`, which both
verifies and RUNS.

THE RULE IS THE ONE THAT ADMITS NO CALL AT ALL: `__init__`'s MINIMUM required argument
count exceeds `__new__`'s MAXIMUM acceptable one. A `__new__` taking `*args`/`**kwargs`
accepts anything and is exempt (control `1906`); an `__init__` whose argument has a DEFAULT
still has a call that works, `Holder()`, and is exempt too (control `1907`). Refuse only
what could never be right.

`getting-better/open-routes/finding-a-contract-over-a-function-that-never-returns.md`
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Holder:
    def __new__(cls):
        return super().__new__(cls)

    def __init__(self, n: int):
        self.x = n


#@ requires k >= 0
#@ ensures \result == k
def grab(k: int) -> int:
    h = Holder(k)
    return h.x
