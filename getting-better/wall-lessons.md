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

**Stmt-walker campaign (2026-07-12, 8h runs) — recognizer-reuse breakthrough draining the cluster.**
1226→1211 via general, certified-machinery recognizers (each triple-plane gated, ledger held at 3, zero
facades, corpus always byte-inert). Landed recognizers in `generic_fold.py`: `recognize_bool_existence`
(generalized to any-tag + compound-guard + inline-if-descend: uses_arrayset/for/continue/break/ghost_type,
has_continue), `recognize_stmt_setfold` (3 sub-shapes value_guarded/direct/chain: find_lambda_vars/
record_vars/ghost_vars/append_targets), `recognize_void_dispatch` (_pb_body/_cs_body/_final_walk_body),
`recognize_void_generic_descend` (_pb_descend/_cs_descend). See [[stmt_walker_recognizer_breakthrough]].

**COUPLING/ORDERING FINDING (_pb_stmt/_cs_stmt BLOCKED — a boundary given current emission):** the
multiway-context twins `_pb_stmt`/`_cs_stmt` cannot be converted faithfully BECAUSE the already-landed
void-family siblings (`_pb_body` via `recognize_void_dispatch`, `_pb_descend` via generic-descend) pass
`_pb_stmt` a bare opaque `int` / literal `0` (the sound "trusted callee can't observe it" handle). Why3
pins `_pb_stmt`'s signature to `(s: int)` across the module → a scalar with NO projectable dict structure,
so its 4-arm dispatch's field reads (`s.get("invariants")`/`variants`/`body`) can't be lowered. The 3
escapes all violate discipline: re-emit siblings (changes verified contracts), an int↔pyval decode theory
(new axiom), or fabricate constant trip counts (a REJECTED facade, per the increment-#1 lesson). **Lesson:
converting a tree-walker's DESCEND/BODY siblings with the opaque-handle trick FORECLOSES faithfully
converting the sibling that NEEDS the real subject structure (the multiway dispatcher). Order matters — a
dispatcher that projects real fields must be converted with a pyval subject BEFORE (or together with) its
callers, or its callers' opaque-int emission makes it a boundary.** For now `_pb_stmt`/`_cs_stmt` = boundary
(reversible only by a larger increment that re-emits the whole `_pb_*`/`_cs_*` family with a pyval subject).

**Stmt-walker campaign near floor (2026-07-12, 1226→1206 = −20 via recognizer reuse). Remaining cluster
members characterized:** the ≥2-via-one-matcher tractable walkers are DRAINED. Boundary map of the rest:
- **Opaque-int-coupling boundaries** (same class as _pb_stmt): `_final_check_stmt` (its converted caller
  `_final_walk_body` passes `s` opaque → signature pinned to `(s: int)`, no projectable fields). `_pb_stmt`/
  `_cs_stmt` (prior). Reversible only by re-emitting the whole caller family with a pyval subject.
- **Single-instance shapes** (below the ≥2 generality bar → a new recognizer for ONE method risks a
  fingerprint/facade): `_union_c8_walk` (per-tag dispatch + sibling-call-with-real-args; NOT caller-coupled,
  so tractable IN PRINCIPLE, but only 1 instance of the shape in the mirror).
- **New-feature builds**: `_noreturn_walk_stmts` (STATEFUL — threads `prev_noreturn_call` across loop
  iterations, order-dependent conditional raise; no fold-recognizer precedent — a genuinely new
  state-threaded-void-fold primitive).
- **Different-value-model boundaries**: `_collect_mutations` (by-ref `out:List`), `find_array_and_dict_vars`/
  `find_iteration_mutations` (Tuple/record returns), `_collect_tuple_var_assigns` (Dict + self-side-channel),
  `_collect_array_var_assigns` (fixpoint `while changed`), `find_assigned_vars` (unbounded by-ref side-call),
  `collect_escaping_exceptions` (external `handler_catches` oracle), `uses_inline_set_or_dict_ops` (generic-Any
  `.values()` walker = lesson-3 boundary).
**Doctrine applied:** do NOT build a single-instance recognizer (facade risk) or grind bespoke +1 new-value-model
machinery on the heavy file for diminishing return. The stmt-walker wall is at its recognizer-reuse floor.

**GHOST-HANDLER cluster at floor (2026-07-12) — clean projector-reuse vein exhausted, 1226→1188 (−38).**
~19 ghost expr-handlers converted via byte-inert emitter enablers (gating fix + `_EMIT_IR_NODE_ATTRS`/
`_EMIT_IR_STR_ATTRS` name→projector maps reusing IrBinOp's left_of/right_of + name_of; NO emit_ir theory
change, ledger held 3). REMAINING = BLOCKED on deeper features:
- **elem/set + nth/mem/proj/ctor_test (7): BLOCKED on emitter subtype-tracking.** `_handle_attribute_expr`
  (expressions.py:5059) sees only the attr NAME (`expr.get("attr")`), NOT the node's ExprIR SUBTYPE. A
  name→projector map can't disambiguate position-SWAPPING names (`SetAddExpr(set,elem)` vs
  `SetMemExpr(elem,set)` — `elem` is field-2 in one, field-1 in the other). Fixing needs the node subtype
  threaded to the generic attr-lowering site (a deeper emitter feature) or ir_schema field renames (touches
  live code — out of scope). A per-handler map would be a facade.
