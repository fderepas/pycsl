# OPEN ROUTE #263 — RECURSION THROUGH METHOD CALLS IS NEVER CHECKED FOR TERMINATION

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Red-team round 3; driver-reproduced at HEAD 13451c8d (t06/t09/h04 rc=0;
CPython RecursionError). Witnesses `witnesses-r263/`: t06 (self-recursive method), t08 (+ no_exception), t09
(mutually recursive methods), t10 (function -> method -> function cycle), h04 (`#@ happy ... total` policy proves
for a non-terminating `parse`).
Mechanism: every `self.m()`/`obj.m()` call is a bodyless `val` stub keeping the callee's `ensures` (when it has no
`requires`), so Why3 sees no cycle: a plain `let` with no variant/diverges claims termination and assumes the
callee's postcondition circularly. Top-level recursion is `let rec` and is checked. Route #206 checks only cycles
through trusted stubs.
Repair: build the full call graph including method calls (resolved by receiver class / self), and for any cycle
either require a `#@ variant`/`decreases` checked across the cycle, or mark `\diverges` / refuse; the callee's
postcondition must not be assumed within its own SCC without a termination argument.

## REPAIR (2026-10-17, branch r263 off 283d1033)

**Rule** (inline in `pycsl.py::_run_pipeline`, mirror twin `\trusted`; two halves). (1) After the
`ir-validate-boundary` check, build the unit's call graph INCLUDING method calls, receivers resolved by class:
`self` -> the enclosing class's hierarchy (ancestors = inherited implementation, descendants = overrides);
`super()` -> what follows the class in an MRO (ancestors of a subclass, never the class or a subclass); a
typed or constructor-bound local/parameter -> its class's hierarchy; a typed field chain -> the field's type;
`ClassName.m` -> that class; an imported module or a builtin (`type.__instancecheck__`, `str.join`) -> no method
of this unit; anything else -> EVERY method of that name (over-approximation, the sound direction). Constructor
edges `C(...)` -> `__init__@C`, whose calls (`__init__`/`__post_init__`/`__new__`, dropped by Module 5) are
read from the woven AST. `\trusted`/`\abstract`/lemma functions contribute no edges. Tarjan SCCs; every SCC
holding a method/constructor edge is a candidate. (2) Just before `return _mlw`, each candidate edge a->b is
decided on the EMISSION (Module 6 owns the concrete-vs-stub decision; re-deriving it would be a second
producer): UNSEEN if a's body references a stub `<recv>_<m>_<arity>[_c<h>][_<k>]`; SEEN if it applies b
concretely (directly or through helpers of its own `let rec` group — the bespoke pyval walkers), is one
delegation into a `variant`-carrying `let rec` catamorphism (0960 `app__pp = pp_term (App ...)`), or was
re-expressed by a bespoke lowering as its own `<name>__*` variant walkers (`irscanner__find_assigned_vars`);
anything else (a vanished call, a constructor) is UNSEEN. A cycle with an unseen edge is refused
(`PYCSL-SEM-METHOD-RECURSION-UNCHECKED`) unless EVERY member is `#@ \diverges` (partial correctness: assuming a
recursive callee's postcondition is then the standard sound rule). (3) Module 6
(`expressions.py::_handle_dotted_call`, mirror `\trusted`): the stub of a call whose method name names a
`#@ \diverges` method of the unit carries `diverges` — so a `\diverges` method recursing only through its stub
is writable at all (Why3 rejected it: "this expression does not diverge"), and a NON-`\diverges` caller of a
diverging method no longer gets its termination for free (Why3's termination VC fails). Byte-identical for
every unit with no `\diverges` method.

`#@ happy ... total`: a total target on a refused cycle is refused by (1); marking it `\diverges` is refused by
route #93; reaching a `\diverges` callee is refused by route #208. `no_exception`: t08's shape is refused by (1).

| witness (corpus) | shape | 283d1033 | after |
|---|---|---|---|
| 2770 | `m -> self.m` | PROVED | refused |
| 2771 | 2770 + `no_exception \all` | PROVED | refused |
| 2772 | `a <-> b` via `self.` | PROVED | refused |
| 2773 | `g -> c.m -> g` (fresh local) | PROVED | refused |
| 2774 | `happy ... total` on self-recursive `parse` | PROVED | refused |
| 2775 | terminating `m` calls `\diverges` `spin` via `self.spin` | PROVED | FAIL (termination VC) |
| 2776 | `B.m -> inherited self.p -> self.m` (dispatch-only cycle) | PROVED | refused |
| 2777 | `__init__ -> self.m -> C()` | PROVED | refused |
| 2778 | `C().m(k)` receiver form | PROVED | refused |
| 2779 | `@staticmethod` `C.m(k)` | PROVED | refused |
| 2780 | 2770 marked `\diverges` (now writable) | FAIL (does not diverge) | PASS |
| 2781 | control: acyclic self/fresh/`super()`/builtin-field calls | PASS | PASS |

CPython ground truth in each `__main__` (RecursionError / "does not terminate"). Probe files (not corpus):
inherited-dispatch, field-typed `self.c.m`, param-typed `other.m`, unused-result, in-condition recursion all
refused; `len(self)`/`==` dunder recursion and `@property` recursion fail type-check (not proved).

**Blast radius.** Corpus root: 1 MOVED (0893, declared SOURCE repair), 0 GONE, 0 APPEARED (1740 -> 1743, 3 new
emitting sources); pyref 2186/2186 0 MOVED/GONE. M1: 0893 `PatternWalker.pattern_has_constructor` recurses via
`self.pattern_has_constructor(...)` with no measure — PROVED at base, refused after with the old source; it now
carries `#@ \diverges` (no measure over an `ExprIR` dict is expressible) and PROVES after; the projection
capability it locks is unchanged. Mirror: 3 MOVED, 0 GONE — every moved line is an added `diverges`:
`frontend/pure_ast` (52 `#@ \diverges` markers: `_Unparser.traverse` recurses `self.traverse(item)` with no
measure, and the 50 `visit_*`/`visit`/helpers + the nested `unparse_inner` that reach it through its
now-diverging stub — measured by a fix-point of Why3 "termination of this expression cannot be proved"
warnings, 0 left; the recursion is over finite AST trees but nothing in the mirror's model can state that),
`frontend/Module3_Weaver` (1: `_target_dotted_path` recurses `Module3_Weaver._target_dotted_path(target.value)`;
its only callers are bespoke-walked), `pycsl` (the imported Weaver stub). All three `why3 --type-only` clean;
Why3 termination-warning scan of all 53 mirror emissions: 0 at base, 0 after. Census before the emission
criterion: 24 mirror SCCs (pyval walkers, `IRScanner` statics, Weaver collectors) — all but these two classes
are SEEN by the emission criterion (bespoke `let rec` walkers with variants), so they needed nothing.

RESIDUALS (measured, NOT closed here; candidates for a new route):
- R1 receiver-form call to a `\diverges` method from a terminating caller: `C().spin(k); return 7` lowers to a
  generic contract-less `val spin_1`, not `_handle_dotted_call`, so the stub stays terminating. MEASURED after:
  `m` (`ensures \result == 7`, no `\diverges`) PROVES; CPython `C().m(1)` never returns.
- R2 the Module 5 mirror's bespoke handlers (`_py_expr_compare`, the four comprehension handlers, `_py_expr_lambda`,
  `_py_stmt_assign/delete/match`) re-enter the `\diverges` dispatcher `_py_expr_to_ir` through the STATIC
  receiver-less decl `val self__py_expr_to_ir_1` (`abstract_ops._SELF_DISPATCH_VAL_DECLS`) and claim termination.
  Closing it needs the bespoke headers (`functions._expr_bespoke_body` and the stmt scaffolds) to honour
  `\diverges` plus 9 mirror markers; Module5's whole-file proof would be OWED.
- R3 a call that VANISHES into an opaque comprehension (`[self.spin(x) for x in xs]` -> `list_comp_int`) carries no
  termination obligation at all; `\diverges` cannot even be written there. MEASURED after: `ys = [self.spin(x) for x
  in xs]; return 7` under `ensures \result == 7` PROVES; CPython `C().m([1])` never returns.
- R4 `#@ \diverges` + `#@ no_exception \all` on an unbounded recursion (method or top-level `let rec`) PROVES
  while CPython raises RecursionError — by the documented semantics `\all` is the Phase-1 set (RecursionError
  is not in `KNOWN_EXCEPTIONS`), so this is a scope statement to make explicit, not a lowering bug. MEASURED: the
  top-level `def f(k): return f(k)` form PROVES at 283d1033 and after; the method form PROVES after (it did not
  type-check before: "does not diverge").
- R5 cross-unit cycles (a receiver that is an imported module/class resolves to nothing here).

**Gates** (logs under the executor scratchpad `r263/`). G1: 2770-2779 PROVED at 283d1033 -> refused / FAIL after;
2780 FAIL -> PASS; 2781 PASS -> PASS (`g1/base.log`, `g1/after.log`). G2: root 1740 -> 1743 .mlw, 1 MOVED (0893,
declared) / 0 GONE / 0 APPEARED; pyref 2186/2186, 0/0/0 (`g2_root.log`, `g2_pyref.log`); M1 0893 base PROVES, old
source refused after, new source PROVES after. G3: mirror 53/53, 3 MOVED (declared, `diverges` lines only) / 0 GONE,
`why3 --type-only` clean on all three; `module3_weaver___target_dotted_path` re-proved (`--fun`, rc=0); the rest
of Weaver and `pycsl` unchanged but for the added clause; pure_ast whole-file proof OWED (big file); the moved
functions only LOSE a termination goal. G4: fast planes 61/61 (two ledgers re-measured: `refusal-witness-census.tsv`
rows appended by the plane's own `_census_row` for 2770-2779 only; `check-corpus-contract-truth-args` MAX_RAISED
14 -> 15 for the fourth declared-`\diverges` driver 2780). Slow: 17 run green; 3 red at base skipped
(stdlib-modules-verify, getattr-erasure, assigns-writes-survival); `no-exception-differential` /
`value-differential` exceed the 10-minute foreground window — their whole populations (260 drivers incl.
`generated/`) are byte-inert, 0 MOVED / 0 GONE, so neither verdict can move. `check-self-annotate-sync.sh`,
`self-annotate-mirror-check.sh`, `check-mirror-coverage.py` (549/549), `doc-coherency --check`: rc=0.
