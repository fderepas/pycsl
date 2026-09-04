"""Test 0999 — a NON-EMPTY TUPLE LITERAL bound to a local, then used as a guard, is
REFUSED. ROUTE #27; the same defect as 0997 and 0998.

`x = (1, 2)` emitted `x := 0`, so `if x:` was decided FALSE while Python's non-empty tuple
is truthy. Measured, before the refusal, on this body with `#@ ensures \result == 0`:

    [+] Verification SUCCESS! All contracts formally proven.

while Python returns 7.

THE CONTROL: the same tuple read BY INDEX, `if x[0] == 1:`, always FAILED correctly — the
projection off the erased local is abstract. Three shapes, three witnesses, one refusal in
`_to_bool`, and one rule worth carrying forward:

    AN ERASURE TO A LITERAL IS ONE `if` AWAY FROM A FALSE PROOF;
    AN ERASURE TO AN OPAQUE VALUE IS NOT.
    So probe an erasure by CONSUMING IT IN A GUARD, never by reading it.

That rule is what found routes #24, #25, #26 and #27. For #24 the field-read probe FAILED
and the site was nearly written off as fails-safe; only the truthiness test exposed it.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires True
#@ ensures \result == 0
def f() -> int:
    x = (1, 2)
    if x:
        return 7
    return 0


if __name__ == "__main__":
    print(f())
