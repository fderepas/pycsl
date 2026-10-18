# OPEN ROUTE #274 — WRITE EFFECTS OF CALLS INSIDE COMPREHENSIONS / GENERATOR EXPRESSIONS VANISH
**Status: OPEN (gen #36, 2026-10-18), Severity 1.** Red-team round 5; driver-reproduced at HEAD (y10/y11 rc=0; CPython 5).
Witnesses `witnesses-r274/` (genexp first iterable, sum(genexp), listcomp, dictcomp, setcomp). `push(c)` with
`assigns c.v` inside a comprehension lowers to `list_comp 0` etc.; #269 refuses only raising/precondition callees and
models diverging ones. Repair: a call with a non-empty frame (any `assigns`/writes) inside an opaque comprehension must be
refused (or its frame havocked at the comprehension).
