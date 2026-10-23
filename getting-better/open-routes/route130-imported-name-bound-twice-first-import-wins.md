# ROUTE #130 — an IMPORTED name bound a second time keeps the FIRST import in the model

**Status: CLOSED AND FULLY GATED by gen #25 (2026-09-15), battery-A (cheap legs, emission vs HEAD byte-inert in all three, suite 3503/3521 same 18 0 XPASS, planes 34/34 — every leg predicted and hit).**
**Severity: SEV-1. Second-order (carrier of #118/#119 rule (1), which keyed on this file's defs, and #124, which keyed on star imports).**

## MEASURED at HEAD `65237fdb` (each PROVES, CPython contradicts)
- `from plainlib import inc` (+1) then `from starlib import inc` (-1): `inc(3) == 4` proved; CPython 2.
- `from plainlib import inc` then module `inc = plainlib.dec`: `inc(3) == 4` proved; CPython 2.
- `import plainlib as m` then `import starlib as m`: `m.inc(3) == 4` proved; CPython 2.
- `FLAG = 0; if FLAG == 1: from starlib import inc / else: from plainlib import inc`: `inc(3) == 2` proved (the
  textually first import); CPython 4.
- module `from plainlib import inc`, `f(): from starlib import inc; return inc(3)`: `== 4` proved; CPython 2.
Faithful (FAIL-CLOSED): an explicit import after a star import; `from plainlib import dec as abs`.

## REPAIR (Module3_Weaver.process, the #130-#133 block)
Per scope (module, class body, function body): a name with an import binding site and any other binding site of a
different key (another import of a different object, a def/class, a store) is refused; a function-local import of a
name the module binds differently is refused. `import os.path` and `import os` share the key `import os`.
CENSUS: witness 1342 (already refused), pycsl_lib json/tool.py try-import fallback (not ingested), agents (not ingested).
Witnesses 1362, 1363, 1364; positive control 1373 (identical local import still proves).
