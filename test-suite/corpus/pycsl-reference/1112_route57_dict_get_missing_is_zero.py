"""Test 1112 — ROUTE #57 negative witness (a): `d.get(k)` on a MISSING key was the
integer ZERO, not `None`.

FALSE OF THE PROGRAM: Python's `{1: 2}.get(5)` is `None`, and `None == 0` is False,
so `f` returns 0.

THE MAP WAS ALWAYS MODELLED FAITHFULLY AND THE READ WAS NOT. The emission is
`let d = ref (map_update_some (const (None: option int)) 1 2)` over a
`map 'k (option 'v)`, in which `None` is a real, distinct value. What erased it was
the read: `match Map.get !d 5 with | Some v_ -> v_ | None -> 0 end`.

THE ZERO WAS BORROWED FROM A PLACE ITS JUSTIFICATION DOES NOT REACH. It comes from
`_dv_missing_default`, whose docstring calls it the placeholder for a dict SUBSCRIPT
read, "proven dead under `#@ no_exception KeyError`". That is coherent for `d[k]`,
which RAISES on a missing key, so the arm really is unreachable and the value only
has to type-check. **`.get` never raises.** It is total and returns `None`, so
nothing can ever make this arm dead and the value it answers IS the model's answer
to an ordinary call.

The fix answers route #44's existing `pycsl_none` opaque instead. 1115 is the
positive control that the EXPLICIT-default form `d.get(k, v)` is untouched.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 2}
    if d.get(5) == 0:
        return 1
    return 0
