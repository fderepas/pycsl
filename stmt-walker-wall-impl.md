# stmt-walker-wall-impl.md — implementation plan (the Stmt-walker wall is BREAKABLE)

*From `stmt-walker-wall.md` (report) + `stmt-walker-wall-response.md` (independent fable review, oracle-run).
Verdict, oracle-grounded and driver-verifier-re-confirmed: **BOUNDED FEATURE, not a boundary** — a recursive
`stmtir → scalar` READER over a variant with `list stmtir` (never `array stmtir`) list-children, a
`size`/`size_list` measure, and the element-decrease as a proved `let rec lemma`, is expressible + provable in
WhyML AXIOM-FREE (make-or-break spike `getting-better/composition-wall/stmt-walker-spike.mlw` = **14/14 Valid
on Alt-Ergo AND Z3, 0 `^axiom`, negative control fails**; independently re-verified by the driver). So the
wall is NOT leave-trusted. The residual is the classic M2 gap (target-provable ≠ emitter-generable): the
EMITTER must GENERATE that proven shape from the verbatim Python `StmtIR` frozen-dataclass sum. This plan
scopes that, spike-gated. Unlocks the 34-method dict-IR walker cluster (§census).*

## 0. Status of the TARGET spike (Gate S — already PASSED)

`stmt-walker-spike.mlw`: `stmtir` variant with leaves + `SIf (list stmtir)(list stmtir)` + a full `STry` with
FOUR list children (body/handlers/orelse/finalbody) + handlers as a mutually-recursive second sort; four-way
mutually-recursive cons-cell-counting `size`/`size_list`/`size_handler`/`size_hlist`; the element-decrease as
PROVED `let rec lemma`s (both sorts) + parent-child corollaries; the reader `ends_with_return` (3 mutually
recursive fns, `variant { size … }`); a non-decreasing `bad_walk` negative control. **14/14 Valid (Alt-Ergo
2.6.2 + Z3 4.13.3), every goal <0.1s; 0 `^axiom`; `bad_walk'vc` Timeout (non-vacuous).** So (R) read, (L)
list-child recursion, (T) termination, AND the multi-field/multi-sort handler shape ALL PASS. Oracle bonus:
`SIf (array stmtir)` is Why3-TYPE-REJECTED ("non-pure type in recursive type definition") — the live failure's
root cause; the child MUST be pure `list`/`seq stmtir`. **No refutation exit: the wall is confirmed breakable.**

## 1. The one un-spiked half — EMITTER-GENERABILITY (the make-or-break of the BUILD)

The TARGET is proven; the BUILD's make-or-break is whether PyCSL's emitter GENERATES the proven shape from the
Python `StmtIR` sum (`src/pycsl/ir_schema.py`: frozen dataclasses `IfStmt`/`WhileStmt`/`ForStmt`/`TryStmt`/…
with `body: List["StmtIR"]`, `orelse`, `finalbody`). Two facts make this tractable — and one risk:
- **PRECEDENT:** PyCSL ALREADY lowers a sibling frozen-dataclass sum — `ExprIR` (base `IRNode`,
  `ir_schema.py:271`) — to the `emit_ir` WhyML variant with `size`/projectors/size-decrease lemmas
  (`preamble.py::_emit_exprir_theory`). The ADT-lowering machinery EXISTS.
- **RISK (the spike target):** that machinery may be EXPR-family-specific — `ExprIR` children are FIXED-arity
  scalars (`left`/`right : ExprIR`), whereas `StmtIR` children are **`List["StmtIR"]`** (a self-referential
  LIST field). The emitter must lower a `List[<the ADT itself>]` field to a `list stmtir` variant field (pure,
  not `array`) AND emit the `size_list` leg + the element-decrease `let rec lemma`. Whether the existing
  `_emit_exprir_theory`-style generator handles a self-list-child is the exact unknown.

## 2bis. §2 SPIKE RESULT (2026-07-11, isolated worktree — VERDICT: GENERABLE-WITH-GAP)

The §2 make-or-break was RUN in an isolated worktree. Outcome, precisely:
- **S-C1 (theory emission) FULLY LANDS.** A hand-written `_emit_stmtir_theory()` (preamble.py, ~110 lines, the
  `_emit_exprir_theory` twin) emits the proven spike's `stmtir`/`shandler` sum (`size*`→`stmt_size*` to avoid
  clashing with the coexisting `emit_ir` `size`), wired into Module6 after the `_emit_exprir_theory()` call,
  same `_mutable_state_classes`/`_uses_ir_node_param` gate. The EMITTED theory: **9/9 Valid (Alt-Ergo + Z3),
  0 `^axiom`, children emit as pure `list stmtir` (NOT `array`)** — incl. `STry (list stmtir) (list shandler)
  (list stmtir) (list stmtir) with shandler = EHandler (list stmtir)` + the element-decrease `let rec lemma`.
  **Corpus-byte-inert CONFIRMED** (stash-diff on 0342 byte-identical; `stmtir` absent from 5 spot-checked corpus
  files). So the foundation's theory half is proven emittable and zero-risk — the next session re-emits it in
  minutes from this recipe.
