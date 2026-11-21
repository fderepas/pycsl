"""Test 0973 — `try ... except*` is REFUSED, because dropping it PROVED A FALSE
POSTCONDITION.

`Module5_IREmitter._PY_STMT_HANDLERS` has no entry for `ast.TryStar`, and
`_py_stmts_to_ir` dispatches with `if handler_name is not None: ... elif Match:` and NO
`else`. An exception-group `try` therefore vanished ENTIRELY — body, handlers, `else` and
`finally` — and nothing in the pipeline said so. Measured, before the refusal:

    #@ ensures \result == 1                    <-- FALSE OF THE PROGRAM
    def f() -> int:
        x: int = 1
        try:
            x = 2
        except* ValueError:
            x = 3
        return x

    [+] Verification SUCCESS! All contracts formally proven.

The emitted body was `let x = ref 0 in x := 1; !x`. Real Python returns 2.

Modelling `except*` needs ExceptionGroup splitting semantics — a value-model feature, not a
normalization — so the honest answer is a loud refusal, exactly as for `for ... else`.
CENSUS at the time of writing: 2 in `python-reference` (0111, 0187 — 0187 was already
`pycsl-expected: FAIL`), 0 in `pycsl-reference`, 0 in the mirror, 0 in `src/pycsl_lib`,
0 in the live emitter.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    x: int = 1
    try:
        x = 2
    except* ValueError:
        x = 3
    return x
