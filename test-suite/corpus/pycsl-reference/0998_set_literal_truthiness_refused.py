"""Test 0998 — a NON-EMPTY SET LITERAL bound to a local, then used as a guard, is REFUSED.
ROUTE #26; the same defect as 0997 and 0999.

`s = {1, 2, 3}` emitted `let s = ref 0 in` with NO STORE AT ALL — the assignment simply
vanished — so `if s:` was decided FALSE while Python's non-empty set is truthy. Measured,
before the refusal, on this body with `#@ ensures \result == 0`:

    [+] Verification SUCCESS! All contracts formally proven.

while Python returns 7.

THE CONTROL: the same set with a MEMBERSHIP test, `if 1 in s:`, always FAILED correctly —
membership routes through a modelled path, truthiness through the erased local. So the
value was never the problem; the guard was.

WORTH RECORDING ABOUT THE INSTRUMENTS: `bin/check-dropped-mutation.py` classifies an
assignment by its TARGET shape, so this statement counts as HANDLED ("Assign -> Name")
even though the store never happens. That gate cannot see a mutation dropped because of
its RHS.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires True
#@ ensures \result == 0
def f() -> int:
    s = {1, 2, 3}
    if s:
        return 7
    return 0


if __name__ == "__main__":
    print(f())
