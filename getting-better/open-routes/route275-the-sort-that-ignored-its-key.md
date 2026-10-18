# OPEN ROUTE #275 — `sorted(..., reverse=..., key=...)` IS MODELLED AS AN ASCENDING SORT
**Status: OPEN (gen #36, 2026-10-18), Severity 1.** Red-team round 5; driver-reproduced at HEAD (o07/o09 rc=0; CPython False).
Witnesses `witnesses-r275/`. Emission `sorted_1 xs` drops the keywords, and `sorted_1` ensures ascending order.
Repair: honour `reverse` (descending) and refuse/opaque any `key` (or keyword not modelled) — never drop keywords
(route #259 noted the generic path drops keyword args for every builtin: census all builtins).
