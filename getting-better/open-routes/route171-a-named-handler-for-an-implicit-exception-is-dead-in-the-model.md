# ROUTE #171 — a handler for an implicit exception the model says cannot occur is dead code

**Status: REPAIR DRAFTED by gen #29 (worktree wtR, on top of #170).** Severity 1. Generator: carrier
of #170 (other implicit exceptions caught in the same function).

## Measured at `4c2ded03`

    xs: List[int] = []
    try: v = xs[0]
    except IndexError: return 9
    return v * 0                     #@ ensures \result == 0   PROVED   (CPython 9)

    try: v = int("1.5")
    except ValueError: return 9
    return v * 0                     #@ ensures \result == 0   PROVED   (CPython 9)

Without `no_exception`, implicit raises are ambient: the empty literal is a 1024-cell placeholder
array (its read cannot fail), `int(<str>)` is an opaque `str_to_int` that never raises. Harmless
while the exception would escape; a handler makes it an observable control-flow path, and the model
erased it. Refused at HEAD: in-bounds-faithful list reads, string index, modulo/float division by
zero, `chr(-1)`, `list.index`, `str.index`, `max([])`, assert failures (pipeline refusal).

## Repair (draft)

`_reset_function_state` (trusted): when the function makes a claim (non-trivial `ensures`, route
#70's test, or an in-body assertion) and a `try` has a NAMED handler whose builtin class covers one of
the modelled implicit exceptions (IndexError, KeyError, ValueError, ZeroDivisionError, StopIteration;
by name or via LookupError/ArithmeticError...), the function is checked as if it declared
`no_exception` for those — every such operation must be proved not to raise (routes #159/#160/#161
obligations and refusals), so a proof implies the handler really is dead. Local: the function's
emitted contract is untouched; a callee's EXPLICIT `raises` keeps using the declared set
(`_wrap_call_with_callee_raises_assert`, `callee_escaping`), so a raised-and-caught callee exception
is still modelled faithfully (1302, 0449 re-prove). `_scan_preamble_needs` emits the predicate
vocabulary for such functions. A dict read under #170's raising model skips the presence assert.
Emission: corpus 12 + python-reference 3 MOVED (predicate definitions only; every PASS one re-proved),
mirrors inert. Witnesses 1588–1590 (XFAIL), 1591 (PASS).

## Open residual (recorded)

`except Exception` / `BaseException` / bare handlers are NOT widened: measured, doing so refused 7
self-annotate mirror files whose verified functions (`ensures True`) wrap trusted callees; even with
the claim gate, a caught `Exception` around a placeholder read with a real claim still proves.
Also: implicit exceptions outside the 5 modelled classes (TypeError, AttributeError) and unknown /
trusted callees inside a named handler (assumed not to raise, the #161 assumption).
