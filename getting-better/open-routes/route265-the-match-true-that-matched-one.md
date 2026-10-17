# OPEN ROUTE #265 — `case True:` / `case False:` / `case None:` MATCH BY EQUALITY, NOT IDENTITY

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Red-team round 3; driver-reproduced at HEAD 13451c8d (both rc=0; CPython 0).
Witnesses `witnesses-r265/`: m09 (`x = 1; match x: case True: return 1`), m10 (`case False` on `n: int`, n == 0).
PEP 634: the singleton literals True/False/None match by `is`. Emission `if (n = 0) then ...`. Route #90 (`is True` as
`=`) again, through the match-literal path.
Repair: singleton literal patterns lower like `is` (an int-typed subject never matches True/False; decide by the
static type or opaque), consistent with route #90's repair.
