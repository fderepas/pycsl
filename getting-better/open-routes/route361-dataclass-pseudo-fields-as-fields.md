# OPEN ROUTE #361 — DATACLASS `InitVar` / `KW_ONLY` PSEUDO-FIELDS ARE COUNTED AS STORED FIELDS
**Status: OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r361/`: `r23_initvar_read_k.py`, `r26_kw_only_sentinel_read.py`, `r29_initvar_arith_ensures.py`.

`k: InitVar[int]` and `_: KW_ONLY` join the synthesized field set (ClassVar is correctly excluded), so route #347's definite-assignment check credits them: reading `d.k` / `d._` under no_exception proves (r29 even proves `\result == 5`); CPython AttributeError.

Repair: Exclude `InitVar[...]` and `KW_ONLY` (string and `dataclasses.` spellings) from the dataclass field set and record type, like ClassVar.
