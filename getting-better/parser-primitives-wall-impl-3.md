# parser-primitives-wall-impl-3.md — ROUND 3 (re-scoped: 205 stubs, not 7-10; low-blast-radius gate)

Rounds 1-2 stand for the MODEL: the fable oracle (`parser-oracle.mlw`) CONFIRMED a `_tok` record + token stream +
`Seq.get` (total ⇒ NO OOB VC under `requires True`), ledger-neutral; and round 2 BUILT + committed the expensive
prerequisite `List[RecordType]` class field → `array <record>` (614fd814, fixture 0925, byte-diff 0).
Round 2 then hit CERTIFIED-BOUNDARY on ONE thing: converting a primitive needed `@mutable_state` on the mirror
`_Parser`, which flips a GLOBAL gate that also emits the entire emit_ir ADT theory + file-wide field qualification
= **+283 mlw lines** in a 262-stub runtime-imported file.

## WHAT ROUND 2 GOT WRONG (the re-scope — this is why round 3 is worth running)
Round 2 scoped the wall at "~7-10 primitives, payoff capped ~3". That was measured on `pure_ast.py` ALONE.
A read-only census over all 929 portable stubs shows the SAME W8 token-cursor shape gates **205 stubs across THREE
files** — `pure_ast._Parser` (110), `Module2_Parser._ContractParser` (81), `proof2why3/parser._Parser` (14) — and
**292 stubs in those three files hit NO other known wall** (67% of all 439 wall-clean stubs in the whole mirror).
Realistic mechanical yield once the gate opens: **~90-120 stubs = ~31% of the remaining portable TCB.** That changes
the ROI by an order of magnitude and justifies building the gate properly instead of routing around it.

## The three capabilities (the expensive one is ALREADY BUILT)
- (0) DONE — `List[RecordType]` class field → `array <record>` (614fd814).
- (i) **LOW-BLAST-RADIUS record-element class-field gate.** The blocker is NOT the field itself but that today the
  only route to a record-typed self-field is `@mutable_state`, whose gate ALSO pulls the full emit_ir ADT theory +
  file-wide field qualification (+283 lines). Build a NARROW gate: a class with record-typed fields emits its record
  + field access WITHOUT pulling the emit_ir theory. Make-or-break: does a `_Parser`-shaped class (`toks: List[_Tok]`,
  `i: int`) emit `{ mutable toks: array tok; mutable i: int }` + a working `cur` WITHOUT the +283-line theory pull,
  and does the mirror-wide L3-tc sweep stay at ZERO failures?
- (ii) **varargs-membership** `def at_op(self, *vals): ... t.string in vals`. Narrowly scoped BY CONSTRUCTION: only
  **12 varargs stubs exist in the entire mirror and all 12 are in these two parser files.** Model `*vals` as a
  `seq string` / bounded str-eq disjunction over the call-site literals.
- (iii) **self-field-array-read projection**: `self.toks[self.i].py_type` must lower to a real record projector
  (`let _rec_ = toks[i] in _rec_.py_type`, which ALREADY works for a PARAM) not the `get_py_type` opaque facade.
- Bounds: `Seq.get`/array read OOB is discharged by a class invariant `0 <= self.i < length(self.toks)` (round-2
  spike PROVED this: `cur`'s array read → Valid, witness `by { toks = Array.make 1 <rec-default>; i = 0 }`).
- Token kinds → CONCRETE int literals (`tokenize.OP`=55, NAME=1, NUMBER=2, STRING=3) — NOT abstract vals (else a
  distinctness axiom moves the ledger off 3). [fable mandatory rule]

## Gate S — make-or-break spike (capability (i) ONLY), refutation exit
Spike the low-blast-radius gate on a `_Parser`-shaped probe. PASS ⇒ measured line delta stays small AND the
mirror-wide L3-tc sweep stays at 0 failures AND `cur` typechecks+proves. REFUTE (the record-field route is
inseparable from the emit_ir-theory pull, or the sweep regresses) ⇒ CERTIFIED-BOUNDARY, record, stop.

## §GATE-S RESULT — **PASS** (capability (i) BUILT, fixture-witnessed, mirror byte-inert)

Probe: a `_Parser`-shaped class (`@dataclass Tok(py_type,string,start,end)`; `@mutable_state class Parser` with
`self.toks: List[Tok]` + `self.i: int`; class invariants `0 <= self.i`, `self.i < \length(self.toks)`,
`\length(self.toks) >= 1`; `cur(self) -> Tok: return self.toks[self.i]`).

### The decisive number: **−277 lines** (303 → 26)
The blast radius round 2 measured was NOT the record field — it was the `emit_ir` ADT theory that the coarse
`@mutable_state` disjunct dragged in unconditionally. Probe emission **before**: 303 lines, of which lines 8-282 are
the ~277-line theory (80-ctor sum + `kind_of` + every projector/discriminant + recursive `size` + its size-decrease
lemmas + `irlist`/`iropt`). **After**: **26 lines** — `type tok`, `type parser = { mutable toks: array tok; mutable
i: int }` with its three invariants + the `Array.make 1 { py_type = 0; … }` record-literal witness, and
`parser__cur`. The record-typed class field is therefore **fully separable** from the emit_ir theory pull.

### The narrow gate (Module6_WhyMLTranspiler.transpile + `_resolve_deferred_exprir_theory`)
The theory's gate is a 5-way disjunction. Four disjuncts (`_uses_ir_node_param`, `_uses_stmt_ir`, `_uses_call_kw`,
`_uses_tparam`) are POSITIVE evidence of real emit_ir use — untouched, still eager. The fifth,
`_mutable_state_classes`, is the coarse one: it fires for any `@mutable_state` class, including one whose state is
plain records/arrays/ints. When ONLY the coarse disjunct fires we now **defer**: park a sentinel line, emit the rest
of the file, and splice the theory back in iff the emitted text references a symbol the theory DECLARES
(`_exprir_theory_symbols` — types, `with`-group members, constructors, `let (rec) function`/`val`/`lemma`/`exception`
names, inline record field labels — derived from the theory's OWN emitted text, same anti-drift discipline as
`_reserved_exprir_symbols`). Any reference, including one inside a comment, re-inserts ⇒ conservative in the safe
direction. No new directive, no language-surface change, no allow-list.

