# OPEN ROUTE #239 — `isinstance(<Any>, T)` IS KEYED ON THE VARIABLE'S NAME, NOT ITS VALUE

**Status: OPEN (gen #36, 2026-10-15), Severity 1.** Named as an unprobed residual by the #237/#238 repair
executor; the driver wrote the exploit and reproduced it at HEAD 4b049d8b.

## Witness (PROVED at HEAD rc=0; CPython `f(1, "s")` = 0)
`witnesses-r239/isinstance_any_rebound_name.py`:

    def f(x: Any, y: Any) -> int:      # ensures \result == 1  <-- PROVED
        a = 0
        if isinstance(x, int): a = 1
        x = y
        b = 0
        if isinstance(x, int): b = 1
        if a == b: return 1
        return 0

Emission: both tests are `(typeof_op 120) = 0` — `typeof_op` is a `val function` applied to a constant
derived from the NAME `x`, so rebinding `x` cannot change the answer. Control
`witnesses-r239/control_two_names.py` (`isinstance(y, int)` -> `typeof_op 121`) does not prove (Unknown).

## Repair direction
The type test must be a function of the VALUE (e.g. `typeof_op` applied to the lowered value when it is an
int-erased Any, or a fresh opaque bool per evaluation `(any bool)`), never of the name. Census every
`typeof_op` emission site and any other name-keyed opaque (hashing a variable NAME into an opaque
function's argument is the general shape — grep for it).
