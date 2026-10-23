"""Test 0985 — `del <list>[i]` is REFUSED. It is the LIST half of WL-05c, left open when
the dict half was fixed, and it is unsound for the same reason — and worse.

`_handle_del_subscript_stmt`'s own docstring calls the blanket no-op "UNSOUND ... a
severity-1 fail-OPEN" for dicts, then keeps it for "list `del a[i]`, a self-field, an
unknown receiver". Python's list `del` does not merely clear a slot: it SHIFTS every later
element left and SHRINKS the sequence, so a no-op model is wrong about EVERY index, not
just the deleted one. Measured, before this refusal:

    xs: List[int] = [1, 2, 3]
    del xs[0]
    return xs[0]
    #@ ensures \result == 1              <-- FALSE OF THE PROGRAM

    [+] Verification SUCCESS! All contracts formally proven.

Real Python returns 2. The emitted body was `(); 1` — the delete lowered to nothing, and
the read was then constant-folded against the untouched array.

WHAT LOCALISES IT: the DICT half correctly FAILS the analogous probe
(`d[1] = 7; del d[1]; return d.get(1, 0)` under `#@ ensures \result == 7`), because a local
dict delete lowers faithfully to `map_update_none`. Only the non-dict/set receiver reaches
the no-op.

REFUSED rather than modelled: a faithful `del` on an `array int` needs the LENGTH to be part
of the value model — the same capability route #13's list-mutator family needs — and a wrong
shift is worse than no shift.

CENSUS: 11 `del <subscript>` sites in the whole tree, and the dict/set ones take the faithful
or the reject branch above, so the corpus emission is BYTE-IDENTICAL across all 820 files,
the mirror is L3-tc 53/53, and `src/pycsl_lib` is unchanged. Corpus 0854-0857, the WL-05c
dict locks, all keep their expected verdicts.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[0]
    return xs[0]
