"""Test 0989 — `with ... as v:` is REFUSED. The binding was DROPPED, and this is the
CTXBIND population `bin/check-dropped-mutation.py` has been ratcheting at 50 all along.

`_py_stmt_with` reads `stmt.body` and the `csl_critical_mutex` / `csl_acquires` markers.
It NEVER reads `stmt.items`. So the context-manager expression AND the `as v` binding both
vanish, and the body is inlined against the PRE-`with` value of `v`. Measured, before this
refusal:

    class CM:
        #@ ensures \result == 7
        def __enter__(self) -> int:
            return 7

    #@ ensures \result == 0                    <-- FALSE OF THE PROGRAM
    def f() -> int:
        v: int = 0
        with CM() as v:
            return v

    [+] Verification SUCCESS! All contracts formally proven.

Real Python returns 7. The emitted body was

    let v = ref 0 in  v := 0;  !v

`CM()` and `__enter__` are not in the model at all.

Carried into the IR as the additive field `with_bindings` and refused in Module 6's GENERIC
emission — the `nonlocal_writes` shape exactly, and for the same reason: a `\trusted` /
`\abstract` function emits as a bodyless `val` whose body is never lowered and must stay
exempt, and only that layer knows it.

A BARE `with <lock>:` has no binding and IS modelled, as a critical section. The refusal
keys on the `as` clause alone.

CENSUS: 62 `with ... as` sites across both corpora, the mirror, `src/pycsl_lib`, the live
emitter and `tests/`. Exactly ONE is inside a CONVERTED mirror method —
`pure_ast._Unparser.visit_Lambda`, whose `with self.buffered() as buffer:` was reading a
stale `buffer`; it is re-`\trusted` with this change. Two are `python-reference` syntax
coverage tests (0093, 0191), now `pycsl-expected: FAIL` — the treatment #34 gave
`python-reference/0111` for `except*`. `pycsl-reference` emission is BYTE-IDENTICAL across
all 820 files.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL


class CM:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        pass

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def __enter__(self) -> int:
        return 7

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __exit__(self, a: int, b: int, c: int) -> None:
        pass


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    v: int = 0
    with CM() as v:
        return v
