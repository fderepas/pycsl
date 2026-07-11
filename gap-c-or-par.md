# gap-c-or-par.md — the `_field_type_of` 3-recognizer all-or-nothing build

*Self-contained build plan, 2026-07-10. Converts the mirror leaf `_field_type_of`
(`src/self-annotate/src/module6_whyml/types.py`, `TypeInferenceMixin`) from `\trusted` to a verified
body, unlocking a −1 that ALSO retroactively de-int-hashes two already-converted methods. Successor to
`m2-reader-emitter-build.md`; discipline carried forward: spike-gated recognizers, measured acceptance
only, ledger fixed at 3, byte-diff-0 corpus gates, VALUE-not-count. Scoped from this session's
port+`--fun` measurement (`getting-better/post-m1-census.md`, "_field_type_of measured").*

## Why this build (the leverage)

`_field_type_of` is the LEAF that the already-verified `_rhs_yields_array` and `_rhs_yields_map` CALL
(`self._field_type_of(val_ir) in ("set","dict","frozenset")`). Because `_field_type_of` is trusted, those
callers' Attribute/FieldGet branches currently lower `_field_type_of`'s result to an **int-hash** compare
(`self__field_type_of_1 val_ir = 1555321514 || …`) — a faithfulness residual. Converting `_field_type_of`
to a body typed `(attr_ir:"ExprIR") -> Optional[str]` (returns `option string`) makes those caller branches
route through `str_eq_op` on a real `option string` — **one −1 that makes THREE methods faithful**.

## The measured blocker chain (port `_field_type_of` verbatim on the scaffold, `--fun` stops at each)

`_field_type_of` is a 60-line ExprIR reader. Its body needs, IN ORDER (each is the FIRST `--fun` blocker
once the prior is built):

### R1 — Gap-C `or-{}` node-projection chain  (FIRST blocker, `types.mlw:449`)
`receiver = attr_ir.get("value") or attr_ir.get("object") or {}` — the "first present sub-node, else empty"
idiom. `attr_ir.get("value")` → `svalue_of`, `.get("object")` → `object_of` (both `emit_ir`, sentinel
`IrOther ""` for the absent key); `or {}` → the empty-node sentinel. Currently lowers to int-boolean
nonsense (`if true||true then 1 else 0 || (const (None: option int))`). BUILD: recognize
`<emit_ir>.get(K1) or <emit_ir>.get(K2) or {}` (K1,K2 ∈ node-keys value/object/…; terminal `{}` = empty
DictLit) → a first-non-sentinel `emit_ir` selector:
`(let _r = svalue_of attr_ir in if is_ir_other _r && name_of _r = "" then object_of attr_ir else _r)`
(or a `match`; the `{}` fallback is `IrOther ""`). The result is `emit_ir`, so the downstream
`receiver.get("type") == "Var"` → `kind_of`, `receiver.get("name")` → `name_of`. Site: the BoolOp/`or`
value-emission path (`expressions.py`; the `or`-chain currently routes through the string/int-bool lowering,
NOT `_EMIT_IR_PROJ`). **REUSABLE** — the `x.get(a) or x.get(b) or {}` idiom recurs across the node-reader
family (also in `_is_string_expr`, `_field_type_for`). Gate on emit_ir receiver → corpus-inert (no corpus
emit_ir does this).

### R2 — nested-dict over `self._record_types`  (SECOND blocker)
`_record_types` is `Dict[str, <record-info-dict>]` where each value is a heterogeneous dict with
`whyml_name: str`, `field_types: Dict[str,str]`, `fields`, …. The body does:
- `gcls in self._record_types` — dict-key membership;
- `self._record_types[gcls].get("whyml_name")` — subscript-then-`.get` (→ `string`);
- `for info in self._record_types.values(): if info.get("whyml_name") == cls: return
  info.get("field_types", {}).get(field_name)` — `.values()` iteration + nested `.get("field_types",{}).get`
  (→ `option string`).
BUILD: a closed-key **TypedDict-view for the `_record_types` VALUE** (`RecordInfoView` with
`whyml_name: str`, `field_types: Dict[str,str]`), so `_record_types` types as
`map string (option recordinfoview)` — the composition-wall TypedDict-monomorphization applied to a nested
dict value. Then `[gcls]`/`.get("whyml_name")` project the record field, and
`info.get("field_types",{}).get(field)` reads the inner `map string (option string)`. The `.values()`
iteration returning a match on `option string` is the return path. HARD PART: modeling the heterogeneous
value dict as a record (only the fields `_field_type_of` reads — `whyml_name`, `field_types` — need to be in
the view; the rest stay unmodelled).

### R3 — getattr-self-field-`{}`-`.get`  (THIRD blocker)
`getattr(self, "_module_global_classes", {}).get(receiver_name)`, and the same for
`_current_record_var_classes` and `_record_param_classes` — `getattr(self,"<dict-field>",{}).get(k)` on a
`Dict[str,str]` self-field → `map string (option string)` read (the `{}` default, then `.get`). Distinct
from R1's None-default (`getattr(...,None)`): here the default is `{}` and it is immediately `.get`-ed.
BUILD: recognize `getattr(self,"<declared-dict-field>",{}).get(k)` → `Map.get self.<field> k`. Declare the
three fields (`_module_global_classes`, `_current_record_var_classes`, `_record_param_classes`) as
`Dict[str,str]` in the mirror scaffold (they are already partly declared; add `_record_param_classes`).
Likely the smallest of the three (the getattr-self-field-`.get` machinery from the M2 work is close).

