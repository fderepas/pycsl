# item34.md — tracking plan for the two remaining trust surfaces (items 3 & 4)

**Purpose.** Track progress on the final two trust surfaces after the 12 reflecting-family
statement handlers were un-`\trusted` (PR #148). Companion to `remaining-trust.md` (the
assessment); this file is the executable ledger — mark stages `✅ DONE` inline and keep live
status in §5.

**Doctrine.** [no-more-int] + the small-trusted-core discipline. Item 4 is byte-clean by
construction (every change `@mutable_state`-gated; the 627-corpus has no such class). Item 3 is
*not* a build task — it is a bounded verification that the existing stratification holds.

**Scope split (from `remaining-trust.md`):**
- **Item 3** — value contracts for the recursion leaves `_expr_to_whyml`/`_stmts_to_whyml`.
  **IRREDUCIBLE (Ceiling B, Gödel/Löb).** Not a build task; the only trackable work is auditing
  that the sound stratification (coherence lemmas + audited D2 axioms) is intact and no new
  opaque trust crept in.
- **Item 4** — un-`\trust` the control-flow statement family (`if`/`while`/`for`/`return`/
  `try`/`match`). **A scoped, ceiling-free campaign** — structural setup + ~6 compositional
  handler ports, each a multi-iteration port+prove of the magnitude of one already-landed
  handler.

---

## 1. Item 3 — audit the stratification (NOT a build; irreducible by design)

**Claim under audit.** The 12 handlers prove type-safety + frame; value-faithfulness is
stratified into the audited D2 evaluator axioms via the coherence route
(`src/self-annotate/pycsl-wp-spec.mlw`), NOT eliminable (a system cannot prove its own
evaluator sound). Doing more = a fake axiom = forbidden.

| # | Audit task | Gate | Status |
|---|---|---|---|
| **I3.1** | `Print Assumptions`-style audit of `pycsl-wp-spec.mlw`: the residual is ONLY the enumerated `X_semantics` D2 axioms (no `Admitted`, no new axiom). | residual = the pre-listed D2 set | ✅ **DONE** (2026-07-03) |
| **I3.2** | Confirm the recursion-leaf stubs (`_expr_to_whyml`/`_stmts_to_whyml` + the sibling stubs) are all `\abstract`/`\trusted`-with-sound-`ensures` (no silent hole). | every stub enumerated | ✅ **DONE** (2026-07-03) |
| **I3.3** | Reconcile the docs: mark the standing boundary; note item 3 is complete-by-stratification. | docs reconciled | ✅ **DONE** (2026-07-03) |

**I3.1 findings.** `src/self-annotate/pycsl-wp-spec.mlw` residual = **37 axioms, 0 `Admitted`/`sorry`/
`assume`** (the one text hit is a comment "0 Admitted"). All 37 are the enumerated D2 class: 2
state-model foundation axioms (`update_lookup_same`/`_other`, matching `Phase2_State.v`), ~33
WP-arm `*_semantics` axioms (one per rule arm: assign/skip/aug_assign/array_set/seq/if/while/
return/continue/for/slice/field/expr_stmt), and 2 coherence-bridge axioms (`expr_coherent`,
`eval_e_int` — the D2 core). Several former axioms were PROMOTED to proved `let lemma` (lines 396,
471, 507), shrinking the TCB. No new/stray axiom crept in. `evaluator-axiom-audit.md` enumerates
the set.

**I3.2 findings.** Every `\trusted` sibling/leaf stub in the two mirror files carries a sound `#@
ensures` (predominantly `ensures True` — claims nothing, the soundest boundary); a machine check
for a `\trusted` stub *without* an `ensures` returned EMPTY — **no silent hole**. The recursion
leaves `_expr_to_whyml`/`_stmts_to_whyml` are `\trusted / ensures True`; the full stub list is
recorded in the 2026-07-03 audit (stmt_control_flow.py: `_materialize_bridge`, `_seq_init_expr`,
`_pattern_has_constructor`, `_match_*`, … ; statements.py: `_resolve_dotted_signature`,
`_is_emit_ir_expr`, `_field_label`, cross-mixin `_handle_return_stmt` stub, …).

