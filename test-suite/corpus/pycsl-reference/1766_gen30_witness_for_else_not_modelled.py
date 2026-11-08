r"""Test 1766 — WITNESS: `for ... else`, which the IR emitter would SILENTLY DROP.

The `else` clause of a loop runs exactly when the loop finished without `break`, and the
emitter reads only the loop body — so the clause would vanish from the model while staying
in the program. Refused with a rewrite (an explicit flag). One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result >= 0
def scan(n: int) -> int:
    i = 0
    for i in range(3):
        if i == n:
            break
    else:
        return 1
    return 0
