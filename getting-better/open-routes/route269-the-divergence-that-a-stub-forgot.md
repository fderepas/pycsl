# OPEN ROUTE #269 — RESIDUAL DIVERGENCE LEAKS AFTER #263

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Residuals recorded by the #263 executor; driver-reproduced
at HEAD dc693d5c (all four witnesses rc=0).

## Witnesses (`witnesses-r269/`)
- R1 `r1_receiver_form_diverging_callee.py`: terminating `m` does `C().spin(k); return 7` with `spin` `\diverges`;
  `\result == 7` PROVES (CPython never returns). The `C().m()` call form gets a generic stub `spin_1` without
  `diverges`.
- R3 `r3_comprehension_vanished_call.py`: `[self.spin(x) for x in xs]` lowers into an opaque `list_comp_int`; the
  diverging call carries no termination obligation.
- R4 `r4_diverges_no_exception.py` / `r4b_toplevel_diverges_no_exception.py`: `\diverges` + `no_exception \all` on
  unbounded recursion proves; CPython raises RecursionError (`\all` covers the five known exceptions only) —
  needs an explicit scope statement or RecursionError modelling.
- R2 (mirror, not a witness here): nine Module 5 bespoke handlers call the `\diverges` dispatcher through the fixed
  terminating stub `val self__py_expr_to_ir_1` (abstract_ops._SELF_DISPATCH_VAL_DECLS) and claim termination.
- R5: cross-module cycles are not tracked (imported receivers resolve to no edge).
## Repair direction
Every stub of a `\diverges` callee carries `diverges` regardless of call form (R1, R2); a call hidden in an opaque
comprehension must propagate its callee's divergence/raises (or be refused) (R3); R4: either model RecursionError
for unbounded recursion under `no_exception \all` (refuse `\diverges` + `no_exception \all`) or document the scope;
R5: refuse unresolvable cross-module recursion or treat imported receivers conservatively.

## REPAIR (2026-10-17, branch r269 off 8b0bfbbd)

**Rule** (all inline in `pycsl.py::_run_pipeline`, mirror twin `\trusted`; no Module 1-6 edit).
- **R1/R2 (every stub of a `\diverges` callee diverges).** On the EMISSION, just before route #263's second
  half: every plain program `val` whose name is a stub spelling `<...>_<m>_<arity>[_c<h>][_<k>]` of a
  `\diverges` function or method `m` of the unit gains `diverges`, whichever producer minted it (generic
  receiver-form `spin_1` for `C().m()` / `super().m()`, `_handle_dotted_call`'s `self_m_1`, the fixed Module 5
  `val self__py_expr_to_ir_1` of `abstract_ops._SELF_DISPATCH_VAL_DECLS`). Name-matched like #263/#167: an
  ambiguous match makes MORE callers owe `\diverges`. Logic `val function/predicate/ghost/constant` symbols are
  model operations (census: none matches a `\diverges` name in corpus or mirror) and are untouched. And every
  emitted `let`/`with` of a `\diverges` function carries `diverges` even when a bespoke scaffold wrote its
  header (`functions._expr_bespoke_body` and the stmt scaffolds hard-code theirs; also the imported Module 5
  handlers that `pycsl.mlw` still emits WITH bodies).
- **R3 (vanished calls).** A call inside a `ListComp`/`SetComp`/`DictComp`/`GenExp`/`Lambda` IR node whose
  callee name (last segment) names a `\diverges` function, one that may RAISE (declared `raises` or escaping
  `raise`, closed transitively over call names), or one with a non-trivial `requires` (found while repairing:
  the vanished call's precondition is never checked — 2891), must be visible in what the caller's emitted body reaches
  (transitively through emitted `let`s): a concrete application or a matching stub. If not: a diverging callee
  -> the caller's body first applies `val pycsl_opaque_call_diverges (_u: unit) : unit diverges` (so a caller
  claiming termination fails its termination VC, an honestly `\diverges` one type-checks — Why3 otherwise rejects
  its `diverges` with "this expression does not diverge"); a raising or precondition-carrying callee -> refused
  (`PYCSL-SEM-VANISHED-CALL-EFFECT`).
