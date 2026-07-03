# cf6.md — land `_handle_match_stmt` as an additive, gated self-annotation pass

**Purpose.** Un-`\trust` the LAST control-flow statement handler, `_handle_match_stmt`, so the
self-annotation mirror verifies its real body (type-safety + a checked `assigns \nothing` frame).
This is the 18th (final) body-faithful handler in item 4 (`item34.md`).

**Context / verdict (from the `item34.md §7b` exploration).** match is **type-checkable — NOT a
Ceiling.** A prior all-at-once attempt drove all three branches (union-subject, native
constructor, value-pattern) to a clean type-check, but did it with changes that regressed
siblings and left byte-diff unverified. The two failure modes were both *blast radius*, not
*impossibility*:
1. `List[Dict[str, Any]]`→`emit_ir` was applied globally, so `TryStmt.handlers` (also
   `List[Dict]`) flipped to `emit_ir` and broke CF5's `h.get("exc_type")` string reads.
2. The gate that would have fixed (1) was placed on the wrong field-collection path — MatchStmt
   is an IMPORTED `@dataclass` (`ir_schema.py`), whose fields are built in
   `_collect_class_fields` **line 2138**, not the local class-def loop (line 1835).

**This pass fixes both** by making every mechanism **additive** (new emit_ir-reflection surface,
absent from the 627-corpus) and **gated byte-diff 0** BEFORE porting match — and by gating the
case-reflection to the field NAMED `cases` on the `@dataclass` path (2138). Once handlers stay
int-opaque, the CF5 regression cannot recur.

**Feature vs refactor.** FEATURE (adds emit_ir reflection surface) that MUST NOT change corpus
emission: the surface fires only in `@mutable_state` / emit_ir-reflection contexts, which the
627-corpus has none of. **byte-diff 0 is the gate on every stage.**

**Doctrine.** [no-more-int] + small-trusted-core + §8.5 gate battery. Type-safety + frame ONLY
(NOT value-faithful `ensures \result == <string>` — that is item 3, Ceiling B). The union-branch
IR mutation (`c["pattern"] = new_pat`) is a **sound no-op** (the reflected IR is immutable; the
rewrite is unmodelled; `cases` is a local `Array.copy` so the frame holds regardless).

---

## 0. The model (representation decision — no new SMT theory)

match reflects on a case-list. The emitter has TWO list-of-node views, and the whole pass hinges
on keeping them distinct:

| surface | WhyML | projection | meaning |
|---|---|---|---|
| `c.get("captures")`, `.get("args")` | `array emit_ir` | `args_of` | a REFLECTED node list |
| `c.get("body")` | `array int` | **`stmts_of`** (NEW) | an OPAQUE stmt-list → feeds `_stmts_to_whyml` |
| `c["pattern"]` (subscript) | `emit_ir` | `svalue_of` | the pattern SUB-NODE |
| `c.get("pattern")` (`.get`) | `string` | `kind_of` | the pattern KIND |
| `c.get("ctor")` | `string` | `name_of` | the constructor NAME |
| `c.get("guard")` | `emit_ir` | `svalue_of` | the guard node |

The `"pattern"` key is **context-dependent** (subscript→node, `.get`→kind); it lives in BOTH
`_EMIT_IR_NODE_KEYS` and `_EMIT_IR_STR_KEYS`, read by disjoint code paths (`_is_emit_ir_expr` vs
`_is_string_expr`). All new `val`s are OPAQUE (`stmts_of : emit_ir → array int`, no content law)
— sound under-approximations for type-safety, no SMT-feasibility spike needed (Gate B: N/A, no
recursive/algebraic theory).

---

## 1. Stages (each: apply → type-check → **byte-diff 0** → next)

### M1 — additive emit_ir-reflection surface (byte-diff 0 per sub-stage)

- **M1.1 `stmts_of` projection.** Add `val stmts_of (e: emit_ir) : array int` to the emit_ir
  theory (`preamble.py::_emit_exprir_theory`, near `args_of`). Add to `_EMIT_IR_PROJ`
  (expressions.py): `"pattern": "kind_of"`, `"ctor": "name_of"`, `"captures": "args_of"`,
  `"body": "stmts_of"`, `"guard": "svalue_of"`; `"pattern"`/`"ctor"` → `_EMIT_IR_STR_KEYS`;
  `"pattern"`/`"guard"` → `_EMIT_IR_NODE_KEYS`. **Gate:** corpus byte-diff 0 (no emit_ir reflection).
