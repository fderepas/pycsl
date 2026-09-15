# ROUTE #122 — a `def` that is NOT a top-level module statement (inside `if`/`try`, or nested in
# another function) is hoisted into module scope, where the TEXTUALLY LAST def of a name wins

**Status: OPEN (found by gen #24, 2026-09-15).**
**Severity: SEV-1. Order 2** (carrier = #118's rule (1), whose module pass keys on top-level defs;
the dup-def control "last def wins" is only right for top-level duplicates).

## MEASURED at HEAD `7c9dede2` (each PROVES a claim CPython contradicts)
1. `FLAG = 1; if FLAG == 1: def inc -> y - 1  else: def inc -> y + 1`; `f() = inc(3)`, `\result == 4`
   PROVES; CPython 2. Only the else-branch def is emitted.
2. `try: def inc -> y - 1  except ImportError: def inc -> y + 1` (the fallback idiom): same, PROVES 4, CPython 2.
3. Module `inc -> y - 1` with its own contract; `other(): def inc(y): return y + 1; return inc(0)`;
   `f() = inc(3)` with `\result == 4` PROVES; CPython 2. The nested def of ANOTHER function replaced the
   module function (one `let inc (y) = (y + 1)` in the emission).

## REPAIR (to scope)
Refuse when a function name is defined by more than one `def` in the module and at least one of them
is not a top-level module statement (nested in a compound statement, or inside another function).
Census the four trees first (conditional defs, nested helper defs sharing a name).
Drivers: `scratchpad/g24/p1/if_def.py`, `try_def.py`, `nested_def_dual.py`.

## MORE CARRIERS (same day)
4. Two sibling functions each with a nested `def h` (+1 / -1): `a()`'s FALSE `\result == 2` PROVES — ONE hoisted
   `let h` (the last). CENSUS: 34 colliding nested defs in the MIRRORS (functions.py classify/rename/saw/refs_param,
   core_ir_semantic walk, ir_resolve _walk, types _scan, preamble _walk, statements rec), 2 in pycsl_lib
   json/encoder.py — so the nested-def arm CANNOT be a front-end refusal (it would refuse mirror files); it belongs
   where the lifted def is emitted (Module 6 `_emit_function`, the `nonlocal_writes` precedent).
5. `try: from starlib import inc / except ImportError: def inc` — the fallback def wins in the model, the import at
   runtime. PROVES a false `\result == 4`.
See also ROUTE #126 (the closure free variable of a lifted nested def becomes a global constant).