- **map_set/set_card/str_sub/ctor_payload/ghost_copy_range/ghost_make (6): need a 3rd projector** (emit_ir
  only has left_of/right_of for 2-child; a 3-child node needs a new projector, likely a theory-adjacent add).
- **mktuple (1): variadic `elts`** — needs list-child handling.
CAUTION for any future projector-table edit in expressions.py: it reroutes expressions.py's OWN mirror
(BinOp/ArrayEq/Permutation handlers) → MUST re-prove expressions.py (~15-20min, the largest mirror file).

**GHOST-HANDLER cluster at FAITHFUL floor (2026-07-13, 1226→1183 = −43).** ~21 handlers converted via
byte-inert projector-map reuse (0/1/2-child unambiguous names dict/key/head/tail/left/right/lo/hi/size/
default → left_of/right_of; scalars → name_of; 3-child map_set/set_card via the 3rd child's svalue_of
default — 3 DISTINCT projectors, no collision). REMAINING BLOCKED for a FAITHFUL conversion:
- **elem/set/nth/mem/proj (swap): no subtype info.** All live handlers type `node: "ExprIR"` (base), so a
  name→projector map can't faithfully disambiguate a name whose FIELD POSITION swaps across subclasses
  (`SetAddExpr(set,elem)` vs `SetMemExpr(elem,set)`). DOCTRINE NUANCE: they ARE convertible under the fixed
  `ensures True` contract (map one swap-name → left_of, the other falls to svalue_of default → 2 distinct
  size-bounded projectors → proves type-safety+termination, non-facade) — BUT the projection is
  value-UNFAITHFUL (wrong child) and needs a position-INCONSISTENT global map entry. Held the FAITHFUL line
  (VALUE-not-count): did NOT manufacture these. A faithful conversion needs subtype-tracking (thread the
  handler's specific ExprIR subtype to `_handle_attribute_expr`, which today sees only the attr NAME) — a
  deeper emitter feature, or specific-subtype live-signature annotations (risky live change).
- **ctor_test**: `Array.make !arity` precond `n>=0` undischargeable (abstract arity getter has no
  `ensures result>=0`) — needs a nonneg-safe getter.
- **mktuple**: variadic `elts` list.
This is the practical FAITHFUL floor of the projector-reuse vein. Further ghost progress needs a deeper
emitter feature (subtype-tracking / nonneg-arity / variadic) or a user decision on value-unfaithful-but-
type-safe conversions.

**PROCESS CORRECTION (2026-07-13, user-prompted) — I declared a "floor" WITHOUT escalating to the fable
oracle, and it was WRONG.** After draining the ghost cluster to 1183 I called the remainder a floor
(needs-deeper-feature/boundary) on MY OWN authority. The user asked why I didn't ask Fable. I ran the
Gate-W→R cycle (`ghost-handler-wall.md` → independent fable oracle → `ghost-handler-wall-response.md` +
`gh-spike.mlw`/`gh-spike-controls.mlw`, driver-re-verified: 22/22 Valid, 0 `^axiom`, negative controls fail).
**Verdict: NO FLOOR — every remaining ghost handler is a BOUNDED FEATURE, axiom-free:**
- swap handlers (elem/set/nth/mem): a per-subtype/per-handler projector table gives FAITHFUL distinct
  projections (the disambiguating key — each `_handle_X` statically handles ONE subclass — IS available);
  BOUNDED, no live-source change, no axiom.
- 3-child (map_set/set_card): FAITHFUL via a real 3rd projector (`Q1FaithfulThirdChild` spiked Valid,
  axiom-free) — better than the value-degenerate `svalue_of` sentinel.
- ctor_test: `ensures result>=0` on the abstract arity getter discharges `Array.make`'s precond (Valid).
- mktuple: `IrTuple (list term)` + list projector + fold under `ensures true` (5/5 Valid).
**Two lessons:** (1) A "floor" is ONLY real when a fable make-or-break spike REFUTES the build — my own
"this is blocked/boundary" verdict is exactly what the driver's Gate R exists to distrust (cf. term-rewriter
+ stmt-walker walls, both fable-proven BOUNDED after I'd have called them boundaries). Escalate, don't
self-declare. (2) FRAME THE ORACLE CORRECTLY: I described the ghost handlers as RECURSIVE; they are NOT
(they call the trusted abstract `val _e`, `let` not `let rec`), so the oracle's rigorous "sentinel-unsound-
by-termination-substitution" analysis applied to a scenario that doesn't exist — verified the emitted `.mlw`:
`5221ef3d` (map_set svalue_of) is SOUND as a non-recursive type-safety conversion, no bug. A mis-framed
report wastes the oracle on the wrong question.

**GHOST CLUSTER COMPLETE (2026-07-13, 1226→1176 = −50 session) — all ghost expr handlers converted EXCEPT
proj/ctor_payload (reverted by a WORTH judgment, not a breakability boundary).** The fable escalation (after
the user corrected my self-declared floor) unlocked the whole cluster: swap handlers (per-subtype projector
table), ctor_test (arity ensures>=0), map_set/set_card (IrTer3 mini-M1), mktuple (existing args_of +
genexpr→listcomp live refactor). proj/ctor_payload ARE breakable but an executor sprawled to build them —
num_of int-projector mini-M1 + a list-local-from-`.get` recognizer (ir_scanner.py) + native-element-write
(statements.py, a GENERAL emitter path → corpus-perturbation risk) + a type-inference extension (types.py) +
a helper stub — for a net of only −1 (2 converted, 1 stub added). REVERTED: 3 general-live-emitter-feature
additions + a shared theory + a stub for net −1 is disproportionate blast radius (measure-before-build,
VALUE-not-count, flag-risky-live-changes). **KEY DISTINCTION (post-correction): fable adjudicates
BREAKABILITY; the COORDINATOR judges WORTH. A wall being fable-BOUNDED does NOT mean every instance is worth
building — a net-−1 conversion requiring 3 new general-emitter features that risk corpus perturbation is a
decline-on-worth, not a floor-declaration. Both self-declaring a floor (wrong, per the user) AND grinding a
breakable-but-disproportionate build (wrong, sprawl) are errors; the discipline is escalate-to-verify-
breakability THEN judge-worth.**

**Lesson (defer-with-pinned-gap kind):**
> When a wall is oracle-proven BREAKABLE but the emitter build reveals a genuine multi-recognizer M2 gap, the
> driver's win is the PINNED gap + a proven-ready foundation piece, NOT a forced conversion. Land nothing that
> reduces no count (lesson 7); DEFER the build with the exact make-or-break line recorded (`functions.py:68`,
> the `list <T>` param family) so the next session builds deliberately, not blind. Distinguish this from a
> CERTIFIED BOUNDARY (map-iteration, generic-Any walkers): a deferred-breakable has a proven target + a pinned,
> bounded gap; a boundary has neither.

**_field_type_of / _field_type_for — ORACLE-VALIDATED REVERSE-INDEX, but INSUFFICIENT ALONE → worth-decline
(2026-07-13).** Fable adjudicated the `_field_type_of`/`_field_type_for` wall (`file-type-of-wall*.md`): the
report mis-classified them as needing map-ENUMERATION; the oracle's counter is they need a **reverse index** (a
second keyed map `_record_types_by_whyml_name`, populated at the single write site, since the search key
`whyml_name` is already in the value). The reverse index was SPIKED and VALIDATED: **corpus byte-diff 0**,
sound, re-appliable. BUT the spike also proved neither leaf converts on the reverse index alone — each is gated
on ORTHOGONAL emitter features: `_field_type_for` needs + U (union-return closer + a RecordInfoView TypedDict
value-view) + a §10.4 re-port; `_field_type_of` needs + U + Gap-C (or-`{}`) + a getattr-chain. That is a
**4-feature receding-horizon build for +2** — the same disproportionate-blast-radius shape as proj/ctor_payload.
DECLINED ON WORTH (not a floor, not a boundary): the reverse index alone reduces no count (lesson 7 —
land-nothing-that-reduces-no-count), and the full build's ROI (+2 for 4 general-emitter features, each its own
verification) is negative. The oracle's category lesson is banked: **"search by a field of the value" is NOT
evidence of a need to enumerate — check for a missing index first.**