- **M1.2 `cases`-gated case reflection.** In `_collect_class_fields` **line 2138** (the
  `@dataclass` path) AND the local class-def loop (line 1835): if the field is named `cases` and
  annotated `List[Dict[...]]`, set `value_type = "emit_ir"`. Do NOT touch
  `_m5_get_list_elem_type` (keeps `List[Dict]` params/other fields int-opaque — the CF5-safe
  choice). **Gate:** corpus byte-diff 0 (no `cases: List[Dict]` corpus record); `MatchStmt.cases`
  is `array emit_ir` in the mirror mlw.
- **M1.3 subscript `"pattern"` → node.** `_handle_subscript` §26: `<emit_ir>["pattern"]` →
  `svalue_of` (not the shared `kind_of`). `_is_string_expr` subscript case: EXCLUDE keys in
  `_EMIT_IR_NODE_KEYS` (so `c["pattern"]` is not mis-typed string). **Gate:** byte-diff 0.
- **M1.4 IR-mutation no-op.** `_handle_array_set_stmt`: `<emit_ir>[k] = v` → `()` in
  `@mutable_state`. **Gate:** byte-diff 0.
- **M1.5 latent List-field bug.** `_is_emit_ir_expr` Attribute case: a field carrying a
  `value_type` (collection) is NOT a scalar node → return False (fixes `_irnode_ann_name`
  mis-tagging `List[ExprIR]` as scalar `ExprIR`). **Gate:** byte-diff 0; CF1–CF5 still type-check.
- **M1.6 truthiness + tuple + array-or helpers.** `_to_bool`: emit_ir-array → `Array.length … <> 0`,
  string → `not (str_eq_op … "")`. `_handle_binop`: `<array> or []` → left. `_infer_tuple_slot_type`:
  emit_ir slot. `_collect_tuple_var_assigns`: `self.<m>()` key resolution + slot-type recording.
  Tuple-local unpack typing (string/emit_ir targets) in the string + emit_ir collectors.
  Array-var collector: `<emit_ir>.get("captures"/"args"/"body")` (direct Call AND `… or []`) →
  array local. `_val_elem_ty`: `.get("captures"/"args")` → emit_ir element. **Gate:** byte-diff 0.

### M2 — collector fixpoint, regression-safe

The mutual dependency `existing_caps`→`pat`→`cases` needs array-elem classification AFTER emit_ir
locals AND vice-versa. Run `_collect_array_elem_types` → `_collect_emit_ir_result_locals` →
`_collect_array_elem_types` (2-pass). **Because M1.2 gates handlers OUT of emit_ir, no non-match
local reclassifies** — but VERIFY: the gate is *CF1–CF5 still type-check AND prove unchanged*
(the try-handler `raw_parts` seq/string typing is the canary).

### M3 — port match + un-`\trust`

Port the real `_handle_match_stmt` body verbatim into the mirror
(`stmt_control_flow.py`), remove the `\trusted` stub, add `#@ requires True / ensures True /
assigns \nothing`, and the pattern-helper sibling stubs (`_pattern_has_constructor`,
`_render_match_pattern`, `_match_pattern_cond`, `_match_subject_union_info`,
`_union_ctor_for_arm_tag` — the last two return plain `(str, ExprIR)` tuples). **Gate:**
`stmt_control_flow.py --no-proof` → Verification SUCCESS (18/18 handlers type-check);
`check-self-annotate-mirror-sync.py` green (match body verbatim).

### M4 — prove + gates

**Gate battery:** (1) `stmt_control_flow.py` full PROOF green; (2) **byte-diff 0** across the
627-corpus for ALL emitter changes; (3) both mirror-sync gates green; (4) reference corpus
witness added + verifies (§3); (5) `run-self-annotation-suite.sh` — no new failures.

---

## 2. Critical files

- `src/pycsl/module6_whyml/preamble.py::_emit_exprir_theory` — `stmts_of` decl (M1.1).
- `src/pycsl/module6_whyml/expressions.py` — `_EMIT_IR_PROJ`/`_STR_KEYS`/`_NODE_KEYS` (M1.1),
  `_handle_subscript` §26 pattern-node (M1.3), `_is_string_expr` subscript exclusion (M1.3),
  `_is_emit_ir_expr` value_type guard + `.get`/subscript node keys (M1.5), `_to_bool` (M1.6),
  `_handle_binop` `<array> or []` (M1.6).
- `src/pycsl/frontend/Module5_IREmitter.py` — `_collect_class_fields` line 2138 + line 1835
  `cases`-gate (M1.2).
