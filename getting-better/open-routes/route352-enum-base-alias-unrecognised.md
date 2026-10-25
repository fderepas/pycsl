# OPEN ROUTE #352 — AN ENUM WHOSE BASE IS AN IMPORT ALIAS (`from enum import Enum as E`) IS NOT RECOGNISED — MEMBERS KEEP INT LAWS
**Status: OPEN, Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r352/`: `e01_enum_import_alias.py`, `e28_intenum_import_alias_eq.py`.

Route #339 classifies an enum by the base's spelled name / attribute tail; `from enum import Enum as E; class C(E)` (e01: `x - x` under no_exception proves, CPython TypeError) and `IntEnum as IE` with a user `__eq__` (e28: `x == x` proves True, CPython False) fall outside the list, so `C` is a plain class and its members are ints.

Repair: Resolve base names through the file's imports (`from enum import X as Y`, `import enum as e`); refuse a class whose base is an imported name the check cannot classify.
