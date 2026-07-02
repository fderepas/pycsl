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
| **I3.1** | `Print Assumptions`-style audit of `pycsl-wp-spec.mlw`: the residual is ONLY the enumerated `X_semantics` D2 axioms (no `Admitted`, no new axiom). | residual = the pre-listed D2 set | ◻ TODO |
| **I3.2** | Confirm the recursion-leaf stubs (`_expr_to_whyml`/`_stmts_to_whyml` + the ~10 sibling stubs) are all `\abstract`/`\trusted`-with-sound-`ensures`, each re-sited onto `arm-coverage.md` (no silent hole). | every stub enumerated in `arm-coverage.md` | ◻ TODO |
| **I3.3** | Reconcile the docs: mark `semantic-ceiling-plan.md §12` / `a2-a3-plan.md §7` as the standing boundary; note item 3 is complete-by-stratification. | docs reconciled | ◻ TODO |

**Definition of done (item 3):** the audit confirms the boundary is exactly the enumerated D2
axioms + sound abstract-op laws (`arm-coverage.md` "Emitter-model abstract ops"); no new trust.
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
| **CF6** | `_handle_match_stmt` | match-case tables — broadest. | tbd | ◻ TODO |

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
| Item 3 (recursion-leaf value contracts) | **IRREDUCIBLE** — sound handling = stratified D2 axioms; audit tasks I3.1–I3.3 ◻ TODO |
| Item 4 · CF0 structural setup | ✅ DONE |
| Item 4 · CF1 return | ✅ DONE (proven, byte-diff 0) |
| Item 4 · CF2 if | ✅ DONE (proven, byte-diff 0) |
| Item 4 · CF3 while | ✅ DONE (proven) |
| Item 4 · CF4 for | ✅ DONE (proven, byte-diff 0) — tuple-return gap fixed |
| Item 4 · CF5 try | ✅ DONE (proven, byte-diff 0) — uniform seq-string model (snapshot-at-source) landed the deepest handler (17th) |
| Item 4 · CF6 match | ◻ TODO |

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

**Status:** re-sync reverted to keep the mirror verifying (green tree). The sync-checker
(committed) now makes the drift visible; the verification campaign to complete the re-sync is a
scoped follow-on. Not yet wired as a hard gate.

---

## 6. Definition of done

- **Item 3:** audit I3.1–I3.3 confirm the stratified boundary is intact (no new trust). No
  un-`\trust` deliverable (irreducible).
- **Item 4:** CF0 + CF1–CF6 landed; the control-flow statement family verifies its own bodies
  un-`\trusted` (type-safety + frame); byte-diff 0; suite green. The statement-handler trusted
  base is then empty for BOTH families (reflecting + control-flow) — only the recursion leaves
  (item 3, irreducible) and the enumerated abstract-op laws remain, as designed.