**I3.3 — standing boundary (reconciled).** `attic/semantic-ceiling-plan.md` (Slice 2, the
`_expr_to_whyml` value contract) and `a2-a3-plan.md §7` record the SAME irreducible floor now
confirmed here: item 3 is **complete-by-stratification** — the residual trust is exactly the
audited D2 axiom set above, and there is **no un-`\trust` deliverable** (a system cannot prove its
own evaluator sound — Gödel-2/Löb). See `remaining-trust.md` (item 3 = Ceiling B).

**Definition of done (item 3): ✅ MET.** The audit confirms the boundary is exactly the 37
enumerated D2 axioms + sound abstract-op laws; 0 `Admitted`; no new trust; no silent stub hole.
There is **no un-`\trust` deliverable** — that is provably unavailable.

---

## 2. Item 4 — the control-flow family campaign

### 2.0 Structural prerequisites (CF0 — do first, gates every handler)

| # | Item | Gate | Status |
|---|---|---|---|
| **CF0.1** ✅ | Make `ControlFlowStmtMixin` (`src/self-annotate/src/module6_whyml/stmt_control_flow.py`) a `@mutable_state @dataclass` so the emit_ir / string-local / seq machinery fires. | class marked; unmarked emission unchanged | ◻ TODO |
| **CF0.2** ✅ | Declare the state it READS: `_has_early_ret: int`, `_func_return_type: str`, `_current_tuple_arity: int` (+ existing `_seq_locals`/`_array_locals`). | fields declared | ◻ TODO |
| **CF0.3** ✅ | Cross-file sibling stubs (`-> str`, `\trusted`): `_materialize_bridge`, `_materialize_str_bridge`, `_maybe_inject_union_return`, `_seq_init_expr`, `_bool_ir_to_int_wrap`, `_stmts_to_whyml`, `_expr_to_whyml`. | stubs typed | ◻ TODO |
| **CF0.4** ✅ | Wire `stmt_control_flow.py` into `bin/run-self-annotation-suite.sh` (a new suite entry). | suite runs it | ◻ TODO |

### 2.1 Per-handler ports (each: port the REAL body → type → prove → un-`\trust` + frame)

Order by tractability (read-only leaf first, broadest last). Each gate: type-checks →
verifies un-`\trusted` → byte-diff 0 (corpus) → suite green.

| # | Handler | Notes (measured) | Frame | Status |
|---|---|---|---|---|
| **CF1 ✅** | `_handle_return_stmt` | 126 lines, **read-only** (`assigns \nothing`); reflects on `val_ir`; seq/array/string/tuple/union returns via materialize bridges + `_seq_init_expr`. The natural FIRST target. | `\nothing` | ◻ TODO |
| **CF2 ✅** | `_handle_if_stmt` | compositional: reflect on `stmt.test`, recurse `_stmts_to_whyml` on both arms. | tbd | ◻ TODO |
| **CF3 ✅** | `_handle_while_stmt` | loop invariants/variants (the SQ5 `0<=idx`/variant discipline reused); recurse. | tbd | ◻ TODO |
| **CF4 ✅** | `_handle_for_stmt` | iterable classification + the for-loop invariant/variant (already added for the emitter for-loops). | tbd | ◻ TODO |
| **CF5 ✅** | `_handle_try_stmt` | the deepest CF handler — LANDED (4th pass). Uniform `seq string` name-collections (snapshot-at-source), map-based sets, string-or, exception-arm tables. Proven; byte-diff 0. | `\nothing` | ✅ DONE |
| **CF6 ✅** | `_handle_match_stmt` | match-case tables — broadest. LANDED via `attic/cf6.md` (additive+gated): `stmts_of` opaque stmt-list vs `args_of` reflected list; subscript-vs-`.get` `pattern` split; IR-mutation no-op; `cases`-gated `List[Dict]`→emit_ir. Proven; byte-diff 0. | `\nothing` | ✅ DONE |

