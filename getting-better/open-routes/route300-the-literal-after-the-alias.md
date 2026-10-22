# OPEN ROUTE #300 — A LITERAL REBINDING AFTER A NON-LITERAL FIRST BINDING REGISTERS A FIXED FOLD SIZE (#297 residual)
**Status: OPEN (gen #37, 2026-10-22), Severity 1.** Red-team round 10; driver-reproduced at 2cef1801 (2 probes rc=0; CPython violates).
Witnesses `witnesses-r300/`: `d = e; if c == 1: d = {"a": 1}; return len(d)` proves `\result == 1` (CPython g(0, {}) = 0, j04); loop
variant k04. The fold registration in src/pycsl/module6_whyml/types.py (~88-100) blacklists a rebound name only when its FIRST
binding was a literal; a later literal binding registers size/elements that are then used on every path. Route #297's residual (1).
Repair: register a fold only for a name bound EXACTLY ONCE (single static binding, not in a loop/branch, never re-bound / aliased
/ mutated), otherwise blacklist; census all binding forms (params, aliases, loops, branches, augmented assignment, del, walrus,
for-targets, with-as, except-as) and every fold consumer (len, subscript, truthiness, sum, in).