**_csl_var/_csl_string CONVERTED via a TOOL-CORRECTNESS FIX (2026-07-13, 1176→1174).** Turning the mirror
`PyCSLToJSONEmitter` `@mutable_state` (to construct `IrVar`/`IrStr`) turned on the `emit_ir` theory, whose
top-level `size` measure collided with the bare `size` FIELD of an imported `GhostMakeExpr` record →
`Symbol size is already defined`. Root cause: `_field_label`'s ambiguous-field set never considered names the
`emit_ir` theory reserves. Fix: `_emit_type_decls` unions the theory's declared-symbol set (parsed from
`_emit_exprir_theory`'s OWN emitted text, drift-proof) into the ambiguous set — but ONLY inside the existing
`_mutable_state_classes`-gated block, so corpus programs (never `@mutable_state`) never trigger it → **corpus
byte-diff 0 verified by stash-sweep**. This is the legitimate face of a tool fix (contrast proj/ctor_payload's
sprawl): a genuine correctness gap, one gated line reusing existing machinery, byte-inert, unblocking a
conversion the campaign already wanted. Distinguish: fixing a CORRECTNESS GAP that blocks a wanted conversion
(land it) vs. BUILDING speculative features for a marginal count (decline).

**MODULE5 `_csl_*` CONSTRUCTION FAMILY — census FALSE-GREEN caught; recursive family is a CSL-AST-as-int
frontend BOUNDARY (2026-07-13).** After converting `_csl_var`/`_csl_string` (string-leaf, real IrVar/IrStr),
an automated census ported all ~72 `_csl_*` live bodies + ran `--fun`, reporting **62 SUCCESS**. ALL 62 WERE
FACADES. Two independent tells, both in the emitted `.mlw`: (1) the body was `(IrOther "BinOp")` — a
node-IGNORING sentinel, because `_IRNODE_CTORS` (expressions.py:776) only wires 5 kinds (Var/Attribute/String/
Number/RawWhyml); every other kind falls to `(IrOther "{kind}")` (line 1409), and (2) a Why3 **"unused variable
node"** warning — the body doesn't read `node` at all. A `--fun` SUCCESS under `ensures True` proves the sentinel
body type-safe but the conversion is VACUOUS (removing `\trusted` while the method emits a node-ignoring constant
is the exact reclassification-dodge facade the campaign forbids). **This repeats the tier-1 `--no-proof` 39→8
overcount at the CONSTRUCTION layer: a census MUST check the `.mlw` body reads `node` + constructs the RIGHT
(non-IrOther) ctor, never just `--fun` green.** THEN probed the real fix: the theory ALREADY has IrBinOp/IrSub/
IrTuple/IrCall/IrIfExpr/IrFieldGet — wiring "BinOp"→IrBinOp into `_IRNODE_CTORS` (theory-free, @mutable_state-gated,
corpus-inert) DID make `_csl_binop` emit a real `(IrBinOp node.cslbinop_op (csl_to_ir left) (csl_to_ir right))`.
But it FAILS to prove: the mirror models the **entire CSL AST as opaque `int`** (`type cslbinop = {cslbinop_left:
int; cslbinop_op: string; cslbinop_right: int}`, `val _csl_to_ir (node: int): int`), so the emit_ir children are
`int`, not emit_ir → `IrBinOp` type-rejects them. `_csl_var`/`_csl_string` converted ONLY because they read
STRING fields (`cslvar_name: string`), never int-node children. **The recursive `_csl_*` construction family is
a genuine BOUNDARY under the current modeling: it needs the whole CSL AST record hierarchy re-lowered from `int`
to real node types + `_csl_to_ir` retyped `int→emit_ir` (the `-> "ExprIR"` annotation alone doesn't reach the
cross-call bridge `val self__csl_to_ir_1 (x0:int):int`). That is a deep multi-session frontend remodel (no-more-int
at the CSL-AST layer), NOT a ctor-wiring win.** Fieldless leaves (none/result/nothing → IrOther "None" loses no
data but leaves `node` unused) are doctrine-borderline (ghost-handler Q1) and marginal; not chased. Module5
construction cluster = DONE at var/string; the rest is the int-AST boundary. VALUE lesson: a construction census
without a body-reads-node check manufactures facades at scale.

