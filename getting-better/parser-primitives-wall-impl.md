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
