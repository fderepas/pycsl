# ROUTE #173 — a tuple unpack's arity mismatch proves `no_exception ValueError`

**Status: REPAIR DRAFTED by gen #29 (worktree wtT, on top of #172).** Severity 1. Generator: hand
(unmodelled implicit exceptions caught, after #171/#172).

## Measured at `210033fe`

    #@ no_exception ValueError
    def probe() -> int:  s = "a"; a, b = s.split(","); return 0       PROVED  (CPython ValueError)

    try: a, b = s.split(",") except ValueError: return 9; return 0    PROVED `== 0` (CPython 9)
                                                                      (also on the #172 draft)

Unpacking a list local of the wrong length is refused at HEAD (t7m). No trigger row and no refusal
covers the arity of an unpack whose value has no static length, so the ValueError context — declared,
or widened by #171 from a handler — was discharged vacuously.

## Repair (draft)

`_reset_function_state` (trusted), gated on a ValueError context (`no_exception ValueError` / `\all`,
including #171's widening): a `TupleUnpack` is accepted only when its value is a tuple display of
exactly the target count or a call to a function of this file; otherwise PyCSLIRError. Emission
inert (corpus/pyref/mirrors). Witnesses 1596, 1597 (XFAIL), 1598 (PASS). Fast planes, conformance,
sync green.

## Carrier folded in (committed on wip/g29-r174)

`for a, b in ["abc"]` and `for k, v, w in d.items()` under `no_exception ValueError` PROVED (CPython
ValueError). A `For` with `tuple_targets` is accepted only over `enumerate(x)` / `.items()` with two
targets or `zip(...)` with one target per argument. Comprehension tuple targets and single-element /
string unpacks were already refused. Witnesses 1604-1605 (XFAIL). Emission unchanged.

## Also measured this batch (recorded, not routes)

Caught AttributeError on `None.x` (`Optional` local), OverflowError from `float(10**400)`,
UnicodeDecodeError from `bytes([255]).decode()` each PROVED the dead-handler value (CPython 9):
exception classes the model does not know at all. OPEN — candidates for the next route: a claiming
function with a handler whose class can only be reached by an UNMODELLED implicit exception
(AttributeError, TypeError, OverflowError, UnicodeError, ... — and `except Exception`, which also
catches those) must be refused. Uncaught AttributeError on None proves under the ambient convention.
