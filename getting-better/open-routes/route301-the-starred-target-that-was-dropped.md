# OPEN ROUTE #301 — A STARRED ASSIGNMENT TARGET IS DROPPED BY THE FRONT END (the bound names keep their old values)
**Status: OPEN (gen #37, 2026-10-22), Severity 1.** Found by the r299 executor; driver-reproduced at 379d0f3a (rc=0 on main; CPython g([5]) == 5).
Witness `witnesses-r301/u1_starred_target.py`: `t = 0; [*h, t] = e; return t` under `requires len(e) == 1` proves `\result == 0`.
The starred unpack target is silently dropped, so `t` (and `h`) keep stale values. Repair: lower starred unpacking faithfully
(prefix/suffix slices of the source, length guard ValueError under no_exception) or REFUSE every Starred target (Assign, for,
with, comprehension); census every assignment-target shape the front end drops (starred, attribute/subscript in tuple targets,
nested, `*_`).