CF0 gates CF1–CF6; CF1 (read-only) is the cheapest end-to-end validation of the CF0 setup.

---

## 3. Critical files

- `src/self-annotate/src/module6_whyml/stmt_control_flow.py` — the mirror: `@mutable_state`
  marker, state-field declarations, sibling stubs, the per-handler real-body ports + un-`\trust`.
- `src/pycsl/module6_whyml/*.py` — expected to need only INCREMENTAL, `@mutable_state`-gated
  recognizer additions (the emit_ir/string/seq infrastructure already exists; a CF handler may
  surface a new leak the same way the statement handlers did).
- `bin/run-self-annotation-suite.sh` — add the `stmt_control_flow.py` entry (CF0.4).
- `src/self-annotate/pycsl-wp-spec.mlw` / `arm-coverage.md` / `evaluator-axiom-audit.md` —
  item 3 audit surfaces.

---

## 4. Out-of-scope / soundness boundary

- **Item 3 stays stratified** — no attempt to un-`\trust` the recursion leaves (Gödel/Löb);
  no fake axiom (`pycsl-how-to-develop §8.4`).
- **Item 4 is type-safety + frame** (like the 12 landed handlers), NOT value-faithful
  `ensures \result == <string>` (that bottoms out at item 3).
- **Corpus untouched** — every CF change `@mutable_state`-gated; byte-diff 0 is the gate.
- **`break`/`continue`/`pass`** are inline in the `_stmts_to_whyml` dispatch, not separate
  handlers — no CF entry (already covered by the statement dispatch).

---

## 5. Progress ledger (live)

| Surface | Status |
|---|---|
| Item 3 (recursion-leaf value contracts) | **IRREDUCIBLE** (Ceiling B) — sound handling = stratified D2 axioms; audit tasks I3.1–I3.3 ✅ DONE (37 axioms / 0 Admitted / no silent stub hole) |
| Item 4 · CF0 structural setup | ✅ DONE |
| Item 4 · CF1 return | ✅ DONE (proven, byte-diff 0) |
| Item 4 · CF2 if | ✅ DONE (proven, byte-diff 0) |
| Item 4 · CF3 while | ✅ DONE (proven) |
| Item 4 · CF4 for | ✅ DONE (proven, byte-diff 0) — tuple-return gap fixed |
| Item 4 · CF5 try | ✅ DONE (proven, byte-diff 0) — uniform seq-string model (snapshot-at-source) landed the deepest handler (17th) |
| Item 4 · CF6 match | ✅ DONE (proven, byte-diff 0) — landed via `attic/cf6.md` (additive+gated pass); 18th & FINAL handler |

**Verification (per CF stage):**
```bash
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/stmt_control_flow.py --import-path src/pycsl --no-proof
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/stmt_control_flow.py --import-path src/pycsl        # proof
PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh /tmp/after && diff -rq <clean-HEAD-baseline> /tmp/after
bash bin/run-self-annotation-suite.sh    # only pre-existing failures (if any) may remain
```

---

## 7. CF5-notes — `_handle_try_stmt`, the deepest handler (THREE exploration passes)

`try` is the single most entangled statement handler — it exercises nearly every collection
construct SIMULTANEOUSLY (array-int stmt-lists, string name-collections, map-based sets, string
ops, comprehensions, nested loops, exception-arm tables). Three passes drove the type error
**195 → 571** (≈92% through the ~120-line body), fixing ~50 distinct constructs. All infra was
verified **regression-free** (`statements.py`, the 12 handlers, stayed green each pass). Model
evolution — each pass corrected the last:

- **Pass 1 — `array int`:** WRONG. The names are strings → `whyml_ident(var)` fails. An int-leak.
- **Pass 2 — `array string`:** right element type, but a REASSIGNED collection (`x = sorted(x)`,
  `x |= …`) is a `ref (array _)` → **Why3 region alias** on the rebind (`illegal alias`).
- **Pass 3 — `seq string`:** CORRECT. A reassigned collection is an immutable, reassignable
  `seq string`; `array string` sources bridge in via `snapshot`.

