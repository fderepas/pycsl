# OPEN ROUTE #504 — ROUTE #498 NAMED RESIDUAL: A FIELD HOLDING A COMPUTED int (`self.a = n + 1000`, OR A CLASS-TYPED PARAMETER's FIELDS) IS READ AS AN EXISTING OBJECT, SO `k.a is k.b` IS DECIDED AS VALUE EQUALITY
**Status: OPEN, Severity 1.** Red-team round 45 (driver run #4, 2026-11-01, on 0d561a23b = main + the #496 / #498-#500 repairs under integration: 332 probes in g600-g607, 303 CPython-breaching, 15 confirmed in 5 families, all default mode; rt44's 139 pairs: 127 refused by the repairs, #497's 12 still prove = user decision). Census `scratchpad/rt45/census.tsv`; the family block below is quoted from `scratchpad/rt45/FINDINGS.txt`.
Witnesses `witnesses-r504/` (2): `g601_b60104_field_computed.py`, `g601_b60105_field_param_class.py`.

Driver repro: session scratchpad `rp45/repro.sh` on 0d561a23b, 2026-11-01T05:35Z: all 8 rt45 verify exemplars rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F4 ROUTE #498 NAMED RESIDUAL: A FIELD HOLDING A COMPUTED int (`self.a = n + 1000`, OR A CLASS-TYPED PARAMETER's FIELDS) IS READ AS AN EXISTING OBJECT, SO `k.a is k.b` IS DECIDED AS VALUE EQUALITY (2)
  EXEMPLAR: g601/b60104_field_computed.py: `class K: __init__(self, n): self.a = n + 1000; self.b = n + 1000`; `#@ ensures \result == True` f(n): `k = K(n); return k.a is k.b`
  CPYTHON: f(5) -> False (VIOLATION contract False); b60105 (`#@ requires k.a == k.b` f(k: K): `return k.a is k.b` with k.b = int('1000')) -> False
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt45 && PYTHONHASHSEED=0 PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt45/g601/b60104_field_computed.py --import-path src/pycsl   (CPython: cd /home/fabrice/git/pycsl/scratchpad/rt45/g601 && /home/fabrice/git/pycsl-rt45/.venv/bin/python3 -E -s b60104_field_computed.py)
  WHY: src/pycsl/pycsl.py route #498: `Attribute` / `FieldGet` operands `continue` (not fresh). The route doc lists this as a NAMED RESIDUAL ('a field / module global STORING a computed int / str is read as an existing object'); it is NOT in the README's declared-assumption list, so it is counted here but flagged. REPAIR: treat an `is` between two int / str-typed fields as an uninterpreted predicate (or refuse it).
  PROBES: g601/b60104_field_computed.py g601/b60105_field_param_class.py
```
