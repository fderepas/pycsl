# parser-primitives-wall-impl.md — implementation plan (spike-first; emission-refutation exit)

Synthesized from `parser-primitives-wall.md` + `-response.md` (Gate R **CONFIRM**, one mandatory emitter condition).
MODELING proven (fable `parser-oracle.mlw`: tok record + seq _tok + Seq.get all Valid, Seq.get total ⇒ NO OOB VC
under `requires True`, ledger-neutral). The impl make-or-break is the EMISSION. These are CONVERSIONS (count DOWN).

## The certified shape (emit this)
- `_Tok` RECORD: `{ tok_type: int; tok_string: string; tok_start: int; tok_end: int }` (reuse PyCSL's record
  machinery — the live `_Tok.__slots__ = ("type","string","start","end")`; `.type`→int, `.string`→string).
- `Parser` STATEFUL record: `mutable toks: seq _tok` self-field + `mutable i: int` self-field (the @mutable_state /
  K1-seq-field / stateful-record precedent). `self.toks[j]` → `Seq.get toks j` (TOTAL — no OOB VC); `self.i += 1` →
  `i := i+1`; `len(self.toks)` → `Seq.length toks`.
- **MANDATORY (fable rule):** token kinds lower to CONCRETE int literals — `_tokenize.OP`→55, `_tokenize.NAME`→1,
  `_tokenize.NUMBER`→2, `_tokenize.STRING`→3 (from `import tokenize; tokenize.OP` etc.). NOT abstract `val`s (else
  `at_op_false` discrimination needs a distinctness axiom → ledger off 3). `t.string in vals` → `str_eq_op` disjunction.
- Reuse record + seq.Seq + str_eq_op — NO new axiom (ledger 3).