### Gate battery
- **Mirror-wide L3-tc sweep**: **0 failures before, 0 failures after** (52/52).
- **Mirror byte-diff (52 files, emission)**: **0** — every file that actually uses emit_ir gets the theory spliced
  back byte-identically. This is the real inertness proof for the shared-lowering change.
- **Corpus byte-diff (770 files)**: **8 differ, each exactly `-277 / +0`** (the theory block deleted, nothing else) —
  `0746 0750 0772 0773 0774 0775 0776 0925`, i.e. precisely the `@mutable_state` corpus programs that never touch
  emit_ir. Strict byte-diff 0 is UNREACHABLE for any real capability-(i) implementation (0925 has the probe's exact
  shape), so the gate was discharged the stronger way instead: all 8 re-run under full proof — 7 × `SUCCESS! All
  contracts formally proven`, and `0776` is the `# pycsl-expected: FAIL` negative control, which fails identically
  at HEAD. Net effect on those 7: same semantics, ~277 fewer lines of dead SMT context.
- **Ledger 3** (no axiom, no abstract val, `proof_axiom_allowlist.py` untouched); **fidelity 52/52**;
  **`\trusted` count 1041 UNCHANGED** (infra + fixture, no conversion — no mirror file touched).
- **Fixture** `test-suite/corpus/pycsl-reference/0926_record_field_no_exprir_theory.py`: 32 lines emitted, **all VCs
  Valid** incl. `Sub-goal index in array bounds of goal parser__cur'vc: Valid` (the OOB discharges via the class
  invariant, exactly as round 2's spike and the fable oracle predicted). **NON-VACUITY**: the evil twin
  (`\result == toks[0].start + 12345`) is **Unknown** — does NOT prove. **ANTI-FACADE**: the param projection emits
  the real record projector `(let _rec_ = toks[0] in _rec_.py_type)`, not an opaque getter.

### Capability (iii) is SEPARATE (does NOT fall out of (i))
Measured on the probe: adding `def cur_type(self) -> int: return self.toks[self.i].py_type` emits
`(get_py_type self.toks[self.i])` — the opaque facade — and **fails L3-tc** (`This expression has type
PyCSL_Program.tok, but is expected to have type int`). The `let _rec_ = … in _rec_.<f>` projector path is wired for
a PARAM array read only; the SELF-FIELD array read still routes to the abstract-op fallback. So W1's `cur`/`peek`/
`advance` are unlocked by (i) alone, but any primitive that PROJECTS a field off the cursor needs (iii) first.

## Build order (only if Gate S PASSES) — convert in waves, commit each wave
W1 cursor primitives (`cur`/`peek`/`advance` + the non-varargs `expect_*`) → W2 varargs predicates (`at_op`/
`at_name`/`at_kw`/`accept_op`/`accept_kw`) via capability (ii) → W3 the mechanical ≤5-line grammar helpers →
W4 precedence-climbing binop chains + comma/dot accumulators + keyword→single-clause constructors.
Defer: the ~50 node-constructing grammar rules (`_parse_atom_bs`, 247 lines / ~50 CSLNode cases) and
`pure_ast._Unparser` (107 stubs, a separate shape).

## Gate battery (EVERY wave — the gate gap that cost 2 regressions is now mandatory)
fidelity 52/52 ∧ whole-file proof (or `--fun` + wedge-note on the big files) ∧ **mirror-wide L3-tc sweep at ZERO
failures** ∧ corpus byte-diff 0 vs the FRESH baseline (768 files; the old pinned one was stale) ∧ ledger==3 (concrete
int token kinds, no abstract-val token, no new axiom) ∧ count strictly DOWN ∧ MUTATION TEST + ANTI-FACADE (real
record projector / Seq.get / str_eq_op; no isinstance_op 0 0 / int-hash / opaque getter / shadow-local).

## §CAPABILITY (iii) — **BUILT, Gate S PASS, but it CONVERTS NOTHING TODAY** (W8 run #5)

### Gate S verdict: PASS (both halves), fixture `0928_self_field_array_projection.py`
The self-field array read now takes the SAME `_rec_` projector as a param array read, in two shapes:
- **DIRECT** — `self.toks[self.i].py_type` → `(let _rec_ = self.toks[self.i] in _rec_.py_type)`; `.string` →
  `_rec_.string : string`. (`_handle_attribute_expr`: a `Subscript` base that is a `FieldGet`/`Attribute` on `self`
  naming a field in `_record_array_fields`.)
- **LOCAL-BOUND** — `t = self.toks[self.i]` … `t.py_type` → `(!t).py_type`. (New `_record_field_elem_locals`,
  published by the 0927 record-ref pre-decl scan; consumed in the `Var` arm of `_handle_attribute_expr`.)
- **STRING TYPING** — a `str` field so projected is registered string-typed (`_record_elem_field_py_type` feeding
  `_is_string_expr`), so `<proj> == "EOF"` routes to the faithful `str_eq_op` (`ensures result <-> a = b`), NOT the
  int-hash / int-coercion. Without it the compare failed L3-tc (`has type string, but is expected to have type int`).

Gates: **mirror-wide L3-tc sweep 0 failures before AND after**; **corpus byte-diff 0** on all 771 baseline files
(baseline dir lacks `0927` — it predates that commit; worth re-pinning); fidelity **52/52**; ledger **3**
(allowlist untouched, `grep -c axiom` on the fixture = 0); token kind is the **concrete int literal 55**;
**MUTATION TEST pass** (`55`→`1` and `self.i`→`self.i + 0` both change the emitted `.mlw`);
**NON-VACUITY pass** (`direct_matches_local` / `texts_match` read the SAME element once through each path and
`ensures \result == 1`; the evil twin `\result == 0` is **Unknown**). Count **1007, UNCHANGED** — no conversion.

### Why the payoff is ZERO — the round-3 unlock list was measured on the WRONG shape
A read-only census of the whole live tree (`grep -rn 'self\.[a-z_]*\[[^]]*\]\.[a-z_]'`) finds **exactly ONE**
occurrence of the direct shape: `Module2_Parser._ContractParser._grab_reviewer_id` (a `_re.match` scanner — out of
reach for unrelated reasons). Every predicate the plan listed goes through **`self.cur()`**, not `self.toks[...]`:
- `pure_ast._Parser` has **no** `at_eof`/`at_bs`. Its only non-varargs primitives are `cur`/`advance` (converted in
  W1), `peek` (deferred (iv)/(v)), `error`/`unsupported` (raise), and `accept_*`/`expect_*` — which all CALL the
  varargs `at_op`/`at_kw`, so they are (ii)-gated, not (iii)-gated.
- `Module2_Parser._ContractParser.at_eof` is `return self.cur().type == "EOF"`; `at_bs`/`at_op`/`at_name` are
  `t = self.cur()` then `t.type == …` — all varargs except `at_eof`.
- `proof2why3/parser._Parser` has only `take` (converted) and `peek`/`expect` (Optional, deferred).

### TWO NEW CERTIFIED BOUNDARIES found while probing (both blocking the `at_*` family, neither is (iii))
- **(vi) record-returning SELF-METHOD call.** `self.cur().py_type` emits `(get_py_type (self_cur_0 ()))` — i.e. the
  self-method call is abstracted to `val self_cur_0 () : int`, which **drops the receiver entirely** and mistypes the
  record return. Two sub-gaps: `_resolve_dotted_signature` does not map a `-> <record class>` return to the record's
  WhyML type, and the concrete lowering `(parser__cur self)` exists only behind the opt-in `#@ sibling_concrete`
  marker (`expressions.py` ~line 4103) which additionally requires a `field_spec`. Until this lands, ANY primitive
  written against `self.cur()` (i.e. essentially all of them) stays trusted, and a `-> <record>` abstract val would
  be a FACADE (no link to the receiver) — a Gate C reject, not a shortcut.
- **(vii) tail-return `bool`→`int` coercion (a live emitter BUG, pre-existing and independent).**
  `def f(x: int) -> bool: return x == 55` emits `let f (x: int) : int = (x = 55)` and **fails L3-tc**
  (`This expression has type bool, but is expected to have type int`). `_bool_ir_to_int_wrap` is applied ONLY on the
  early/in-loop `raise (Return …)` path (`stmt_control_flow.py:1546`); the TAIL return (`return f"{indent}{val}"`)
  never wraps. A one-line fix at that site (gated on an `int` declared return) is the obvious repair, but it moves
  no count on its own — every candidate it would unblock is also (vi)-gated. NOT taken in this run: it is a shared
  lowering change with its own byte-diff exposure and zero standalone payoff.

### Revised build order for W8
(iii) DONE. **(vi) is now the true gate** for the `at_*`/`accept_*`/`expect_*` family — it must land BEFORE (ii)
varargs-membership is worth building, because every varargs predicate's first statement is `t = self.cur()`.
Then (vii) for the `-> bool` predicates, then (ii), then (iv)/(v) for the three `peek`s.
