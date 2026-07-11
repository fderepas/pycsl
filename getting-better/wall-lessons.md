# wall-lessons.md — the self-tcb-reduction-driver lesson store

*The Gate S-lesson ledger (per `config/skills/self-tcb-reduction-driver/SKILL.md`). One entry per driver
run/resolved wall. A lesson is written ONLY after its trigger/validity test returns PASS or CARVE-OUT,
with the wall it came from and the `L`-input that revealed the divergence. Over-general lessons are carved
to their valid complement, never kept whole; irreconcilable ones are REJECTED and logged.*

---

## 2026-07-10 — Driver run #1: Gate W discriminated a non-wall (RecordInfoView value-typing)

**Wall-signal (from the base loop):** `_field_type_for`/`_field_type_of`'s value read
`info.get("field_types",{}).get(f)` int-collapses because a `Dict[str, <RecordInfoView TypedDict>]` field
emits `map string (option int)` (opaque value), not `map string (option recordinfoview)`. First surfaced
by the U build (`file-type-of-wall-impl.md` status).

**Gate W cheap-win test (the `L`-input):** read `_m5_get_dict_value_type` (`Module5_IREmitter.py:3688`).
It returns `"string"` for `Dict[str,str]`, `"map int (option ν)"` for `Dict[str,Dict]`, `"seq T"` for
`Dict[str,List]`, and **`return None`** for `Dict[str, <record-name>]` — a MISSING case, not a wall. The
fix is one recognizer branch (if the value annotation is an `ast.Name` naming a declared TypedDict/record,
return its `whyml_name`), analogous to the existing three. **Verdict: NOT A WALL — a bounded recognizer
gap the base loop handles inline. Gate W did NOT escalate** (no report/review/impl cycle spent). This is
the cost-control gate working: the expensive cycle is reserved for walls where a build could be REFUTED,
not routine recognizer additions.

**Lesson (ignore-signal kind → trigger test):**
> Candidate rule: *"a `Dict[str, <TypedDict>]` value that emits opaque `option int` is a wall
> (leave-trusted / needs a review cycle)."*
> **Trigger test (perturb the signal against `L`):** does the opaque emission actually resist a bounded
> fix? Measured NO — `_m5_get_dict_value_type` simply lacks the record-value case; adding it is the same
> shape as its three existing cases. So the "wall" signal is spurious here.
> **VERDICT: CARVE-OUT.** The rule is kept only for value shapes that genuinely resist a recognizer
> (e.g. an iterated map — `_field_type_of`'s `.values()`, the certified map-iteration boundary). For a
> *keyed-read-only* `Dict[str, <declared record/TypedDict>]`, it is NOT a wall — **check for a missing
> `_m5_get_dict_value_type` case before escalating.**

**Carried-forward carve-out (the reusable takeaway):**
> **"opaque `option int` value ≠ wall."** Before escalating a `Dict[str, ν]`-value opaqueness to a wall,
> check whether `ν` is a shape `_m5_get_dict_value_type` already could handle with one more case
> (str / Dict / List / **declared record-or-TypedDict name**). Only a value that must be *enumerated*
> (not just keyed-read) is a genuine map boundary (see `file-type-of-wall.md`). Sibling of the reviewer's
> earlier carve-out *"search-by-value-field ≠ enumerate — check for a missing index before `pydict`."*

**Driver outcome:** no wall escalated this run. The RecordInfoView recognizer is a cheap base-loop item
(part of the scoped `_field_type_for` build, which additionally needs U + §10.4 re-port — a build, not a
wall). The frontier's genuine walls are already resolved: `_field_type_of` full-body map-iteration =
CERTIFIED-BOUNDARY (`file-type-of-wall.md`, S-R2 spike refuted); U mechanism = VALIDATED (a build, not a
wall). Gate W's discrimination — flagging nothing this run — is the calibrated behavior (a driver that
escalates everything, or nothing without measuring, is miscalibrated).

## 2026-07-10 — Driver run #2: FULL cycle fired — Term-rewriter wall = BOUNDED FEATURE (oracle-refuted the boundary)