- **R4 (decided: refuse).** A `\diverges` function declaring `no_exception \all` that REACHES a cycle of the
  #263 call graph (itself included) is refused (`PYCSL-SEM-DIVERGES-NO-EXCEPTION-RECURSION`): an unbounded
  Python recursion ends in RecursionError. Scope documented (annotations.md §2.1.13, translational reference
  §T.2.7): RecursionError is not in `KNOWN_EXCEPTIONS`; a TERMINATING (`\variant`) recursion under
  `no_exception \all` is proved regardless of depth (control 2890(c)).
- **R5 (cross-module, partly closed).** The #263 graph now reads an IMPORTED function's body (kept by
  `ir_resolve._process_dependency`) for calls back into a module-level function of THIS unit (any qualifier,
  by last segment — over-approximate); edges into imported stubs (`f(...)`, `mod.f(...)`) are unchecked edges,
  and #263's second half treats a callee emitted as a `val` as never concretely applied. A cycle through an
  imported stub is refused (`PYCSL-SEM-CROSS-MODULE-RECURSION`) unless every member is `\diverges`.

| witness (corpus) | shape | 8b0bfbbd | after |
|---|---|---|---|
| 2880 | terminating `m` -> `C().spin(k)` (`\diverges`) | PROVED | FAIL (termination VC of `c__m`) |
| 2881 | terminating `m` -> `super().spin(k)` | PROVED | FAIL (termination VC) |
| 2882 | `[self.spin(x) for x in xs]` (vanished) | PROVED | FAIL (termination VC) |
| 2883 | `sum(self.spin(x) for x in xs)` (vanished) | PROVED | FAIL (termination VC) |
| 2884 | `no_exception \all` + `[self.chk(x) ...]`, `chk` raises | PROVED | refused (VANISHED-CALL-EFFECT) |
| 2885 | `\diverges` + `no_exception \all`, `self.m` recursion | PROVED | refused (DIVERGES-NO-EXCEPTION-RECURSION) |
| 2886 | same, top-level `let rec` | PROVED | refused |
| 2887 | same, non-recursive `top` reaching a `\diverges` recursion | PROVED | refused |
| 2888 | 2880 honestly `\diverges` | FAIL (does not diverge) | PASS |
| 2889 | 2882 honestly `\diverges` | FAIL (does not diverge) | PASS |
| 2890 | controls: terminating comprehension call; `\diverges`+`\all` loop; `\variant` recursion + `\all` | PASS | PASS |
| 2891 | `no_exception \all` + `[self.inv(x) ...]`, `inv` requires `k > 0` over `10 // k` | PROVED | refused (VANISHED-CALL-EFFECT) |
| 2892 | `g -> imported f -> __main__.g` (fixture `multi_file_lib/r269_main_peer.py`) | PROVED | refused (CROSS-MODULE-RECURSION) |
| `witnesses-r269/r5_cross_module_cycle_{a,b}.py` | `a.g -> b.f -> a.g` via module imports | PROVED (both) | refused (both, CROSS-MODULE-RECURSION) |

