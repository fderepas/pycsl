# OPEN ROUTE #285 — EXCEPTIONS INSIDE COMPREHENSIONS/GENEXPS: ONLY DIVISION AND SUBSCRIPT TRIGGERS ARE CHECKED
**Status: OPEN (gen #37, 2026-10-20), Severity 1.** Red-team round 7; driver-reproduced at 83aa79bd (p196/p211/p214 rc=0; CPython ValueError).
Witnesses `witnesses-r285/`. Under `no_exception \all`, `[str(x) for x in xs]`, f-string/repr elements, `",".join(str(x) for ...)`
(digit limit, #281), `[chr(x) ...]`/`{x: chr(x)}` (chr range), `[1 << x ...]`/`sum(1 << x ...)`/`[x >> n ...]` (negative shift) all
prove; the same operations outside a comprehension are caught (p206/p210/p213/p216). The comprehension refusal enumerates
ZeroDivisionError and IndexError/KeyError only. Repair: drive the comprehension check from the exception-trigger table itself
(every trigger row, present and future), not a hand list; census the trigger table against it.