**The definitive model (pass 3).** Name-collections (`try_assigned`/`body_raised`/`candidates`/
`raw_parts`/`sorted_assigned`) are **`seq string`**. Sources return `array string` and are
`snapshot`-bridged at the binding; ops are seq-typed. The full working brick set:

| construct | lowering |
|---|---|
| `IRScanner.find_*`/`collect_*(<stmts>)` | `val … (l: array int) : array string` (a name-list) |
| `<handler>.get("body", [])` (list default, NON-emit_ir recv) | `array int` stmt-list; GATED off emit_ir recv so `val_ir.get("elts",[])` keeps its int-model path (fixes blocker 1) |
| `<handler>.get("exc_type")` (1-arg, string key, non-emit_ir) | `val …_str (k: string) : string` |
| `x = find_(…)` / seq-source | seq-promote `x` (`_is_seq_src`), bind `ref (snapshot …)` |
| `x \|= find_(…)` | `x := arr_union !x (snapshot <arr>)`, `arr_union (a b: seq string):seq string` |
| `sorted(<seq>)` | `sorted_str (a: seq string) : seq string` (dispatch on `_seq_value_types`) |
| `<str>.split(sep)` | `str_split_op (s sep: string) : array string` (whole-list form) |
| `[a] + [comp]` | `array_concat (a b: seq string) : seq string`; comp → `list_comp_string_filt` |
| `set(<coll>)` | identity (dedup unmodelled) |
| `already_matched \|= seen_local` | `map_union` (map-based sets, distinct from name-lists) |
| `seen_local.add(tag)` | `map_update_some … (str_hash_op tag)` — local-set string keys hashed |
| `h.get("x") or "lit"` | string-`or`: `if not (str_eq_op a "") then a else b` |
| `[tag for tag in <seq>]` | `list_comp_seq`; `_iter_elem_class` binds the loop var `string` |
| `List[str]` return | Module5 captures `return_value_type`; `_build_method_return_type_map` + `_compute_return_type` → `array string` (fixes blocker 3) |
| for-target over a seq/array string | seeded string in the string-collector BEFORE its fixpoint |

**The tangle that makes it a dedicated pass (pass-3 wall).** The `snapshot`-bridging is
CONTEXT-dependent: a `let`-binding (`let x = ref (snapshot v)`) wraps an array source, but a
`:=`-reassign (`x := arr_union …`) needs a seq-returning op directly. Ops (`sorted`, split,
concat, union) appear in BOTH contexts, so `_seq_operand` must pass seq-producing values through
WITHOUT re-`snapshot` (added `_seq_value_producing`). Getting every op's array-vs-seq return and
every use-site's bridge consistent — PLUS the string-collector/seq-promotion ORDERING (a
for-target over `sorted_assigned` needs `_seq_value_types` populated first) — is the remaining
plumbing, on top of the un-reached **exception-arm/code-assembly tail** (past line 571: the
`for h in handlers` connector/`code` construction, ~110 lines).

**Recommendation:** land CF5 as its own dedicated pass starting from this brick table + the
pass-3 `seq string` model. The hard part is not discovery (done) but the seq/array `snapshot`
bridging discipline. `match` (CF6) is comparably broad and untouched.

**UPDATE: CF5 LANDED (4th pass).** The uniform `seq string` model — snapshot-ified at the
SOURCE (`find_`/`collect_`/`.split` emit `(snapshot (op …))`) so the whole flow is seq with no
array/seq mixing (the pass-3 wall) — closed it. Proven; byte-diff 0; the 17th handler.

---

## 7b. CF6-notes — `_handle_match_stmt`: type-checkable, but ARCHITECTURALLY invasive (parked)

A full exploration drove `_handle_match_stmt` (112 lines) from its first type error (~line 195)
through ALL THREE of its branches to a clean-ish type-check — the union-subject branch, the
native constructor branch, and the value-pattern if-chain all lowered. **It is not a Ceiling; it
is reachable.** But — unlike CF1–CF5, which were localized recognizers — match needs changes that
reach ACROSS the whole control-flow handler family and risk regressing the landed handlers.
Parked, tree reverted to the green 17-handler state. What it takes (measured):