CPython ground truth in each `__main__` ("does not terminate" / ValueError / ZeroDivisionError / RecursionError /
7). The two-file R5 pair is not a corpus driver (a corpus file `NNNN_*.py` cannot be the target of an `import`);
2892 closes the same cycle through `__main__`. Probe files (scratchpad, not
corpus): field-chain `self.c.spin`, `@staticmethod` `C.spin`, typed-param `c.spin` already diverged at base (#263).

**Census + blast radius (measured first).** `\diverges` population: 46 corpus root files, 0 pyref, 4 mirror files.
At 8b0bfbbd no corpus emission carried an un-diverging stub of a `\diverges` name; the mirror had
`self__py_expr_to_ir_1` (Module5_IREmitter) and `unparse_inner_1` / `visit_2` (pure_ast). Corpus root: 0 MOVED,
0 GONE, 0 APPEARED (1755 -> 1762 .mlw, 7 new emitting sources 2880-2883/2888-2890; 2884-2887/2891/2892 refused);
pyref 2186/2186, 0/0/0. No corpus file reaches the three new refusals but the witnesses, so M1 has no mover.
Mirror: 3 MOVED, 0 GONE — every moved line is an added `diverges`, the opaque diverging `val`, or its application:
- `frontend/Module5_IREmitter` (+14 `#@ \diverges` markers, each forced by a fixed point of a static scan of the
  emission for a non-`diverges` `let`/`with` whose body applies a diverging symbol — 0 at base, 0 after; Why3's
  own termination warning is not printed by `--type-only`): R2's nine bespoke handlers `_py_expr_compare`,
  `_py_expr_listcomp/setcomp/dictcomp/genexp`, `_py_expr_lambda`, `_py_stmt_assign/delete/match` (each applies the
  `\diverges` dispatcher `_py_expr_to_ir` through `self__py_expr_to_ir_1`), and R3's five whose call to the
  dispatcher VANISHED into an opaque comprehension — `_comprehension_generators_to_ir`, `_py_expr_tuple`,
  `_py_expr_list`, `_py_expr_dict`, `_py_expr_set` (`[self._py_expr_to_ir(e) for e in ...]`; their emitted bodies
  now apply `pycsl_opaque_call_diverges`, without which Why3 rejects the honest marker: "this expression does not
  diverge").
- `frontend/pure_ast` (+2 markers): `visit_FormattedValue` calls its nested `\diverges` `unparse_inner` (its stub
  `unparse_inner_1` now diverges) and `_fstring_FormattedValue` calls `self.visit_FormattedValue`.
- `pycsl` (the importer): the imported Module 5 stubs gain `diverges`, and the Module 5 handlers this file still
  emits WITH bespoke bodies get the header clause and (`_py_expr_dict`) the opaque application.
All three `why3 --type-only` clean at base and after. Whole-file proofs OWED (all three are big files); every
moved function only LOSES its termination goal (the added `val` has no precondition), so no proof can newly fail;
a `--fun` proof of `pycsltojsonemitter___py_expr_tuple` exceeded the 10-minute window (OWED).

**Ledgers.** `refusal-witness-census.tsv`: 10 rows appended by the plane's own `--append-new` for 2880-2887/2891/
2892 only (the run also produced 221 rows for other routes' row-less witnesses; those were NOT kept); coverage
226 -> 229 demonstrated. `check-corpus-contract-truth-args` MAX_RAISED 15 -> 18 for three declared-`\diverges`
functions of 2888/2889 that loop forever for k > 0 (partial correctness, nothing false claimed; 2888's `m` and
2890's `spin` take `requires k <= 0` to stay out). The 2892 fixture guards its `__main__.g` callback with
`hasattr` so the truth harness (which has no `g`) sees it return 0.

RESIDUALS (measured, not closed here):
- A stub that DROPS its callee's undeclared escaping `raise`: `self.chk(k)` where `chk` raises ValueError (no
  `#@ raises`) lowers to `val self_chk_1` with no `raises`, so a `no_exception \all` caller PROVED at 8b0bfbbd and
  after (CPython: ValueError). Reproducer: scratchpad `r269/r3p/raise_plain.py`; with a declared `#@ raises` the
  call is asserted (fails correctly). Not a divergence; candidate new route.
- A cycle that leaves this unit through an imported CLASS's method (receiver of an imported type) is not tracked;
  the probe shape (`modd.h(self, k)` -> `c.m(k)`) fails L3-tc today (object parameter int-erased), so nothing proves.
- An imported `\variant` function's stub is emitted with its `variant` clause and fails L3-tc ("unexpected
  'variant' clause") at base and after — loud, not unsound.
- A lambda whose body applies a diverging stub makes its enclosing function owe divergence even when the lambda
  is never called (Why3 types the `fun` body's effect; already so at 8b0bfbbd for `self.m()` stubs) — over-strict,
  fail-closed.

**Gates** (logs under the executor scratchpad `r269/`). G1: 2880-2887/2891/2892 PROVED at 8b0bfbbd -> FAIL
(termination VC of `c__m`: 2880-2883) / refused (2884-2887, 2891, 2892); 2888/2889 FAIL ("does not diverge") ->
PASS; 2890 PASS -> PASS (`g1_summary.txt`, `g1/{base,after}/`); R5 pair PROVED -> refused (`g1r5/`). G2: root
1755 -> 1762 .mlw, 0 MOVED / 0 GONE / 0 APPEARED; pyref 2186/2186, 0/0/0 (`g2_root.log`, `g2_pyref.log`); no
mover, so no M1 re-proof is owed. G3: mirror 53/53, 3 declared MOVED / 0 GONE (`g3_mirror.log`); type-only clean
on all three; whole-file proofs OWED (big files). G4: `run-soundness-planes.sh --slow` 84/84 green
(`g4_slow.log`; it includes the 61 fast planes); `check-self-annotate-sync.sh`, `self-annotate-mirror-check.sh`,
`check-mirror-coverage.py` (549/549), `doc-coherency --check`: rc=0.
