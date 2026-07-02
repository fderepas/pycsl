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
| **CF5** | `_handle_try_stmt` | exception arms / handler tables — broad. **Explored** (error 195→573): correct model is **`array string`** name-collections (var/exception names + tags are STRINGS). Bricks mapped: `IRScanner.find_*`/`collect_*` → `array string`; `arr_union`/`array_concat` over `array string`; `sorted`/`set(…)` over the collection; `<node>.get("body", [])` (list-literal default) → `array string`; `_callee_raised_*` stubs → `List[str]`. **Lesson:** an intermediate `array int` model is ITSELF an int-leak — `for var in sorted(...): whyml_ident(var)` needs a `string` element. Reverted (not landed) to avoid banking the int-leak; needs `_array_elem_types` string propagation from the call return type. | `\nothing` | ◻ TODO (array-string) |
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
| Item 4 · CF5 try | ◻ TODO (array-string) — explored; model = `array string` name-collections; int-leak reverted |
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

## 6. Definition of done

- **Item 3:** audit I3.1–I3.3 confirm the stratified boundary is intact (no new trust). No
  un-`\trust` deliverable (irreducible).
- **Item 4:** CF0 + CF1–CF6 landed; the control-flow statement family verifies its own bodies
  un-`\trusted` (type-safety + frame); byte-diff 0; suite green. The statement-handler trusted
  base is then empty for BOTH families (reflecting + control-flow) — only the recursion leaves
  (item 3, irreducible) and the enumerated abstract-op laws remain, as designed.
