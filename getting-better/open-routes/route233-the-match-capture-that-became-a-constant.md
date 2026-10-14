# OPEN ROUTE #233 — THE `match` CAPTURE NAME THAT BECAME A MODULE CONSTANT

**Status: OPEN (gen #36, 2026-10-14), Severity 1.** Found by the route #232 executor (same
mechanism family: a binder the front end fails to scope falls through to `_handle_var_expr`'s
last-branch opaque `val constant`); driver reproduced at HEAD 1362a212.

## Witness (PROVED at HEAD; CPython f(0) returns -1)
`getting-better/open-routes/witnesses-r232/match_capture_read_as_constant.py`:

    #@ ensures \result == 0
    def f(x: int) -> int:
        r = 0; s = 0
        match x:
            case y: r = y
        match x + 1:
            case y: s = y
        return r - s

## Mechanism
The capture `y` is not bound by the `match` lowering; both reads of `y` resolve to ONE opaque
`val constant y`, so `r - s = y - y = 0`.

## Repair direction
Bind capture patterns (`case y:`, `case [a, b]:`, `case C(x=v):`, `case _ as v:`) to the subject
(or the matched component) as real locals, or refuse unbound captures fail-closed. Also audit the
opaque-constant fallback: it is sound ONLY for a genuine immutable module global — any other
unscoped name should be refused.