## Build order & the all-or-nothing rule

`R1 → R2 → R3 → convert `_field_type_of` + COMMIT once`. Build in ONE working tree; **nothing lands until
`_field_type_of` converts** (each recognizer alone converts nothing → a facade; no-unused-facade). After
each recognizer, re-`--fun typeinferencemixin___field_type_of` and confirm the blocker ADVANCES to the next
(R1→ nested-dict blocker, R2→ getattr blocker, R3→ SUCCESS). If a recognizer needs more than its named site
(e.g. R2's nested-dict needs an eliminator the meta-theory doesn't cover), STOP and re-scope — do not sprawl.

## Gates (at the single conversion commit)

- **fidelity** — `self-annotate-mirror-check.sh` 52/52; sync no new divergence.
- **`--fun` `typeinferencemixin___field_type_of` SUCCESS** + **whole-file proof of `types.py` SUCCESS**
  (§10.10 — the sibling-interaction check; also re-confirms the 5 verified TypeInferenceMixin methods +
  `_split_tuple_type` stay green).
- **byte-diff 0** — R1/R2/R3 fire only on emit_ir receivers / declared self-dict-fields (all mirror-only);
  the live-emitter changes are recognizer additions gated NOT to touch corpus emission. Authoritative
  worktree sweep (767 files) REQUIRED — recognizer builds are the corpus-perturbation risk (cf. the M2
  sprawl that perturbed 0887). If any corpus program changes, the gate is a sanctioned-review ONLY if the
  change is provably semantics-preserving; otherwise REVERT.
- **ledger 3** — recognizers are lowerings, no new `axiom`/cert; `Print Assumptions`/`#print axioms`
  unchanged. No TypedDict-view introduces a new WhyML value shape needing a certificate beyond the existing
  record-value certificate (`Phase2b_RecordVal`) — CONFIRM (R2's `RecordInfoView` is a record over
  certified fields string/map, covered by construction; if it needs a `pyval → record` eliminator not
  covered, that is a coupling-rule obligation — flag it).
- **non-vacuity** — the emitted `_field_type_of` reads real `kind_of`/`name_of`/`svalue_of`/`object_of` +
  `Map.get self._record_types` + the `field_types` inner map (no opaque `_get_N <hash>`).
- **count** 1226 → 1225. **The retroactive win:** after landing, re-emit `_rhs_yields_array`/`_rhs_yields_map`
  and CONFIRM their Attribute branches now use `str_eq_op` on the `option string` result (int-hash residual
  GONE) — re-prove both (must stay SUCCESS). Document the faithfulness upgrade in the commit.

## Reference corpus (per the new-feature discipline)

Add driver fixtures to `test-suite/corpus/pycsl-reference/` exercising each recognizer in isolation
(byte-diff-gated, mirror-independent):
- `NNNN.py` — R1: an emit_ir node reader that does `x.get("value") or x.get("object") or {}` then reads
  `.get("type")`/`.get("name")` on the result (positive: proves; a `assigns \nothing` twin).
- `NNNN.py` — R2: a `Dict[str, <TypedDict>]` field read `d[k].field` + `d.values()` iteration + inner
  `.get(f)` (the RecordInfoView shape) proving a string result.
- `NNNN.py` — R3: `getattr(self,"<dict-field>",{}).get(k)` on a declared `Dict[str,str]` field → option
  string. Each fixture is the executable spec of one recognizer; they gate regressions independently of
  `_field_type_of`.

## Risks & non-goals

- **R2 is the make-or-break** — the heterogeneous `_record_types` value dict. Mitigate: model ONLY the two
  fields read (`whyml_name`, `field_types`), the rest unmodelled; if the `.values()` eliminator over
  `map string (option record)` isn't meta-theory-covered, that is a genuine wall — measure with a hand
  `.mlw` spike BEFORE the emitter build (S-R2 spike).
- **No `@mutable_state` regression** — `TypeInferenceMixin` is already `@mutable_state` (from the M2 build);
  `_split_tuple_type` is already repaired. No new scaffold flip.
- **Facade discipline** — do NOT commit R1 or R2 or R3 alone. One commit at the conversion, or revert.
- **Corpus perturbation is THE risk** — recognizer builds touch the live emitter; the authoritative
  byte-diff sweep is non-negotiable, and any non-inert change is REVERTED (not rationalized).
- **Non-goal:** the OTHER `_record_types`-reader (`_field_type_for`) and the string-`or`-chain / A3/A4/U
  cluster (`_call_return_whyml_type`) are separate builds; R1/R2/R3 are REUSABLE toward them but not in scope
  here.

## Order & first action

`S-R2 spike (hand .mlw: does the RecordInfoView nested-dict + .values() eliminator type-check + discharge,
ledger 3?) → R1 → R2 → R3 → convert + single commit → retroactive de-int-hash re-proof of the 2 callers`.
First action: the **S-R2 spike** (make-or-break, cheapest to falsify), then R1 (reusable, easiest).
