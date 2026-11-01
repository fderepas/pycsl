# OPEN ROUTE #503 — ROUTE #498's SAME-OBJECT EXEMPTION FOLLOWS `b = a` TO THE NAME `a` BUT NOT TO A's BINDING TIME: AFTER `b = a; a = n + 1000` THE TWO OPERANDS SHARE THE ROOT NAME `a`, THE TEST IS SKIPPED, AND `a is b` IS DECIDED AS VALUE EQUALITY
**Status: OPEN, Severity 1.** Red-team round 45 (driver run #4, 2026-11-01, on 0d561a23b = main + the #496 / #498-#500 repairs under integration: 332 probes in g600-g607, 303 CPython-breaching, 15 confirmed in 5 families, all default mode; rt44's 139 pairs: 127 refused by the repairs, #497's 12 still prove = user decision). Census `scratchpad/rt45/census.tsv`; the family block below is quoted from `scratchpad/rt45/FINDINGS.txt`.
Witnesses `witnesses-r503/` (2): `g601_b60100_alias_root_rebound.py`, `g601_b60102_alias_root_rebound_isnot.py`.

Driver repro: session scratchpad `rp45/repro.sh` on 0d561a23b, 2026-11-01T05:35Z: all 8 rt45 verify exemplars rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F3 ROUTE #498's SAME-OBJECT EXEMPTION FOLLOWS `b = a` TO THE NAME `a` BUT NOT TO A's BINDING TIME: AFTER `b = a; a = n + 1000` THE TWO OPERANDS SHARE THE ROOT NAME `a`, THE TEST IS SKIPPED, AND `a is b` IS DECIDED AS VALUE EQUALITY (2)
  EXEMPLAR: g601/b60100_alias_root_rebound.py: `#@ ensures \result == True` f(n): `a = n + 1000; b = a; a = n + 1000; return a is b`
  CPYTHON: f(5) -> False (VIOLATION contract False); b60102 (`a = n * 1000; b = a; a = n * 1000; return a is not b`, claimed False) -> True
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt45 && PYTHONHASHSEED=0 PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt45/g601/b60100_alias_root_rebound.py --import-path src/pycsl   (CPython: cd /home/fabrice/git/pycsl/scratchpad/rt45/g601 && /home/fabrice/git/pycsl-rt45/.venv/bin/python3 -E -s b60100_alias_root_rebound.py)
  WHY: src/pycsl/pycsl.py ~14957-14970 (route #498): `_root498` walks a chain of single plain assignments (`len(_bind498[nm]) == 1`) from each operand. `b` has one binding (`b = a`), so its root is the NAME `a`; `a` has two bindings, so the walk stops at `a`. The roots compare equal and the `_root498[0] == _root498[1]` test `continue`s past the site before the freshness walk ever sees `a = n + 1000`. REPAIR: exempt only when the root's own binding count is 1 (or no rebinding of the root lies between the alias and the test).
  PROBES: g601/b60100_alias_root_rebound.py g601/b60102_alias_root_rebound_isnot.py
```
