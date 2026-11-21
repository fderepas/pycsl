"""Test 1030 — ROUTE #38 negative witness: a `with` over a user-defined context
manager drops the WHOLE protocol.

FALSE OF THE PROGRAM: `__exit__` runs on the way out and sets `n` to 5, so Python
returns 5.

At the parent commit c4233fed this proved `\result == 0` and the emitted body was

    let c = { n = 0 } in
    ();
    c.n

— the `with` collapsed to a unit, and NEITHER `__enter__` NOR `__exit__` appears.
Module 5 does not even carry the statement into the IR: a `with c: pass` arrives
at Module 6 as a bare `Pass`.

THE NEIGHBOURING RATCHET HAD BEEN COUNTING THE OTHER HALF FOR TWO WINDOWS.
`bin/check-dropped-mutation.py`'s CTXBIND = 51 records "`with ... as X` — the
binding is not read". The binding is the VISIBLE half; the protocol CALLS are the
half that carries the state change, and nothing counted or established those.

The refusal is keyed on a class that DEFINES `__enter__`/`__exit__`, which leaves
the 52 `@contextmanager` GENERATOR and builtin `with`s in the mirror alone — see
1031. Those are not thereby sound (`yield-erasure`'s ratchet of 2 records that
`_unparser.block` drops its indent/dedent) but they are unobservable while the
emitted `_unparser` record is empty, which is the precondition relaunch #43 wrote
down for converting `_Unparser.__init__`.
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
    c = CM()
    with c:
        pass
    return c.n