**Wall-signal:** the `proof2why3/canonical.py` term rewriters (`_flip_comparisons`, `substitute`, …) —
recursive AST tree-REWRITERS that consume an immutable `Term` (9-constructor sum) and CONSTRUCT a
transformed `Term`. Gate W cheap-win test: clearly not cheap (construction + list-child recursion +
termination, well beyond the reader recognizers) AND breakability genuinely UNKNOWN (no converted method
constructs an ADT value). **Gate W ESCALATED** — the full report→fable-review→impl cycle fired.

**The cycle (all four gates exercised):**
- **Report** `term-rewriter-wall.md` — SOTA framing (verified AST-transformation is native proof-assistant
  territory; the question is the SMT/contract setting + the emitter path), 3 suspected fault lines
  (C: construction, L: list-child map, T: termination), 3 costed routes, open question "boundary or bounded?".
- **Gate R (fable review, artifact-teeth)** `term-rewriter-wall-response.md` — an INDEPENDENT fable agent
  (blind to the sub-loop) RAN the oracle: wrote `term-rewriter-spike.mlw` (a `term` variant with fixed-arity
  `Binop` AND list-child `App (list term)`, mutual `size`/`size_list`, the `flip`/`flip_list` rewriter with
  `variant`, the element-decrease as a proved `let rec lemma`) → **6/6 Valid (Alt-Ergo + Z3), 0 axioms**,
  negative control fails (non-vacuous). Verdict: BOUNDED FEATURE. Gate R passed WITH the artifact.
