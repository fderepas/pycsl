# OPEN ROUTE #367 — ENUM MEMBERSHIP IGNORES `_ignore_` AND PRIVATE-NAME RULES
**Status: OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r367/`: `e18_ignore.py`, `e29_ignore_attr.py`, `e30_private_name_not_member.py`, `e33_ignore_string_form.py`.

Names listed in `_ignore_` (list or string form) and private `__B` names are treated as members by routes #355/#356: `C(2)`, `C(1)`, `C.B` admitted; CPython ValueError / AttributeError.

Repair: Build the member set as Enum does: drop `_ignore_` names (refuse a non-literal `_ignore_`), private `__x`, sunder/dunder names, descriptors and `nonmember(...)`.
