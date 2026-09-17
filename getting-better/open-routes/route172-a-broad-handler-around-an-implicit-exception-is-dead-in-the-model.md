# ROUTE #172 — route #171's residual: `except Exception` / bare around an implicit exception

**Status: REPAIR DRAFTED by gen #29 (worktree wtS, on top of #171).** Severity 1. Generator:
carrier-rerun on the #171 draft (its own recorded residual).

## Measured on the #171 draft (and at `927e899f`)

    xs: List[int] = []; try: v = xs[0] except Exception: return 9; return v * 0   PROVED `== 0` (CPython 9)
    try: v = int("1.5") except Exception: return 9; return v * 0                  PROVED `== 0` (CPython 9)

(A bare `except:` is refused at HEAD.)

## Repair (draft)

The #171 widening also applies to `Exception`, `BaseException` and bare handlers. #171's first
measurement refused 7 mirror files with broad handlers — BEFORE the claim gate (non-trivial
`ensures` or an in-body assertion) existed; with the gate, emission is corpus-inert except #170's
own XFAIL witness 1585, python-reference and mirrors inert. Witnesses 1592, 1593 (XFAIL),
1594 (PASS). Fast planes 19/19, conformance, sync green.

## Carrier folded in

The claim gate itself (from #171) missed loop specs: an `ensures True` function whose
`loop invariant r == 0` holds only on the dead-handler path PROVED (CPython r == 9). Loop
`invariants`/`variants` now count as claims (functions.py and the preamble gate). Still inert on
corpus/pyref/mirrors. Witness 1595 (XFAIL). A frame claim needs no gate: Why3 infers the handler
path's writes (measured: `assigns \nothing` with a handler store is refused at HEAD).

## Still open

Unknown / trusted callees inside a handled `try` are refused only when the widened set triggers
route #161's whitelist; implicit exceptions outside the 5 modelled classes (TypeError,
AttributeError, ...) are not modelled at all.