- **S-C2/S-C3 (walker lowering) HARD-STOPPED at a pinned gap — the true M2 make-or-break.** Converting the
  simplest bool walker (`IRScanner.ends_with_return`) needs **≥3 new recognizers**, so no blind build was made:
  1. **`list <T>` PARAM-TYPE FAMILY — `functions.py:68-97` (`_param_type_str`'s List dispatcher).** It routes
     EVERY `List[T]` param into the `array <T>` family (int/string/real/record/seq/map via `_list_nested_elem`/
     `_param_list_flat_elem`); there is **NO `list <T>` (Why3 `list.List`) exit at all**. So `List["StmtIR"]`
     silently lowers to `array int` — the exact reported `int` vs `array int` failure. This is a NEW type-family
     branch (not a lookup-table entry): the emitter has never produced a `list <T>` parameter. **This is the
     build's real make-or-break** (§1's flagged risk, now pinned to a line).
  2. **list-structural body recursion** — `if not stmts: …; last = stmts[-1]` has no `[-1]` on a Why3 `list`;
     must lower to the spike's `match … | Cons x Nil -> … | Cons _ rest -> recurse` form (a body recognizer).
  3. **`variant { stmt_size … }` synthesis** for the recursive call against the S-C1 theory (S-C3).
- **CONVERGENCE:** recognizer #1 (the `list <T>` param/field family) is ALSO exactly what the **term-rewriter
  wall** (`term-rewriter-wall-impl.md` T-C2/T-C3: comprehension→`list term` helper, `list`-child constructor)
  needs. BOTH remaining breakable walls converge on ONE foundation: **the `list <T>` ADT-child type family +
  list-structural recursion body form.** That shared foundation is the pivotal next build.

**Driver decision (2026-07-11):** DEFER the foundation build to a focused session (it is a genuine 3-recognizer
+ N-conversion multi-session project; every such build receded within this run, so a 120-min forced attempt
would sprawl). S-C1 is proven-ready; the gap is pinned to `functions.py:68`. Build order for the next session:
the `list <T>` param/field family FIRST (unblocks both walls), then S-C1 land + one bool walker as one
count-reducing increment, then the cluster.

## 2ter. `list <T>` TYPE-FAMILY PROBE (2026-07-11, second isolated worktree — VERDICT: BOUNDED, green light)

Probed the pinned make-or-break (`functions.py:68`): is a `list <T>` param/field type-family exit a bounded,
byte-inert add, or is the `array <T>` commitment entangled? **VERDICT: BOUNDED at the signature/type-family
level.** Evidence:
- **~185 lines across 4 files** produce a correct `(stmts: list stmtir)` signature from a `List["StmtIR"]`
  param: (1) `Module5_IREmitter.py` new `_m5_get_ir_node_list_elem` (narrow-gated on literal `"StmtIR"` in
  `List[...]`) threaded into the func IR as `param_ir_list_elem`; (2) `functions.py` `_param_type_str` checks it
  FIRST, before the `array` machinery, returning `(safe: list <elem>)`; (3) `preamble.py` `_emit_stmtir_theory`
  (S-C1) + `needs_list_ghost` forced under @mutable_state so `use list.List/Length/Nth/Mem/Append` land;
  (4) Module6 wiring. A probe class `Walker.walk(self, stmts: List["StmtIR"]) -> int` emitted
  `val walker__walk (self: walker) (stmts: list stmtir) : int` and type-checked (`L1✓ L2✓ L3-tc✓`).
- **Byte-inert CONFIRMED** — 5 corpus files (0001/0002/0100/0342/0500) byte-identical stash-vs-edits. The exit
  is routed OUTSIDE the `array1d_params`/`_array_locals` machinery, so none of the ~15 array-consumer sites fire
  for the param *as long as the body never touches it*.
- **Entanglement precisely bounded to the BODY (not the signature):** `_current_symbol_table[arg]` for a
  `List["StmtIR"]` param still legacy-resolves to `"list"`, so any BODY reference (even read-only) hits the
  array-family paths across ~15 sites / 8 categories (truthiness, `len`, `.join`, subscript, slice, array-set,
  augassign, for-iteration). And Why3 `list.List` is NOT indexable (`stmts[-1]` has no `Array.get` twin) → the
  body needs a QUALITATIVELY different lowering: structural `match Nil -> … | Cons x rest -> …` recursion +
  `variant { stmt_size … }` synthesis (S-C2/S-C3). That is the separate multi-session project, confirmed.

