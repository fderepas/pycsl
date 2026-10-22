# OPEN ROUTE #302 — A PLAIN-NAME for TARGET OVER A NON-INDEX SEQUENCE, READ AFTER THE LOOP, KEEPS ITS PRE-LOOP VALUE (#36 residue)
**Status: OPEN (gen #37, 2026-10-22), Severity 1.** Reported by the r301 executor (route #36's recorded residue, never closed);
witness `witnesses-r302/residual_name_target_read_after.py`: `x = ""; for x in e: pass; return x` under `requires len(e) == 1`
proves `\result == ""` (CPython returns e[0]). Route #36 (relaunch #45) refused a `for` target read outside its loop only for
the index/range lowering; sequence/str/dict iteration still shadows the name inside the body and leaves the outer value stale.
Repair: refuse (or faithfully write back) every loop target read after its loop for EVERY iteration lowering (array/seq/str/
dict-keys/hval/R2b/enumerate/zip/items); flow-aware like #301 (a re-binding before the read kills staleness). Note the
`_handle_for_stmt` mirror stub has no raise: a refusal placed in Module 6 moves the trusted-raises ratchet (lesson d5) — prefer
the IR-level marker + Module 6 refusal pattern #301 used (kwarg_read precedent).