## Gate S — EMISSION make-or-break SPIKE FIRST (refutation exit)
1. Re-prove `why3 prove -P z3 getting-better/parser-oracle.mlw` → reproduce Valid + ledger-neutral.
2. Emit the _Tok record + the Parser toks/i self-fields + port ONE primitive (`cur` = `Seq.get toks i`, and `at_op`
   = `tok_type (Seq.get toks i) = 55 && str_eq_op (tok_string …) …`), token kinds as concrete ints. `pycsl
   pure_ast.py --keep-mlw`. Does `self.toks[self.i]` lower to `Seq.get toks i` (NOT int-array/opaque), `t.type`/
   `t.string` to record projectors (NOT opaque getters/int-hash), `_tokenize.OP` to `55` (NOT an abstract val), and
   TYPECHECK (L3-tc ✓) with NO OOB VC?
   - PASS → build + convert the cluster.
   - REFUTE (the seq _tok self-field won't emit / `_tokenize.OP` can't lower to a concrete int / Seq.get forces an
     OOB VC / the stateful Parser record won't retrofit) → REVERT ALL, record CERTIFIED-BOUNDARY (§GATE-S) with the
     exact Why3/emit error. Do NOT grind.

## Build (only if Gate S PASSES) — convert the primitive cluster (count DOWN)
Model the _Tok record + Parser toks/i self-fields + token-kind concrete-int lowering, then convert the CLEAN
primitives VERBATIM (each a real conversion, count strictly down): `cur`, `peek`, `advance`, `at_op`, `at_name`,
`accept_op`, `expect_op` (~7 clean). Then `at_kw`/`accept_kw`/`expect_kw` (use `_keyword.kwlist` — a ~35-keyword
`str in` membership; convert IF the disjunction lowers, else defer). `_slice` (source-line slicing) / `_fin` / `error`
/ `unsupported` (raises) carry extra bits — assess per-stub, defer if they wall. Convert as many as pass; commit each
(or a batch).

## Gate battery (per converted stub / batch — driver-verifier FRESH)
Fidelity (`bin/self-annotate-mirror-check.sh` green 52/52; the converted primitive bodies byte-match live) ∧ proof:
pure_ast.py is a BIG file (262 stubs) — whole-file may WEDGE → `--fun <mangled_name>` per primitive + all-VCs-Valid +
L3-tc ✓ + wedge-note (ENV-note acceptable) ∧ corpus byte-diff 0 (the Parser model gated on the pure_ast mirror
context / a `_Tok`/`seq _tok` sentinel; corpus programs don't define this Parser → inert; VERIFY `bin/byte-diff-
sweep.sh` EMPTY — pure_ast is a MIRROR file, not corpus, so mirror-only ⇒ 0 by construction unless the emitter
changed shared lowering) ∧ ledger==3 (record+seq+concrete-int, no axiom; token-kind ints NOT abstract vals) ∧ count
strictly DOWN ∧ non-vacuity (MUTATION TEST: change a token-kind int / a field read → emitted .mlw changes; real
Seq.get/tok_type/tok_string, NO isinstance_op 0 0 / int-hash / opaque getter / abstract-int-token facade).

## Honest costed scope
~7-10 primitives from ONE Parser-stateful-record + _Tok model — the highest count-ROI increment on the frontier
(25%-of-trust file, a shared cluster). If the stateful Parser retrofit walls at Gate S → CERTIFIED-BOUNDARY. Deferred
(harder clusters): the ~50 grammar parse-rules (token→node construction), ~50 visit_X unparse, the char-level _lex.

## §GATE-S — SPIKE OUTCOME: **REFUTE at the emitter (CERTIFIED-BOUNDARY)**. Count unchanged (1013), ledger 3, tree clean.

Gate S step 1 reproduced: `why3 prove -P z3 getting-better/parser-oracle.mlw` → all 6 goals as reported
(cur_field/at_op_true/at_op_false/cur_prog'vc/peek_prog'vc **Valid**, evil_twin **Unknown**), ledger-neutral. The
**model is sound**. Gate S step 2 (the EMISSION make-or-break) **REFUTES** — but *below* the model, at PyCSL's
class-field type system. Verified by four focused emitter spikes (all in scratchpad, reverted; NO mirror edit made):

1. **List read is `array` (bounds-checked), NOT the oracle's total `seq`.** `def f(a: List[int], i) requires True:
   return a[i]` → `a[i]` emits *"Sub-goal index in array bounds"* → **Timeout/unprovable** under `requires True`. The
   oracle's `Seq.get` totality (no OOB VC) does NOT match PyCSL's list lowering. **However this is recoverable:** a
   **class invariant** `0 <= self.i < \length(self.toks)` discharges the OOB (`cur`'s array read → **Valid**), and a
   co-invariant `\length(self.toks) >= 1` steers the auto record witness to `by { toks = Array.make 1 0; i = 0 }`
   (`auto_trust._extract_array_lengths`), satisfying the type invariant. Int-element stateful record: **fully Valid.**
   So the OOB / `requires True` concern (§6b) is a NON-issue via the class invariant; the oracle over-approximated
   with `seq` but the faithful `array`+invariant model proves.

2. **THE WALL — a record-typed (or any parametric-element) class field does NOT emit; it collapses to `array int`.**
   `_Tok` itself becomes a clean record: `self.type:int, self.string:str` → `type tok = { py_type: int; string:
   string }` (int + native-string fields, record `by` witness — works). And a record-element list works **as a
   PARAM**: `def f(a: List[Tok], i) : return a[i].type` → `a: array tok`, `(let _rec_ = a[i] in _rec_.py_type)`,
   **L3-tc ✓**. But the SAME `List[Tok]` as a **class field** (`self.toks: List[Tok]`) emits `type p = { mutable
   toks: array int; ... }` — the element type is **discarded** — so `cur` (declared `-> tok`) returns `int`:
   **L3-tc ✗ — "This expression has type int, but is expected to have type ...tok".** Confirmed systematic: even
   `List[List[int]]` as a field collapses to `array int` (nested-list faithful lowering is PARAM-ONLY), then
   `self.g[i][j]` fails L3-tc *"unbound … 'iter_length'"*. There is **no `#@` directive** to declare a `seq/array
   <record>` self-field (the cited "K1 seq pyval self-field" is a hand-written store `.mlw` w/ `materialize`/
   `snapshot` vals + `Return_seq`, not an emitter-generated typed field).

**Root cause (single, localized):** `Module5_IREmitter._field_type_from_annotation[_inst]` maps `List[X]` → the
coarse tag `"list"` (→ `array int`), discarding `X`. The param resolver is richer and disjoint. Class fields carry a
coarse tag set only (`int`/`list`/`dict`/`set`/`str`/`real`/tuple-record/ExprIR); no parametric element survives.

**Why this is a BUILD, not a verbatim conversion (so → boundary, per Gate S "seq _tok self-field won't emit"):**
faithful conversion of `cur`/`at_op`/… (they do `self.toks[self.i].type/.string`) *requires* the `array _tok` field.
A parallel-array workaround (`self.tok_types`, `self.tok_strings`) would break the fidelity byte-match (bodies must
equal live). Emitting the field faithfully needs ~4-5 coordinated cross-module touch points, all with full-corpus
byte-diff exposure: (a) M5 `_field_type_from_annotation_inst` → return an `array:<record>` tag when `X` is a
registered record class (precedent: `_m5_tuple_record_name`); (b) M6 record-field type emit `array:<rec>` → `array
<mangled_rec>` (find the `"list"`→`array int` site); (c) `auto_trust._build_witness_str` → `Array.make N <rec-witness
literal>` for a record-element array (currently hard-codes element `0`); (d) confirm `self.f[i]` field-array read
reuses the param `(let _rec_ = … in _rec_.f)` lowering; (e) `_Tok`'s `start`/`end` are `Tuple[int,int]` → tuple-record
synthesis (WL-03) must compose. That is an authorize-first multi-session emitter feature, not this increment's
"convert clean primitives verbatim." **Do NOT grind — recorded as boundary.**

**De-risked for the follow-on:** the value model is *proven end-to-end except field-element-typing* — int-element
stateful record (Valid), `_Tok` int+string record (emits), record-element **param** array + projector (L3-tc ✓),
class-invariant OOB discharge (Valid), witness steering via `\length >= 1`. Build (a)-(e) above, then the ~7-10
primitives convert on this exact shape. Token kinds: concrete ints confirmed correct (Python 3.14 `tokenize.OP`=**55**,
NAME=1, NUMBER=2, STRING=3) — the oracle used 54 (older Python); the emitter must use the live value 55.
