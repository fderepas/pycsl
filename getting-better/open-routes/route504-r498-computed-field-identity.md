# OPEN ROUTE #504 — ROUTE #498 NAMED RESIDUAL: A FIELD HOLDING A COMPUTED int (`self.a = n + 1000`, OR A CLASS-TYPED PARAMETER's FIELDS) IS READ AS AN EXISTING OBJECT, SO `k.a is k.b` IS DECIDED AS VALUE EQUALITY
**Status: REPAIRED (executor u6, driver run #4, 2026-11-01, off e5237469f; see REPAIR below), Severity 1.** Red-team round 45 (driver run #4, 2026-11-01, on 0d561a23b = main + the #496 / #498-#500 repairs under integration: 332 probes in g600-g607, 303 CPython-breaching, 15 confirmed in 5 families, all default mode; rt44's 139 pairs: 127 refused by the repairs, #497's 12 still prove = user decision). Census `scratchpad/rt45/census.tsv`; the family block below is quoted from `scratchpad/rt45/FINDINGS.txt`.
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

## REPAIR (executor u6, driver run #4, 2026-11-01; annotations §7.504)

Inline in route #498's freshness walk in `pycsl.py::_run_pipeline` (mirror twin `\trusted`; no new def, no axiom), new code
`PYCSL-R504-IS-ON-STORED-VALUE`: two reads of ONE stored path (`c.a is c.a`: names and attribute reads, no call) are exempt;
any other attribute / field operand, directly or through a local bound to it, is an existing object only when it is a
class constant / enum member (an attribute of a program class name, or a class-body binding read through an instance) or
when EVERY declaration of that field in the program's classes (the receiver's class when its type is known) names a
program class or `Optional` of one. A value-typed, container-typed, unannotated or undeclared field (a module attribute
too) is refused. An outer name is NOT exempt by itself: `k.a is G` with `G = 1000` PROVED at base (CPython False, corpus
7989); a module-level name bound once to `object()` (in this file, or imported by `from M import X` with M on the program's
path) and never rebound / named `global` is a singleton operand (`object.__eq__` is identity).

Witnesses: both in `witnesses-r504/` REFUSED under default / typed / store (6/6 runs). Corpus 7984 / 7985 / 7986 (locals
bound to the field reads) / 7989 (field vs a module-global literal) (PROVED at base, REFUSED); control 7992 (`k.a is k.a` on a
local instance) PROVED, 7916 (`c.a is c.a`) still PROVED. Advice followed (witnesses-r504/advice): `==` and the same-field
read VERIFY (default model). Residuals (named): a module global holding a computed int / str (`G1 is G2`) and a computed
class constant are measured OPAQUE (NOT PROVED at e5237469f), not refused; an `object()`-sentinel field compare is likewise
not provable.
Over-refusal: corpus root 0 MOVED / 0 GONE / 0 APPEARED vs v23/bd (5 new controls emit), pyref 2186/2186 0/0/0, mirror 53/53 0/0/0 vs mir-main14 (a first draft refused 2 mirror files through #504 -- frontend/pure_ast `operator_precedence is not _Precedence.FACTOR` via a class-level dict read on `self`, module6_whyml/statements `stmt.origin is not _ABSENT` against ir_schema's `object()` sentinel -- fixed in fc3e8512f); rt43 / rt44 / rt45 CPython-honest controls (345): 0 refused by #503 / #504 / #505.
Commits: 15b5b3e37 (rule + corpus), fc3e8512f (sentinel / class-constant exemptions; mirror over-refusal fixed; 7989).
