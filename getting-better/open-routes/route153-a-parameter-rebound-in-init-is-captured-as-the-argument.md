# ROUTE #153 — a constructor parameter REBOUND before the store is captured as the call's ARGUMENT

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-16), battery F' (with #152/#154). Witnesses 1515/1516/1520 (match-capture carrier).** Severity 1.
Generator: carrier-rerun (construction neighbourhood).

## Measured at `8b91a93b`

    class C:
        def __init__(self, k: int) -> None:
            k = k + 1          # or: k += 1
            self.x = k
    C(5).x     #@ ensures \result == 5   <-- PROVED; CPython 6    (record literal { x = 5 })

The capture rule keeps an RHS over the parameter set and substitutes each parameter NAME with the
call's argument — it never asks whether the body rebound the name first.

## Repair

Every name the constructor body binds (Store/Del `Name`, except-handler names, imports, `global` /
`nonlocal`; nested defs excluded) is removed from the capture set `pset`, so a store over it is not
captured and route #79 marks the field UNKNOWN. Witnesses 1515, 1516.

**Battery F' (every leg predicted and hit):** emission vs the #150/#151-closed tree 1161 -> 1170 0/0/0,
python-reference and mirrors inert; conformance 38/38 + 38/38; suite 3647/3665 same 18, zero XPASS;
planes --slow 34/34. (Battery F was stopped with no verdict read to fold the match-capture carrier and #154.)