- **driver-verifier (check the claim)** — independently re-proved the spike (6/6 Valid) and CAUGHT-then-cleared
  the "0 axioms" claim: `grep -c axiom` = 5, but all 5 are COMMENTS; `^axiom ` = 0 real declarations →
  ledger-clean confirmed. (The claim survived verification — but the driver checked, it didn't trust.)
- **Gate P impl plan** `term-rewriter-wall-impl.md` — spike-first (the make-or-break already PASSED),
  refutation exit moot (confirmed breakable). Scopes the EMITTER build (T-C1 recursive-constructor emission
  from a dataclass call; T-C2 comprehension→recursive helper; T-C3 list-leg `size` + element-decrease lemma;
  T-C4 term-typed return), with the one open coupling-rule check (a CONSTRUCTED term value may need the
  certificate to cover the constructor eliminator, not just projection).

**Lesson (defer-to-oracle kind → validity test → PASS):**
> **A recursive-ADT tree-REWRITER (construct + list-child map + structural termination) is a BOUNDED
> FEATURE, not a boundary — proven axiom-free by spike.** It sits between the two poles already on record:
> the reader ADT (`emit_ir`, SOLVED — projection only) and the map-values-iteration wall
> (`file-type-of-wall.md`, BOUNDARY). Validity test: the oracle spike genuinely distinguishes the case
> (6/6 Valid, control fails) and sanctions the action (build, don't leave-trusted). PASS.
> **Carry-forward:** before classifying an ADT-transforming method as a boundary, SPIKE the target (variant
> + list-child map + `size_list` measure) — construction and structural termination discharge in Why3
> axiom-free; the real cost is emitter-GENERATION (the M2 gap: target-provable ≠ emitter-generable), a
> build, not a wall.

**Driver outcome:** the wall is BREAKABLE (bounded feature) — NOT a certified boundary. The independent
oracle review overturned the report's uncertainty. Next phase = the emitter build (`term-rewriter-wall-impl.md`
T-C1..C4), spike-gated on T-C1 (emitter-generability, the half the target-spike didn't cover). This run
demonstrates the FULL driver cycle (contrast run #1, where Gate W correctly declined to escalate a non-wall).

## 2026-07-11 — Driver run #3 (AUTONOMOUS, 4h): Phase 1 = no_cheap_remaining; Phase 2 = _field_type_for build
Phase 1 drain: confirmed the cheap-conversion supply is EXHAUSTED (reader byte-0 wins all landed; the last
untested class, the `_collect_*` stmt-walkers, measured NOT cheap — `for s in stmts` over `List[Dict]` +
Set/dict accumulators = a stmt-walker feature gap). → Phase 2. Target: the `_field_type_for` build (all
pieces now scoped: reverse index [validated byte-inert], U [mechanism validated], RecordInfoView recognizer
[bounded — `_m5_get_dict_value_type` + the `_m5_record_class_names` registry], §10.4 re-port of the 2 U-edited
verified methods). Delegated + driver-verifier-gated.

**RESULT: STOPPED at net 0 — REVERTED to clean (count held 1226). `_field_type_for` is NOT a bounded
landing; it is a RECEDING-HORIZON build that bottoms out at the SAME gap the Phase-1 `_collect_*` drain did.**
Two converter passes (validated recipe + a 4th/5th recognizer pass) built EIGHT pieces — reverse index,
RecordInfoView value-typing (+3 sub-additions), U union-early-return (3 edits), §10.4 re-port, `opt_record_local`
first-assign kind, `_collect_opt_record_var_assigns` stmt-walker, `option recordinfoview` truthiness, and the
`_opt_record_field_types_get` compound-chain recognizer. With ALL of them the target body *itself* proves
(`--fun typeinferencemixin___field_type_for` = SUCCESS). But landing it as a real −1 requires the mirror to
carry a body-faithful `_collect_opt_record_var_assigns` (the stmt-list-walker that typed-classifies the
opt-record local so it escapes the blanket `ref 0` pre-declare). That walker does NOT verify:
- `src/self-annotate/src/module6_whyml/types.mlw:457` (whole-file): `found := (map_union !found
  (self__collect_opt_record_var_assigns_1 (subscript_get !s !k)))` → **"This expression has type int, but is
  expected to have type array.Array.array int"**. The recursion over nested `s["body"]`/`s["orelse"]` lowers the
  sub-list arg via `subscript_get` (yields `int`) while the recursive callee's synthesized signature expects
  `array int` — **the generic stmt-list-walk lowering gap.** Making the walker a `\trusted` stub instead adds
  +1, exactly cancelling the −1 → net 0. Hard-stop taken; whole tree reverted.

**CONVERGENCE INSIGHT (the high-value takeaway):** the `_field_type_for` build and the entire Phase-1
`_collect_*` stmt-walker class DO NOT have two problems — they have ONE: **the recursive stmt-list-walk
lowering gap** (`subscript_get` on a `Dict[str,Any]` stmt's `s["body"]`/`s["orelse"]` list-child yields `int`,
not `array int`, so a recursive walker over the stmt tree cannot type-check). Fix that ONE gap and BOTH the
`_collect_*` drain AND `_field_type_for`'s completion unlock together. This is the pivotal next wall — and it
is the SAME shape as lesson 3's leave-trusted class (`Dict[str,Any]` generic-tree walkers), so the prior is a
BOUNDARY, but the double-hit elevates it to Gate-W escalation for a definitive oracle verdict.

**Lesson (receding-horizon kind → validity test):**
> A build advertised as "all pieces scoped" can still RECEDE if one piece's own body-verification obligation
> lands on an UNSOLVED emitter gap. Validity test: after the target body proves under `--fun`, does the
> WHOLE FILE prove? Here NO — a support helper (`_collect_opt_record_var_assigns`) hit the stmt-list-walk gap.
> **Carry-forward:** before scoping a reader-conversion as bounded, check whether it needs a NEW recursive
> stmt/expr-tree WALKER helper in the mirror. If it does, it inherits the generic-tree-walk boundary (lesson 3)
> — treat as feature-gated, not a cheap landing. `--fun`-proves-the-body ≠ file-proves (SL lesson 10 restated
> for support helpers, not just siblings).

**CENSUS (2026-07-11, read-only probe) — the stmt-walk gap unlock is WORTHWHILE (42 methods).** Measured the
cluster the stmt-family typed-node ADT would unlock: **42 bucket-A recursive stmt-tree walkers** (iterate a
stmt list AND recurse into nested `s["body"]`/`s["orelse"]`/`s["finalbody"]`/`handlers` children). Split:
- **Schema 1 — dict-IR `StmtIR` sum: 34/42 (81%).** `core_ir_semantic.py` (8: `_noreturn_walk_stmts`,
  `_final_walk_body`, `_final_check_stmt`, `_union_c8_walk`, `_pb_body/_pb_stmt`, `_cs_body/_cs_stmt`),
  `ir_scanner.py` (20 — a dedicated "stateless recursive walkers over the IR dict tree" class: `uses_arrayset`,
  `ends_with_return`, `find_assigned_vars`, `find_ghost_vars`, `has_continue`, `collect_user_exceptions`,
  `has_early_return`, …), `types.py` (`_collect_tuple_var_assigns`, `_collect_array_var_assigns`), Module5
  `_scan_2d_in_stmt`, `auto_trust._collect_map_typed_locals`, `ir_inline.inline_stmts`, and the giant
  `statements._stmts_to_whyml`. KEY: the Python-side typed `StmtIR` sum ALREADY EXISTS
  (`statements.py:stmt_from_dict`/`.to_dict()`, "ir-schema-spec.md §6 Phase B") — but handlers round-trip
  `stmt.body`/`.orelse` back through `.to_dict()` into `List[Dict[str,Any]]` before recursing, which is
  exactly where `subscript_get: int` vs `array int` bites. Data-model half built; the WhyML-lowerable typed
  signature (`array stmtir` fields, no dict round-trip) is missing. ~7 constructors (If/While/For/Try/
  ExceptHandler/Match/Case).
- **Schema 2 — pure_ast attribute-node ADT: 8/42 (19%).** `ConcurrencyChecker._walk_body/_walk_stmt` +
  `pure_ast._Unparser` (`visit_If/While/For/Try/TryStar`, `do_visit_try`) — attribute-based dataclass nodes,
  a SEPARATE schema mirroring Python's `ast.AST` hierarchy.
- Bucket B (~25, NOT this gap): generic `.values()`/`.items()` full-node reflection + `ast.walk`/`iter_child_nodes`
  black-box walkers = the HARDER generic-Any gap (lesson 3), a different boundary.
**VERDICT: escalate Schema 1 (34-method unlock, half-built) as a genuine Gate-W wall → report+oracle-spike
cycle. `stmt-walker-wall.md`.**

**ORACLE CYCLE COMPLETE (2026-07-11) — stmt-walker wall = BOUNDED FEATURE; build DEFERRED with the gap pinned.**
Full driver cycle fired (report → independent fable oracle → impl plan → §2 emitter spike):
- **Fable oracle (blind to sub-loop)** wrote `stmt-walker-spike.mlw`: `stmtir` variant with a 4-list-child
  `STry` + handlers as a mutually-recursive second sort, cons-cell `size`/`size_list`, element-decrease as a
  PROVED `let rec lemma`, reader `ends_with_return` with `variant`. **Driver-re-verified: 14/14 Valid on
  Alt-Ergo AND Z3, 0 `^axiom`, `bad_walk` control Timeouts (non-vacuous).** `array stmtir` is Why3-TYPE-REJECTED
  → child MUST be pure `list`/`seq`. (R)/(L)/(T)/multi-field all PASS. Verdict: BOUNDED FEATURE, not a boundary.
- **§2 emitter make-or-break (isolated worktree): GENERABLE-WITH-GAP.** S-C1 (`_emit_stmtir_theory`, the
  `_emit_exprir_theory` twin) EMITS the proven theory → **9/9 Valid both solvers, 0 axioms, `list` children,
  corpus-byte-inert** (stash-diff confirmed). But the walker lowering needs **≥3 new recognizers** and
  hard-stopped (no sprawl): the pinned make-or-break is **`functions.py:68-97` — `_param_type_str` routes EVERY
  `List[T]` param into the `array <T>` family; there is NO `list <T>` exit**, so `List["StmtIR"]`→`array int`
  (the live failure's root). Plus a `stmts[-1]`→`Cons`-recursion body recognizer and `variant { stmt_size }`
  synthesis.

**PIVOTAL CONVERGENCE (the run's top finding):** the `list <T>` ADT-child type family + list-structural
recursion body form is needed by BOTH remaining breakable walls — the **stmt-walker** (34 readers, this) AND
the **term-rewriter** (`term-rewriter-wall-impl.md` T-C2/T-C3: comprehension→`list term`, `list`-child
constructor). ONE shared foundation (`functions.py`'s `list <T>` param/field family + the `Cons`-recursion body
form) unblocks both. That is the pivotal next-session build; S-C1's theory-emission recipe is proven-ready and
byte-inert, waiting on the param-family fix.

**`list <T>` type-family probe + SUITE-SAFETY gate (2026-07-11):** (a) the `list <T>` param exit is BOUNDED +
corpus-byte-inert (~185 lines, signature emits `list stmtir`); BUT (b) the **self-annotation-suite safety gate
= BREAKS as gated** — the theory is `@mutable_state`-gated and the MIRROR files ARE `@mutable_state`, so it
emits into their own `.mlw` and (1) COLLIDES with three files already declaring their own `type
stmtir`/`stmt_ir`/`SIf` (`stmt_control_flow.py`, `statements.py`, `expressions.py`), and (2) OOMs
`Module6_WhyMLTranspiler.py` (PASS→FAIL, 2 goals `Out of memory` — TRUE regression from the 5-lemma theory
bloating the shared module). **Added next-session requirements: (G1) narrow the emit trigger to modules that
actually contain a `List["StmtIR"]` param/field (not all `@mutable_state`); (G2) collision guard (reserved
prefix / suppress-when-declared) + a LEAN theory (emit only the lemmas a present walker needs).** Meta-lesson:
byte-inert-on-corpus ≠ safe — the mirror IS `@mutable_state`, so ANY `@mutable_state`-gated emitter feature
must pass the FULL self-annotation suite (collision + OOM), not just the corpus byte-diff. All four foundation
facets now measured (S-C1 proves+inert; `list <T>` param bounded+inert; mirror-emission needs G1+G2; body needs
S-C2/S-C3) — deferred with every gap pinned.

**12h-run increment #1 — REJECTED (facade + wrong-base), two process findings:**
- **FACADE (Gate C non-vacuity FAIL).** An executor tasked to "land the first −1" built
  `_maybe_emit_ir_dict_list_walker` (functions.py) that returns a **hand-written literal WhyML body** for
  `ends_with_return`, gated on `func.get("body") == _SW_ENDS_WITH_RETURN_BODY` (an exact-body fingerprint) and
  failing closed on drift. This is NOT a faithful lowering — the emitter substitutes a canned proof the
  executor authored; it does not generalize (would need one fingerprint + one hand-WhyML per method). REJECTED:
  a per-method fingerprint→canned-WhyML is a facade factory (any hard method "converts" by hand-writing its
  proof into the emitter). **Anti-facade rule going forward: the lowering must be a GENERAL recognizer proven
  by converting ≥2 structurally-similar walkers through ONE code path; no hand-written per-method WhyML bodies,
  no per-method fingerprints.**
- **WORKTREE-TOOLING BUG.** `isolation: worktree` provisioned EVERY worktree this session at `f552646c`
  ("Merge ghost-assign-bc6 into main") — **NOT an ancestor of the branch tip `40115583`, 191 commits
  divergent**; the four relevant files differ by hundreds of lines (functions.py +487, preamble.py +457). So
  worktree-isolated builds are un-portable and their emitter-side findings need re-verification at HEAD. The
  core oracle (`stmt-walker-spike.mlw` 14/14) is SAFE — it was authored+verified in the MAIN tree.
  **Going forward: build in the MAIN tree (non-isolated, single-writer, revert-on-failure); do NOT trust
  worktree isolation for base-sensitive work.** (The `functions.py` list-param→array gap and the
  three-file `type stmtir`/`SIf` collisions DO reproduce at HEAD structurally — re-confirm before relying.)
- **The deeper truth this exposes:** target-provability (the 14/14 spike) ≠ faithful emitter-generability. The
  facade is EVIDENCE that faithful generation (general dispatch-on-`.get("stmt")` + list-child projection +
  Cons/Nil recursion, reusing the emit_ir/ExprIR ADT lowering precedent for the StmtIR family) is the real,
  hard, unbuilt core — an executor under count-pressure routes around it via a facade. The genuine build is
  the emit_ir-ADT-extension to statements (lesson 8's deferred stmt-family), NOT a per-method hand-lowering.

**Lesson (defer-with-pinned-gap kind):**
> When a wall is oracle-proven BREAKABLE but the emitter build reveals a genuine multi-recognizer M2 gap, the
> driver's win is the PINNED gap + a proven-ready foundation piece, NOT a forced conversion. Land nothing that
> reduces no count (lesson 7); DEFER the build with the exact make-or-break line recorded (`functions.py:68`,
> the `list <T>` param family) so the next session builds deliberately, not blind. Distinguish this from a
> CERTIFIED BOUNDARY (map-iteration, generic-Any walkers): a deferred-breakable has a proven target + a pinned,
> bounded gap; a boundary has neither.
