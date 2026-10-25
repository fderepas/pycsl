# OPEN ROUTE #362 — AN `InitVar` MAKES DATACLASS CONSTRUCTION OPAQUE AND DROPS THE INVARIANT GOAL
**Status: OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r362/`: `r07_initvar_post_init_inherited_import.py`, `r45_invariant_initvar_nodefault.py`.

With an InitVar the construction becomes opaque (as route #150 does for `__post_init__`) and no constructor-invariant goal is stated, so `invariant x >= 0` is assumed for every instance; CPython -1. Controls without InitVar / with defaults / init=False / kw_only / a verified `D(-5)` FAIL correctly.

Repair: Extend R346: refuse an invariant-carrying dataclass whose base closure declares any InitVar (or keep the construction non-opaque so the goal is stated).