**Net for the next session:** the type-family FOUNDATION (S-C1 theory + the `list <T>` param/field exit) is a
**clean, bounded, corpus-byte-inert green light** (~185 lines, recipe in the two worktree spikes). The BODY
conversion (S-C2 `match Nil/Cons` recursion + S-C3 variant synthesis, replacing array-indexed idioms) is the
larger, well-scoped remainder. Both breakable walls (stmt-walker's 34 readers + term-rewriter's T-C2/T-C3)
consume this same foundation.

## 2quater. SELF-ANNOTATION-SUITE SAFETY GATE (2026-07-11, isolated worktree — VERDICT: BREAKS as gated)

The §2ter probe proved corpus-byte-inertness, but the theory + `list <T>` exit are `@mutable_state`-gated and
the MIRROR files ARE `@mutable_state`, so the theory emits into their OWN `.mlw`. Running the full
self-annotation suite against the foundation edits found it **NOT mirror-proof-safe as currently gated** — TWO
distinct root causes, both must be fixed before the foundation can land:
1. **Name collision (emission-level break).** Three mirror files ALREADY model statement IR with their own
   Why3 decls — `stmt_control_flow.py` (`type stmtir = int`, line 180), `statements.py`
   (`type stmt_ir = … | SIf expr_ir int int | …` + `type stmtir = int`, line 173), `expressions.py`
   (`type stmtir`, line 216). `_emit_stmtir_theory` emits `type stmtir` + `SIf/SPass/SExpr/SReturn/SWhile/
   STry/EHandler` into EVERY `@mutable_state` file → `Symbol stmtir/SIf is already defined`.
2. **Context bloat / OOM (TRUE regression).** `Module6_WhyMLTranspiler.py` went **PASS → FAIL** — 2 goals
   `Unknown (why3: Out of memory)`, confirmed in single-threaded isolation (not concurrent flakiness). The
   full theory (stmtir ADT + 4 mutually-recursive size fns + 2 `let rec lemma` + 3 corollary lemmas + forced
   `list.List/Mem/Append` imports) inflates the shared-module SMT context enough to OOM previously-proving
   goals. Fidelity gates unaffected (67/67 sync, 51/51 mirror). All OTHER green `@mutable_state` mirrors
   (types/functions/ir_scanner/auto_trust/preamble/…) stayed green.

**Two ADDED next-session requirements (beyond the `list <T>` param family + S-C2/S-C3 body work):**
- **(G1) Narrow the trigger.** Emit the `stmtir` theory ONLY into a module that actually has a
  `List["StmtIR"]` param/field — NOT all `@mutable_state`. (The `@mutable_state` gate is too coarse.)
- **(G2) Collision guard + OOM-aware theory.** Guard against a file's own emitted `stmtir`/`stmt_ir`/`SIf`
  (reserve a prefix, e.g. `_sw_stmtir`, or suppress when the name is already declared); and keep the emitted
  theory LEAN (the OOM shows the 5-lemma bundle is too heavy for a large shared module — emit only the lemmas
  a present walker actually needs, or a slimmer measure).

**Net:** the foundation's three halves are now each measured — S-C1 theory (proves, byte-inert), the `list <T>`
param family (bounded, byte-inert), and the mirror-emission safety (BREAKS as gated → needs G1+G2). The
next-session build must land trigger-narrowing (G1) + collision/OOM guard (G2) BEFORE S-C1's theory can emit
into the mirror, then S-C2/S-C3 for the body. Deferred with all gaps pinned.

## 2. First action — the EMITTER make-or-break spike (Gate S of the build)

BEFORE any converter work, in a worktree, answer ONE question: **does PyCSL emit a valid, provable `stmtir`
theory (variant + `size`/`size_list` + element-decrease lemma) from the `StmtIR` sum, the way it does for
`ExprIR`?**
- Inspect `preamble.py::_emit_exprir_theory` (the expr precedent) and whether an analogous stmt-theory emitter
  exists or must be written. Determine if the generator is parameterized over the ADT (reusable for `StmtIR`)
  or hard-coded to `ExprIR`.