**MODULE6 ExprIR-BOOL READER CLUSTER = BOUNDARY-BLOCKED, 3 distinct walls (2026-07-13, count held 1174).**
Measured the last coherent convertible-looking class (`_val_is_bool`/`_pattern_has_constructor`/`_is_string_expr`/
`_is_emit_ir_expr`) with a STRICT non-vacuity gate (open the `.mlw`, confirm the body reads its param via a real
projector, reject "unused variable"/IrOther facades). Result: NONE convert, three real walls: (1) **DEPENDENCY-STUB
FIDELITY WALL** — `_val_is_bool`'s statements.py copy transcribes + `--fun`-proves with real `kind_of`/`op_of`
reads, but `self-annotate-mirror-check.sh` REJECTS it: `StatementEmissionMixin` only INHERITS `_val_is_bool` (it's
defined on `TypeInferenceMixin`/types.py, already converted there), and a mirror may only un-trust a method its
LIVE class actually DEFINES. Cross-mixin dependency stubs are IRREDUCIBLE by fidelity (F1-class). This reconfirms
commit 1208215b independently. (2) **MISSING match-pattern ADT projector** — `_pattern_has_constructor(pat)` has
`pat: Dict[str,Any]` collapse to `map string (option int)`; there is no `IrPattern`/`alternatives_of` constructor
in the emit_ir sum, so the recursive walk degenerates to a dummy `Array.make 1 0` and type-errors. Building it is
a new emitter ADT extension for +1 — worth-decline (sprawl). (3) **Recursive multi-state readers** (`_is_string_expr`
consults `_record_types`/`_current_symbol_table`/`_mutable_state_classes`/…) — beyond a two-field projector.
**CONSOLIDATED FLOOR PICTURE: the remaining ~1174 \trusted is dominated by (F1) cross-mixin dependency stubs
[fidelity-irreducible], (F3) int-modeled AST / generic-`Dict[str,Any]` map readers [the 85-reader hard class,
lesson 3] incl. all of functions.py's `_build_method_*_map` + Module5's int-AST recursive family, and a few
missing-ADT-projector singletons [each a deferred build, worth-declined at +1].** The genuinely-convertible
frontier reachable with existing machinery is largely exhausted; further reduction needs either a no-more-int
frontend remodel (Module5 CSL-AST) or new ADT families (match-pattern) — measured multi-session builds, not loop
increments. Anti-facade gate held throughout: every "SUCCESS" was checked for param-read in the .mlw.

