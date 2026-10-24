# OPEN ROUTE #351 — A READ-ONLY VIEW ESCAPES THROUGH A MUTABLE-TYPED RETURN SLOT
**Status: OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r351/`: `n03_view_returned_as_list.py`.

`as_list(xs: Sequence[int]) -> List[int]: return xs` PROVES; a separate verified `poke(ys: List[int])` under `no_exception` stores `ys[0] = 5`; CPython `poke(as_list((1, 2)))` TypeError. Route #336's READONLY-VIEW-STORE covers stores on the parameter, not its escape. Weaker (two functions); the one-driver chain n09 FAILs.

Repair: Refuse returning (or storing / passing into a mutable-typed slot) a read-only view parameter where the declared type is a mutable container.