- Emit the `stmtir` theory for the real `StmtIR` sum (at least `SReturn`/`SIf`/`STry`) and diff its shape
  against the hand `stmt-walker-spike.mlw` that already proves. GATE: the EMITTED theory must prove
  axiom-free (same 14/14 character), and `SIf`/`STry` children must come out `list stmtir` (NOT `array stmtir`
  — else Why3 type-rejects, per §0's oracle finding).
- If the emitter can only produce `array stmtir` children (mutable) and cannot be made to emit `list`/`seq`,
  STOP — that is a real emitter obstruction to record (though the spike shows the TARGET wants `list`, so this
  is a generator fix, not a boundary).

## 3. The build (converter capabilities, dependency order — each spike-gated, byte-diff-0, ledger-3)

- **S-C1 — the `stmtir` variant theory emission.** Generate the `stmtir` WhyML variant from `StmtIR`
  (list-children as pure `list`/`seq stmtir`), with the mutually-recursive `size`/`size_list` measure and the
  element-of-list-child decrease `let rec lemma` — the `_emit_exprir_theory` analogue for statements. Reuse the
  expr generator if parameterized; else write the stmt twin. (§2 is this capability's make-or-break.)
- **S-C2 — list-child field projection.** Lower a Python `s.body` / `stmt.orelse` access (where `s : StmtIR`)
  to the variant field projection yielding `list stmtir`, and `for h in s.handlers` / `for x in s.body` to a
  `list`-fold/map — NOT the current `subscript_get` (which types `int` and causes the reported
  `int` vs `array int` failure). This is the core fix.
- **S-C3 — recursive-walker signature synthesis over `stmtir`.** A mirror method `f(stmts: List[StmtIR]) ->
  bool/Set[str]` recursing into child lists must synthesize a WhyML signature over `list stmtir` with the
  `variant { size … }` measure, discharging termination via S-C1's lemmas. (The spike's `ends_with_return` is
  the exact witness.)
- **S-C4 — the accumulator return types.** Walkers return `bool` (easy), `int`, or `Set[str]` / `Dict`
  (needs the set/map value model already used elsewhere). Convert `bool`-returning walkers FIRST (e.g.
  `ir_scanner.ends_with_return`, `has_continue`, `has_early_return`, `uses_break`), then set/map returners.

## 4. Build order & first converted target

`§2 emitter spike → S-C1 → S-C2 → S-C3 → convert `ir_scanner.ends_with_return` (or `has_continue`) — the
minimal `bool` witness, the exact shape the spike proved → then the other bool walkers → then set/map returners
(`find_assigned_vars`, `collect_user_exceptions`) as S-C4 lands`. All-or-nothing per method (one commit at the
conversion). First target: a `bool`-returning `ir_scanner.py` walker — the closest live match to the spike.

## 5. Gates (per converted walker)

- fidelity (`self-annotate-mirror-check.sh` 52/52 + sync no-new-divergence); `--fun` + WHOLE-FILE proof of the
  changed mirror file SUCCESS (§10.10 — the whole-file plane is what caught the `_field_type_for` support-helper
  gap; the walker + its `stmtir` theory must prove TOGETHER);
- byte-diff-0 (S-C1/S-C2/S-C3 fire on `StmtIR`-typed recursion → gated on whether any REFERENCE-CORPUS program
  has a frozen-dataclass sum with a `List[Self]` field walked recursively; measure — likely corpus-inert, but
  the authoritative worktree sweep is REQUIRED, recognizer builds are the perturbation risk);
- ledger 3: the `stmtir` variant is a NEW WhyML value shape → the coupling rule applies. Per the review: a
  READ-ONLY walker constructs no value; IF the stmt theory is emitted **match-based/axiom-free** (as the spike
  is — 0 `^axiom`), no soundness certificate fires and termination (the `variant` VC) is the only concern. GATE:
  emit axiom-free (no projector-axiom style); `Print Assumptions` / `#print axioms` unchanged (stay at 3);
- non-vacuity (the walker recurses into REAL child lists via S-C2, no opaque `subscript_get` collapse); count
  strictly down.

## 6. Honest scope & non-goals

- The spike covers the dict-IR **Schema 1** (34/42 walkers). The pure_ast attribute-node walkers (**Schema 2**,
  8/42: `ConcurrencyChecker`, the unparser) need a SEPARATE `ast.AST`-hierarchy schema — a smaller follow-on,
  OUT of this plan.
- Match/Case constructors were not in the target spike (leaves + If + Try were); add them in S-C1 when a
  Match-walking method is converted.
- The emitter GENERATION is unspiked until §2 — only the TARGET is proven. §2 is the make-or-break of the
  *build*; if it fails (emitter can't emit `list stmtir` children / can't reuse the ADT generator), that is a
  generator obstruction to record, not a boundary (the target wants exactly what the spike proved).
- Ledger stays 3; if the stmt theory needs a certificate the read-only ADT lacks, that is the coupling-rule
  obligation to co-land axiom-free, not a silent axiom.

## 7. First action (restated, actionable)

**§2 emitter make-or-break spike in a worktree:** read `preamble.py::_emit_exprir_theory`; determine if it (or
a sibling) can emit a `stmtir` variant with `list stmtir` children + `size_list` + the element-decrease lemma
for the `StmtIR` sum; emit it and confirm the EMITTED theory proves axiom-free (14/14 character) with `list`
(not `array`) children. PASS → S-C1..S-C4 then convert the first `bool` walker. FAIL → record the exact
generator obstruction. This is the half the target spike did not cover (emitter-generability).
