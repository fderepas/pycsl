# OPEN ROUTE #340 — A NESTED def's DEFAULT ARGUMENT THAT IS A BARE NAME IS EVALUATED AT CALL TIME (Python: at def time)
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 24; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r340/`: the lifted `g(y)` is called as `(g !x)` after `x` was rebound (c04; c12 outer parameter; c20 `x += 1`; c36 ZeroDivisionError under
no_exception). Route #273's check accepts a Name default as "literal".
Repair: a nested def's default expressions are evaluated ONCE at def execution: bind them to fresh immutable names at the def site (in
Python order) and use those at calls, or refuse any non-literal (incl. bare-name) default of a nested def.