- `src/pycsl/module6_whyml/statements.py` — `_handle_array_set_stmt` mutation no-op (M1.4),
  `_val_elem_ty`/`_collect_str_call_result_locals`/`_collect_emit_ir_result_locals` tuple-local
  + captures (M1.6), the 2-pass collector fixpoint (M2).
- `src/pycsl/module6_whyml/types.py` — `_collect_tuple_var_assigns` self-resolution + slot types,
  `_collect_array_var_assigns` `.get("captures"/"args"/"body")` (M1.6).
- `src/pycsl/module6_whyml/functions.py` — `_infer_tuple_slot_type` emit_ir slot (M1.6).
- `src/self-annotate/src/module6_whyml/stmt_control_flow.py` — the mirror match port (M3).

---

## 3. Driver / regression guard — the MIRROR (not a standalone corpus witness)

**Measured finding (an attempted corpus witness proved it):** the match-reflection surface is
INTRINSICALLY self-annotation-internal — it cannot be exercised by a standalone corpus program:
- an emit_ir value only arises from an `ExprIR`/`StmtIR`-typed access, which requires `ExprIR`
  to be RESOLVABLE via `--import-path <ir_schema>`; a standalone program has no such import, so a
  `case: "ExprIR"` param/field collapses to opaque `int` (verified: `describe (case: int)`);
- the `MatchStmt.cases : List[Dict]`→`array emit_ir` field reflection (M1.2) needs the
  imported-`@dataclass` field path (a LOCAL `@dataclass` field drops its `value_type`);
- the IR-mutation no-op (M1.4) needs `c` to be an array-emit_ir ELEMENT — same import dependency.

So the demand-driver + regression guard is **the mirror handler itself**,
`src/self-annotate/src/module6_whyml/stmt_control_flow.py::_handle_match_stmt`, verified WITH
`--import-path src/pycsl` in `bin/run-self-annotation-suite.sh`. It fails without the surface
(the parked exploration is the FAIL-first evidence) and passes with it (M3). The 627-corpus
byte-diff-0 gate is what proves the surface is additive (absent everywhere else). This is the
correct analogue of the reference-corpus convention for a self-annotation-internal feature: the
mirror IS the corpus.

---

## 4. Out-of-scope / soundness boundary

- **Corpus untouched** — every change `@mutable_state`/emit_ir-reflection/`cases`-field-gated;
  byte-diff 0 is the gate.
- **`stmts_of` is opaque** (`array int`, no length/content law) — TYPE-safety of the opaque
  stmt-list, not a value claim.
- **IR mutation is an unmodelled no-op** — sound for type-safety+frame; NOT a faithful rewrite.
- **Type-safety + frame only** — `assigns \nothing` (the handler builds a local string + a local
  `cases` copy); NOT value-faithful (item 3, Ceiling B).

---

## 5. Verification (exact commands)

```bash
# per M1 sub-stage: type-check + byte-diff 0
PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/stmt_control_flow.py --import-path src/pycsl --no-proof
git worktree add /tmp/cf6_base df55a984 2>/dev/null
PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh /tmp/cf6_after && diff -rq /tmp/cf6_base_out /tmp/cf6_after
# M4: full proof + mirror sync + suite
PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/stmt_control_flow.py --import-path src/pycsl
bash bin/check-self-annotate-sync.sh && bash bin/self-annotate-mirror-check.sh
bash bin/run-self-annotation-suite.sh
```

---

## 6. Progress ledger (live)

| Stage | Status |
|---|---|
| M1.1 `stmts_of` + projection tables | ✅ DONE (byte-diff 0) |
| M1.2 `cases`-gated reflection (dataclass path 2138) | ✅ DONE (byte-diff 0) |
| M1.3 subscript `"pattern"` node / string-exclusion | ✅ DONE (byte-diff 0) |
| M1.4 IR-mutation no-op | ✅ DONE (byte-diff 0) |
| M1.5 `_is_emit_ir_expr` List-field guard | ✅ DONE (byte-diff 0) |
| M1.6 truthiness + tuple + array-or + collectors | ✅ DONE (byte-diff 0) |
| M2 collector fixpoint (regression-safe) | ✅ DONE (byte-diff 0) |
| M3 port match + un-`\trust` | ✅ DONE (byte-diff 0) |
| M4 prove + byte-diff 0 + mirror sync | ✅ DONE — stmt_control_flow.py + statements.py both PROVE; byte-diff 0 (627); mirror-sync 24/24; driver = mirror (§3) |
