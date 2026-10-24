# OPEN ROUTE #337 — A USER CLASS WITH NO INSTANCE FIELDS IS LOWERED TO `type w = int` (user dunders ignored, int laws on its instances)
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 23; driver-reproduced on main (combined files rc=0; CPython violates each function — run the file to list them).
Witness `witnesses-r337/F2_fieldless_class_int.py` (3 functions): a user `__sub__` is ignored, `x - x == 0` proves; with `class P: pass`, `x < x` and
`x * 0 + 1` prove under no_exception \all (CPython TypeError). #249 only covers `==` on classes defining __eq__.
Repair: a fieldless user class must be an ABSTRACT type (no arithmetic/ordering), and operators on it must dispatch to the user dunder (or refuse).
