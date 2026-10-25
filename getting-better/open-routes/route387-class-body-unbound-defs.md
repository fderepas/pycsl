# OPEN ROUTE #387 — CLASS-BODY DEFS CPython NEVER BINDS AS ATTRIBUTES
**Status: OPEN, Severity 1.** Red-team round 30 (2026-10-25, probes around #373-#380 and route #226 increment 2c); driver-reproduced on main a064a298f (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt30/driver-repro.txt`).
Witnesses `witnesses-r387/`: `h07_class_body_global_decl.py`, `h10_class_body_if_false_def.py`, `h21_class_body_while_false_def.py`, `h22_global_init_decl.py`, `h24_if_version_def.py`, `h25_class_body_try_def_raises.py`, `h26_global_method_decl_invariant.py`.

`global get` / `global __init__` in a class body, a def under `if False:` / `while False:` / `if sys.version_info < (3, 0):`, or after a raise inside `try`: one binding site each, so #377's bound-twice rule never fires; the def is modelled as a method. CPython AttributeError.

Repair: Module 3: refuse `global` / `nonlocal` in a class body naming a member; refuse (or treat as possibly unbound) any def / class / annotated member nested under a compound statement in a class body.
