"""Test 1033 — ROUTE #39 negative witness (a): an ANNOTATED assignment walks
past route #38's refusal.

FALSE OF THE PROGRAM: `__exit__` runs on the way out and sets `n` to 5, so Python
returns 5.

Route #38 refuses a `with` whose context expression resolves to a class that
defines `__enter__`/`__exit__`. It resolved a bare NAME through a census of plain
`Assign` nodes only — so `c: CM = CM()`, which is an `AnnAssign`, bound nothing in
that census, `_bind38.get("c")` returned `None`, and the refusal never fired. At
the parent commit ec7d1b81 this proved, with the emitted body

    let c = { n = 0 } in
    ();
    c.n

— byte-for-byte route #38's own exploit, reached by changing one colon.

THE LESSON IS THE SHAPE, NOT THE NODE TYPE: #38 was a BLACKLIST over an
under-approximate resolution of "which class is this". The enumeration of ways to
name a value is open-ended, so the fix is a WHITELIST — once a file defines a
context-manager class at all, every `with` in it must be positively recognized as
a modelled form (an in-file `@contextmanager` generator, or a stdlib CM with no
value-model footprint) or it is refused. See 1034 and 1035.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
class CM:
    def __init__(self) -> None:
        self.n: int = 0
    def __enter__(self) -> int:
        return 0
    def __exit__(self, a: int, b: int, c: int) -> int:
        self.n = 5
        return 0


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c: CM = CM()
    with c:
        pass
    return c.n
