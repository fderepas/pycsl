# OPEN ROUTE #505 — ir_inline SUBSTITUTES `self` ONLY IN FIELD READS / WRITES AND `self.m(...)` CALL HEADS: A BARE `self` VALUE IN THE SPLICED METHOD (`return getv(self)`) KEEPS ITS SPELLING AND, INSIDE A CALLER METHOD, BINDS TO THE CALLER's OWN `self`
**Status: REPAIRED (executor u6, driver run #4, 2026-11-01, off e5237469f; see REPAIR below), Severity 1.** Red-team round 45 (driver run #4, 2026-11-01, on 0d561a23b = main + the #496 / #498-#500 repairs under integration: 332 probes in g600-g607, 303 CPython-breaching, 15 confirmed in 5 families, all default mode; rt44's 139 pairs: 127 refused by the repairs, #497's 12 still prove = user decision). Census `scratchpad/rt45/census.tsv`; the family block below is quoted from `scratchpad/rt45/FINDINGS.txt`.
Witnesses `witnesses-r505/` (1): `g603_d60305_method_passes_self.py`.

Driver repro: session scratchpad `rp45/repro.sh` on 0d561a23b, 2026-11-01T05:35Z: all 8 rt45 verify exemplars rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F5 ir_inline SUBSTITUTES `self` ONLY IN FIELD READS / WRITES AND `self.m(...)` CALL HEADS: A BARE `self` VALUE IN THE SPLICED METHOD (`return getv(self)`) KEEPS ITS SPELLING AND, INSIDE A CALLER METHOD, BINDS TO THE CALLER's OWN `self` (1)
  EXEMPLAR: g603/d60305_method_passes_self.py: `class C`: `m(self): return getv(self)`; `#@ ensures \result == self.v` `run(self): return g.m()`; `g = C(1)`; `#@ ensures \result == 2` f: `c = C(2); return c.run()`
  CPYTHON: f(0) -> 1 (VIOLATION contract 1): g.m() is getv(g) == g.v == 1
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt45 && PYTHONHASHSEED=0 PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt45/g603/d60305_method_passes_self.py --import-path src/pycsl   (CPython: cd /home/fabrice/git/pycsl/scratchpad/rt45/g603 && /home/fabrice/git/pycsl-rt45/.venv/bin/python3 -E -s d60305_method_passes_self.py)
  WHY: src/pycsl/frontend/ir_inline.py `_substitute`: a `Var` node is rewritten only via `param_map` / `rename`; `self` is substituted only in `FieldGet` / `FieldAssign` / `FieldAugAssign` objects and in `self.X(...)` call funcs. The `Var self` argument of `getv(self)` survives, and once `g.m()` is spliced into `C.run`, it names run's receiver (`c`, v == 2). The #169 capture check exempts it (`n != recv` / `self` not a caller binder). typed / store: Why3 type errors. REPAIR: map `Var self` -> `Var <recv>` in `_substitute` (or refuse a method whose body uses `self` outside a field / call head).
  PROBES: g603/d60305_method_passes_self.py
```

## REPAIR (executor u6, driver run #4, 2026-11-01; annotations §7.505)

Inline in `frontend/ir_inline.py::_Inliner._expand` (mirror twin `\trusted`; `_substitute`, whose twin is VERIFIED, is
untouched; no new def, no axiom), new code `PYCSL-R505-INLINE-BARE-SELF`: renaming the bare `self` to the global receiver
would pass the global as a value, which inline.md Phase 3 (`_check_no_aliasing`) forbids, so refuse by default (Phase 3's
polarity): a spliced method that reads `self` as a value, calls `self`, rebinds `self`, or holds `self` in any node the
renaming does not cover (an `object: "self"` outside `FieldGet` / `FieldAssign` / `FieldAugAssign`).

Witnesses: the one in `witnesses-r505/` REFUSED under default / typed / store (3/3 runs; typed / store were Why3 type
errors at base). Corpus 7987 (PROVED at base, REFUSED), 7988 (`x = self; return x.v`: a Why3 type error at base, refused by
name); controls 7993 (the field passed, `getv(self.v)`) / 7994 (`getv(self)` on a LOCAL instance, by contract) PROVED. Advice
followed (witnesses-r505/advice) = the two controls.
Over-refusal: corpus root 0 MOVED / 0 GONE / 0 APPEARED vs v23/bd (5 new controls emit), pyref 2186/2186 0/0/0, mirror 53/53 0/0/0 vs mir-main14 (a first draft refused 2 mirror files through #504 -- frontend/pure_ast `operator_precedence is not _Precedence.FACTOR` via a class-level dict read on `self`, module6_whyml/statements `stmt.origin is not _ABSENT` against ir_schema's `object()` sentinel -- fixed in fc3e8512f); rt43 / rt44 / rt45 CPython-honest controls (345): 0 refused by #503 / #504 / #505.
Commits: 15b5b3e37. Final battery on dd736c419: fidelity 3/3, carriers, advice 217, planes 62/62 fast green; driver runs --slow.
