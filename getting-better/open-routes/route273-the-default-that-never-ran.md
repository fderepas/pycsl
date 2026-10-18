# OPEN ROUTE #273 — DEF-TIME EVALUATION OF NESTED `def` DEFAULTS, `lambda` DEFAULTS AND NESTED `class` BODIES IS DROPPED
**Status: OPEN (gen #36, 2026-10-18), Severity 1.** Red-team round 5; driver-reproduced at HEAD (v09 rc=0 CPython 5; v04 rc=0
CPython ZeroDivisionError). Witnesses `witnesses-r273/` (v02 diverging default, v04/v07 raising defaults, v05/v09/v12/v13
effectful defaults, v06 lambda default diverging, v08 class-body raise, v10 nested class call, v03 decorator).
Mechanism: nested def/class lifting (and lambda lowering) discards default expressions / class-body statements, which Python
evaluates when the def/class statement runs; their effects/raises/divergence vanish. #269's vanished-call scan doesn't walk them.
Repair: evaluate default expressions/class-body statements at the definition point (or refuse any non-literal default /
non-trivial nested class body).