**Solved sub-problems (each a real, byte-clean mechanism):**
- **Case-list reflection.** `MatchStmt.cases : List[Dict[str, Any]]` must lower to `array emit_ir`
  so `c["pattern"]`/`c.get("ctor")` project. `List[Dict[…]]`→`emit_ir` — but GATED to the field
  name `cases` (see the wall below).
- **The `"pattern"` key is CONTEXT-DEPENDENT** — `c["pattern"]` (SUBSCRIPT) reads the pattern
  SUB-NODE (`svalue_of`), while `pat.get("pattern")` (`.get`) reads the KIND string (`kind_of`).
  Same key, different type at different nesting — resolved by putting `"pattern"` in BOTH
  `_EMIT_IR_NODE_KEYS` (subscript path) and `_EMIT_IR_STR_KEYS`/`_EMIT_IR_PROJ` (`.get` path),
  which are read by disjoint code paths (`_is_emit_ir_expr` vs `_is_string_expr`).
- **`stmts_of : emit_ir → array int`** — a NEW projection distinct from `args_of : → array emit_ir`.
  A case's `body` is an OPAQUE stmt-list (feeds the int-opaque `_stmts_to_whyml`), NOT a reflected
  node-list. So `c.get("body")`→`stmts_of` (int), `c.get("captures")`→`args_of` (emit_ir). This
  is the key insight: the emitter has TWO list-of-node views — reflected vs opaque.
- **IR MUTATION as a sound no-op.** `c["pattern"] = new_pat` writes to an IMMUTABLE emit_ir value;
  modeled as `()` (the rewrite is unmodeled — sound for type-safety+frame, since `cases` is a
  local `Array.copy` so the frame holds regardless). This dissolves the "match mutates its own
  reflected IR" tension that looked fatal.
- **Latent bug found:** `_is_emit_ir_expr` treated a `List[ExprIR]` field (`stmt.invariants`) as a
  SCALAR emit_ir node (`_irnode_ann_name` matches inside `List[…]`); guard on the field's
  `value_type` (collection marker) to return False. Plus tuple-slot emit_ir typing, tuple-local
  unpack typing, array/string truthiness in `_to_bool`, `<array> or []`, and a 2-pass
  array-elem ↔ emit_ir-local collector fixpoint (mutual dependency `existing_caps`→`pat`→`cases`).

**Why it is PARKED (the architectural wall, not a Ceiling):**
1. **Blast radius.** `List[Dict]`→`emit_ir` is too broad — it also flipped `TryStmt.handlers`
   (`List[Dict]`) to `emit_ir`, breaking CF5's `h.get("exc_type")` string reads. Must be GATED to
   `cases`, but the gate has to fire on the IMPORTED-schema field-collection path (MatchStmt lives
   in `ir_schema.py`), not just the local class-def loop — un-pinned.
2. **The 2-pass collector fixpoint reclassifies siblings.** Running `_collect_array_elem_types`
   twice with the emit_ir pass between changed the try handler's `raw_parts` seq/string typing — a
   regression vector for the already-proven CF5.
3. **Gates unverified.** byte-diff 0 across the 627-corpus is NOT established for `stmts_of` + the
   collector reorder + the projections, and the full PROOF + mirror re-sync are pending.

**Recommendation.** Land CF6 only as a DEDICATED pass that first makes the case-list-reflection +
`stmts_of` model additive-and-gated (a `#@`/emit_ir-only surface with a corpus byte-diff-0 gate
per §8.5 discipline), then re-ports match on top. The union-branch IR-mutation-as-no-op and the
subscript-vs-`.get` `"pattern"` split are the reusable insights; the risk is entirely in keeping
`cases`-reflection from leaking into the other CF handlers' opaque stmt-list model.

---

## 8. Mirror-sync finding (`bin/check-module6-mirror-sync.py`)

