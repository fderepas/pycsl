# ROUTE #153 — a constructor parameter REBOUND before the store is captured as the call's ARGUMENT

**Status: REPAIR DRAFTED by gen #29 (worktree wt152, with #152); battery F pending.** Severity 1.
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
