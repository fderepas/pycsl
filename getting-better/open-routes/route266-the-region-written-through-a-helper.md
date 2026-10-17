# OPEN ROUTE #266 — THE HAPPY REGION-INTEGRITY CHECK IS BYPASSED THROUGH A HELPER FUNCTION

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Red-team round 3; driver-reproduced at HEAD 13451c8d (rc=0; CPython
disk[600] = 9). Witness `witnesses-r266/h05_happy_write_via_helper.py`: region 512..2560 / writes self.disk outside
region / except _write_meta; non-exempt `evil` calls module fn `poke(self.disk, 600)` which does `a[i] = 9`.
Mechanism: the per-site check is injected only at direct `self.<field>[i] = ...` writes; the by-reference array write
inside the helper is unchecked (the docs claim callees are caught "at their own site" — only for self.<field> writes).
Repair: any call passing a protected field (or an alias) to a callee that may write its parameter must be refused or
carry the region obligation over the callee's frame (writes on the param).