**MODULE5 CSL-AST-as-emit_ir BUILD — SINGLE-RETURN FAMILY COMPLETE (2026-07-13/14, 1154→1097 = 57 conversions).**
The user AUTHORIZED the big build after I measured the loop-scale frontier exhausted. Ran spike-first (make-or-break
`_csl_binop` proven end-to-end BEFORE the full build) then family-batched. Mechanism (ledger stays 3, NO new value
shape/certificate — reuses the existing emit_ir ADT): (1) model the CSL contract-AST node children as emit_ir not int
by retyping `CSLNode`→`"ExprIR"` on the LIVE Module2_Parser dataclass fields (pure type-hint, dataclass never
enforces; had to be the LIVE file — cross-module class injection resolves the mirror's import to live); (2)
`functions.py` recognizes an IR-node-tag RETURN annotation as emit_ir so the trusted `_csl_to_ir` dispatcher types
`emit_ir->emit_ir`; (3) wire each `{"type":K}` into `_IRNODE_CTORS` (expressions.py); (4) per node kind add an
emit_ir ctor to `_emit_exprir_theory` (variant arm + kind_of arm + size arm — the IrBinOp template). Batches: FOUNDATION
+binop (29873c2c), FREE bucket 3 via IrSub/IrFieldGet (1aa54b22), spec-op 15 (1768b5c5), map/set/list 24 (56ac0016),
misc 14 (62105a02). Each a **sanctioned mini-M1**: the emit_ir theory grows ADDITIVELY, perturbing ONLY the 15
emit_ir-theory corpus files (0746-0881) additive-only (pre-existing ctors/arms preserved; the `type emit_ir =` +
comment lines show as "changed" only because they're single lines that got longer), re-verified. GATES per batch
(all independently re-run by coordinator): whole-file Module5 proof SUCCESS (size measure stays total with all new
arms), corpus byte-diff = 15 files additive-only + re-verify, non-vacuity on EVERY method (.mlw body reads node +
builds the RIGHT ctor, not IrOther/unused-node — caught the earlier 62-facade census this way), ledger 3.
PRINCIPLED SKIPS: `_csl_bool` (CSLBool.value lowers bool→int, IrBool mismatches), `_csl_number` (value is float, IrNum
is int — no-more-int forbids coercion), `_csl_not_in` (body CONSTRUCTS an input CSLIn node → doesn't unify with
emit_ir), `_csl_contract_wrapper` (abstract base class, `expr` on subclasses). FIDELITY NUANCE (accepted, flagged):
`_csl_ctor_payload`'s `index` arg lowers to literal 0 not `node.index` — a PRE-EXISTING `_lower_getattr`
case-sensitivity bug (`obj_type.lower()` vs original-case `_record_types` keys); sound (type-safe, 2/3 args real) but
worth fixing. REMAINING TAIL: early-return handlers (field_access/subscript/old/forall/exists/in/proj/function_variant
— need the Return_emit_ir return-catch infra, patch saved) + variadic (mktuple/call — need a seq/list-emit_ir-carrying
ctor, a genuinely new capability = biggest/riskiest lift, assess worth).
