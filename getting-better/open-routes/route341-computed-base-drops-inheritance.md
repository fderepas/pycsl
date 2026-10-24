# OPEN ROUTE #341 — A CLASS BASE NOT WRITTEN AS THE CLASS'S OWN NAME SILENTLY DROPS THE INHERITANCE EDGE (Liskov/R5/#335/invariants skipped)
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 24; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r341/`: `Base = B; class S(Base)`, `class S(base())`, `class S(me.B if False else B)`, tuple-unpacked alias, `Base: Type[B] = B` — S becomes an
unrelated record: R5 skipped (o09), base `ensures \result == 1` broken by an override returning 2 (o10), no inherited invariant (o11), o13-o16.
Same-file (distinct from the declared imported-base residual).
Repair: resolve a base expression to a class of the file when it is a provable alias (Name bound once to a class); REFUSE any class whose base
expression is not a plain class name / resolvable alias / known builtin or library base (calls, conditionals, unpacked aliases, annotated
aliases, attribute chains that do not resolve).
