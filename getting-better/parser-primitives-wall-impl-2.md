# parser-primitives-wall-impl-2.md — round 2: the localized emitter feature BUILT + mirror boundary

Round 1 (`parser-primitives-wall-impl.md` §GATE-S) REFUTED at ONE localized emitter gap:
`Module5_IREmitter._field_type_from_annotation[_inst]` maps a `List[X]` CLASS FIELD → the
coarse `"list"` tag → `array int`, DISCARDING `X`. A `List[Tok]` PARAM worked
(`a: array tok`, `a[i].type` L3-tc ✓); the SAME `List[Tok]` as a class field collapsed to
`array int`, so `cur (-> Tok)` returned int → L3-tc ✗. Round 2 built that field-typer.

## Gate S (record-element class-field emission) — **PASS**

Probe: `@dataclass Tok(py_type,string,start,end)` + `@mutable_state class Parser` with
`self.toks: List[Tok]`, `self.i: int`, class invariants `0 <= self.i`,
`self.i < \length(self.toks)`, `\length(self.toks) >= 1`, and `cur(self)->Tok:
return self.toks[self.i]`.

- BEFORE: `type parser = { mutable toks: array int; ... }`; `self.toks[self.i]: int`
  vs expected `tok` → **L3-tc ✗**.
- AFTER: `type parser = { mutable toks: array tok; mutable i: int }`;
  `by { toks = (Array.make 1 { py_type = 0; string = ""; start = 0; py_end = 0 }); i = 0 }`;
  `parser__cur (self: parser) : tok` reads `self.toks[self.i]` → **L3-tc ✓**; full proof
  **all VCs Valid** incl. *"index in array bounds of goal parser__cur'vc: Valid"* (the OOB
  discharges via the class invariant).

Also confirmed: `\length(self.toks)` (ACSL op → `ArrayLen` IR) lowers to `Array.length toks`
in the invariant (a self-field array); `len(self.toks)` does NOT (→ unbound `iter_length`) —
use `\length`, not `len`, on a self array field in a class invariant.

### Feature (committed 614fd814) — 3 touch points, all @mutable_state/IR-node gated
- **M5** `_field_type_from_annotation_inst` __init__ AnnAssign path: a `List[<record>]` field
  carries the element record name as `value_type` (reusing `_m5_get_list_record_elem`; the
  element record is pinned PURE via the existing `list_element_record_types` AST-walk).
- **M6** `_emit_type_decls` list branch: `value_type in _record_types` → `array <whyml_rec>`.
- **auto_trust** `_build_witness_str` + new `_record_default_literal`: an `array <record>`
  `by`-witness is `Array.make N { field = <zero>; ... }` (record literal, not int `0`).

### Gates (all green)
- Corpus **byte-diff 0** (767 files, `bin/byte-diff-sweep.sh` vs baseline) — feature is inert
  where absent (record-element field + @mutable_state, corpus-absent).
- **Ledger 3** — record + array + concrete-int; NO axiom, NO abstract val (allowlist untouched).
- **Mutation test** — `List[Tok]`→`List[int]` flips the field `array tok`→`array int` (real,
  not facade); the param projection `elem_type` emits the faithful
  `(let _rec_ = toks[i] in _rec_.py_type)` with `ensures result = ...py_type` **Valid**.
- Fixture `test-suite/corpus/pycsl-reference/0925_list_record_field.py` proves end-to-end.

## Mirror primitive conversion (`src/self-annotate/src/frontend/pure_ast.py`) — **CERTIFIED-BOUNDARY**

Converting even the cleanest primitive (`cur = return self.toks[self.i]`) requires the mirror
`_Parser` to be a RECORD with an `array _tok` field, which requires `@mutable_state` on
`_Parser`. Measured blast radius of that single decorator on the all-trusted mirror:

- **+283 mlw lines (1033 → 1316)** — `@mutable_state` flips the global gate that ALSO emits the
  entire `emit_ir` ADT theory (currently absent from the mirror) AND triggers file-wide record-
  field-name qualification (`_reserved_exprir_symbols`). That is a session-scale rewrite of a
  262-stub, runtime-imported shared mirror file — exactly the "do NOT grind" case Gate S names.
- Independently, the field-PROJECTING primitives (`at_op`/`at_name`/`at_kw`/`accept_op`/
  `expect_op`/`accept_kw`/`expect_kw`) wall on `*vals` **varargs-membership** (`t.string in vals`
  over a runtime tuple param, not a literal disjunction), and `self.toks[self.i].py_type` (self-
  field-array-read projection) lowers via an opaque `get_py_type` facade, not the `_rec_`
  projector. So the payoff is capped at `cur`/`peek`/`advance` even if the retrofit were done.

**Verdict:** the localized emitter feature (the make-or-break) is BUILT, proven, byte-inert, and
banked. The mirror integration is deferred behind two capabilities: (1) a low-blast-radius
record-element field gate that does not require the full `@mutable_state` theory emission, and
(2) varargs-membership lowering (`x in *vals`) + self-field-array-read projection. Count
unchanged (mirror untouched); the feature + fixture 0925 are the increment.