**The `module6_whyml` mirror is NOT covered by `check-self-annotate-sync.sh`** (that script
only diffs `Module1–6`/`errors`/`ir_schema` against the rocq/lean mirrors). Added a
method-level checker: every un-`\trusted` mirror method must have a body byte-identical (modulo
`#@` lines / blanks) to the same-named LIVE emitter method; `\trusted` stubs are skipped.

**It immediately exposed real drift** — the load-bearing invariant "verify the mirror ⇒ the
live `_handle_*` is body-faithful" is currently only TRUE for the CF family:

| mirror | un-`\trusted` methods in sync | drifted |
|---|---|---|
| `stmt_control_flow.py` (CF1–CF5) | **5/5 ✅** (verbatim ports of the current live emitter) | 0 |
| `statements.py` (12 reflecting) | 4 | **10 drifted** |

The 10 `statements.py` divergences have two causes:
1. **Typed-IR migration (pre-session, dominant):** the LIVE emitter moved `_expr_to_whyml` to
   take a typed `ExprIR` (`self._expr_to_whyml(stmt.value, …)`), but the mirror still passes
   the pre-migration `stmt.value.to_dict()`. So the mirror reflects an OLDER emitter — verifying
   it did NOT establish body-faithfulness of the CURRENT emitter for these handlers.
2. **This session (3):** the CF4/CF5 tool changes to the LIVE `_handle_tuple_unpack_stmt`
   (CF4), `_handle_augassign_stmt` (CF5 union), `_handle_expr_stmt` (CF5 str-key hash) were not
   back-ported to the mirror.

**Consequence:** the "12 reflecting handlers are body-faithful" claim is weaker than stated —
they verify a STALE mirror. The CF-family claim (5 handlers) is solid (verbatim, machine-checked
in sync).

**Re-sync attempt (findings).** Re-porting the 10 live handler bodies into the mirror is:
- **CODE-trivial:** a body-swap + 4 field declarations (`_current_self_type`, `_heap_var`,
  `_todict_aliases`, `_getattr_self_dict_aliases`) + 3 sibling stubs
  (`_call_returns_string_collection`, `_resolve_dotted_signature`, `_str_operand_to_int`) makes
  the mirror a verbatim copy — **the sync-checker then passes (all 19 methods)**.
- **VERIFICATION is a campaign:** the CURRENT emitter reflects on emit_ir features the mirror's
  emit_ir ADT does not model — notably `val_ir.get("args")` (the args LIST; the ADT carries only
  `arg0_of`/`nargs_of`, not an `array emit_ir`). Making the re-synced bodies type-check/prove
  needs the emit_ir ADT extended (an `args_of` list projection + `not <array>` / `X or […]`
  handling) plus per-handler recognizers — a moderate campaign, cascading like the CF work.
- **A real emitter bug was found + fixed** en route: `_call_named_builtins` re-lowered its
  already-lowered `args` (crash on `<computed>.endswith(…)`), committed byte-diff 0.

**Status: RESOLVED (`attic/resync-campaign.md` executed).** All 10 drifted `statements.py` handlers
re-ported verbatim from the live emitter (checker green: 19/19); they type-check AND PROVE;
byte-diff 0; the checker is wired into `check-self-annotate-sync.sh`. The `args_of` emit_ir
projection + a handful of `@mutable_state` recognizers closed the verification. All 17 body-
faithful handlers (12 reflecting + 5 CF) now verify the CURRENT emitter — the integrity gap is
closed and gated against future drift.

---

## 6. Definition of done

- **Item 3:** audit I3.1–I3.3 confirm the stratified boundary is intact (no new trust). No
  un-`\trust` deliverable (irreducible).
- **Item 4:** CF0 + CF1–CF6 landed; the control-flow statement family verifies its own bodies
  un-`\trusted` (type-safety + frame); byte-diff 0; suite green. The statement-handler trusted
  base is then empty for BOTH families (reflecting + control-flow) — only the recursion leaves
  (item 3, irreducible) and the enumerated abstract-op laws remain, as designed.
