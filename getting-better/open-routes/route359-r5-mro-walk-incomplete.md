# OPEN ROUTE #359 — R5's MRO WALK SEES ONLY TOP-LEVEL `def`s AND SKIPS IMPORTED MRO CLASSES
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r357 executor off 1a9cfa42 — see REPAIR). Was OPEN, Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r359/`: `m15_rec_assign_override.py`, `m16_rec_lambda_override.py`, `m17_rec_conditional_def.py`, `m19_rec_imported_mixin.py`, `m20_rec_mixin_inherits_import.py`, `m21_rec_try_def.py`.

Route #344's C3 walk finds a method only as a top-level `def` of a file class: `B.m` bound by `m = _bm`, a lambda, a `def` under `if` or `try` (m15/m16/m17/m21) is skipped, so `C.m` resolves to `A.m` and R5 compares it with itself; `a.m() % 1 == 0` proves, CPython 0.5. Imported MRO classes are skipped too (#344 residual), reachable directly (m19) and through a file class `B(Bf)` with no def (m20). Helper `rt26other.py`.

Repair: Treat a class body binding the name by ANY statement (Assign / AnnAssign / def under if/try/with) as defining it and refuse what R5 cannot compare; refuse when a class from outside the file precedes the defining class in the MRO.

## REPAIR (2026-10-25, r357 executor off 1a9cfa42, repaired with routes #357 / #358; code 66f2f2ea / acec0e22 / af97b85a, corpus + docs 570c626f (annotations §7.31, translational §T.6.42), census 66f2dd33)
**Design: every class-body binding counts, and an MRO class R5 cannot read refuses.** In the route #278 block of
`_run_pipeline` (inline, mirror twin `\trusted`, the existing `PYCSL-SEM-OVERRIDE-REFINEMENT` raise — no new site): (1) besides
route #338's top-level-`def` map, every other binding of a name in a class body is recorded (assignment / augmented / annotated
with value / `for` / `with` / `del` targets, walrus targets in a statement header, imports, `except .. as`, `match` captures,
nested `def` / `class`; nested scopes not entered). (2) Route #344's per-pair MRO walk stops at the first class BINDING the
name: a non-`def` binding is an R5 violation, as is a side's own top-level `def` shadowed by a later non-`def` binding, and (sub
side, base class in the file) a class from outside the file before the definer. (3) Because a non-`def` binding records NO
refinement pair (m15/m16/m19/m20 had none, so nothing ran), the block now also runs without pairs (whenever
`check_behavioral_subtyping` holds, i.e. not under `--assume-class-exact`): for every file class K with a consistent C3 MRO
and every method a later file class A of that MRO defines by a top-level `def`, the first MRO class binding the name must be a
file class with a top-level `def`; a non-`def` binding or an outside class before A is refused. `object` and a builtin class
that does not own the name (no `__dict__` entry in its non-`object` MRO; not rebound by an import) are skipped. MEASURED first:
the pair-walk outside-class rule, unrestricted, GONE'd mirror `Module6_WhyMLTranspiler` (its sub class's MRO is all imported
mixins, and the BASE class is imported too) — narrowed to a base class of the file, mirror 53/53 0/0/0.
**Probe table** (full proof via heavy.sh; base = 1a9cfa42; m19 / m20 use the builtin `float` (`float.hex` returns a str) in place
of the witness helper module):
| witness | corpus | base | after |
|---|---|---|---|
| m15 `B.m = _bm` (module fn `-> float`) | 4816 | rc=0 PROVED | rc=1 REFUSED OVERRIDE-REFINEMENT (non-`def` binding) |
| m16 `B.m = lambda self: 0.5` | 4817 | rc=0 PROVED | rc=1 REFUSED |
| m17 `def m` under `if True:` | 4818 | rc=0 PROVED | rc=1 REFUSED |
| m19 `class C(float, A)`, `A.hex -> int` (witness: imported `Bf as B`) | 4819 | rc=0 PROVED | rc=1 REFUSED (outside class before the definer) |
| m20 file mixin `B(float)`, `C(B, A)` (witness: `B(Bf)`) | 4820 | rc=0 PROVED | rc=1 REFUSED |
| m21 `def m` inside `try:` | 4821 | rc=0 PROVED | rc=1 REFUSED |
| control: `C(B, A)` with top-level `B.m -> int` (B also binds `k = 3`); `D(float, A)`, float has no `m` | 4832 | rc=0 PROVED | rc=0 PROVED |
The witness files themselves (with `rt26other.py`) were also run: m15-m21 all rc=1 REFUSED after (rc=0 PROVED at base).
**Blast radius**: the shared sweep in route #357's REPAIR — root 0 MOVED, 1 GONE of this route: `1457_route147_unmodelled_
foreign_ancestor_before_the_definer` (`pycsl-expected: FAIL`, `class Cee(Exception, Ay)`: `BaseException.__init__` precedes
`Ay.__init__`, which is exactly this rule; census row re-measured VERIFY-FAIL -> REFUSAL); pyref 0/0/0; mirror 53/53 0/0/0.
**Gates** (all three routes, one run on the final code af97b85a + corpus/docs/census; tee'd in full): byte-diff root rc=0
(`--expect-gone` 1313 1457) and pyref rc=0 (above); mirror emit sweep rc=0 0/0/0; `check-self-annotate-sync.sh` rc=0 (926
un-trusted mirror functions verbatim); `self-annotate-mirror-check.sh` rc=0; `run-soundness-planes.sh` fast rc=0 61/61;
`doc-coherency --check` rc=0; `check-refusal-witness-coverage` rc=0 (295 demonstrated, 5 undemonstrated = ceiling 5; 324 sites,
one new: PYCSL-R357-DYNAMIC-CONSTRUCTOR); `check-trusted-reasons` rc=0 (420 <-> 420, unclassified 259);
`check-assigns-underdeclaration --transitive` rc=0 (TRAP 3, HOLE 0); `check-getattr-erasure` rc=0 (DECLARED 0); `check-dropped-mutation` rc=0 (0 / 51 / 5 / 0, ratchets
unchanged); `check-assumed-facts` rc=0 (85 facts, all reviewed families); `check-stdlib-modules-verify` rc=0 (known 21
non-verifying). `--slow` planes not run.
**Residuals.** (1) A pair whose BASE class is outside the file is still not compared (R5 reads source only; the mirror's
mixin pairs live there). (2) An imported class that does NOT define the name is still refused when it precedes the definer
(R5 cannot tell; a builtin class is checked by its `__dict__`s). (3) `__getattr__` / metaclass / `__init_subclass__` /
decorator-time rebinding (`setattr(B, ..)` is route #344's rebinding rule) are not modelled. (4) Class bodies are read per file.
