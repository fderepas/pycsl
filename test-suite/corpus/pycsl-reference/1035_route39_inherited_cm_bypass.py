"""Test 1035 — ROUTE #39 negative witness (b): an INHERITED context-manager
protocol walks past route #38's refusal.

FALSE OF THE PROGRAM: `Base.__exit__` runs on the way out and sets `n` to 5, so
Python returns 5.

Route #38 collected "classes that define `__enter__`/`__exit__`" by scanning each
`ClassDef`'s OWN body. `CM` defines neither — it inherits both — so `CM` was never
in the set and the refusal never fired. At the parent commit ec7d1b81 this proved
`\result == 0` with the same `let c = { n = 0 } in (); c.n` emission as 1030 and
1033.

Two independent gaps in one resolution step (see 1033 for the other) is what
moved the refusal from a blacklist to a whitelist.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
class Base:
    def __enter__(self) -> int:
        return 0
    def __exit__(self, a: int, b: int, c: int) -> int:
        self.n = 5
        return 0


class CM(Base):
    def __init__(self) -> None:
        self.n: int = 0


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = CM()
    with c:
        pass
    return c.n
