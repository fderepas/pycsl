# lex-char-class-wall-impl.md — implementation plan (spike-gated, refutation exit)

Synthesized from `lex-char-class-wall.md` (driver report) and `lex-char-class-wall-response.md` (independent fable
review, Gate R: 9 oracle runs cited — hand `.mlw` spikes proved with Alt-Ergo / Z3, emit-and-grep of the real
emission, a full-file spike, and a CPython sweep over all 1,114,112 code points). The review REFUTED the report's
diagnosis: the 3 failing goals are `[@expl:termination] false` (the ported `lex` carries no `#@ loop variant`), the
mirror DOES accept in-body `#@ loop` lines, and with every char-class fix patched in, 10 of 43 `lex'vc` goals still
time out because of the `for op in _OP_TOKENS` (14-element list literal) context. Target: convert
`proof2why3/parser.py::lex` (1 stub) with no new axiom.

## 1. FIRST ACTION — Gate S, the make-or-break spike (response §5 step 0), no emitter change
In a scratch tree: port `lex` verbatim (bin/port-one-mirror-body.py), add the 5 `#@ loop` lines of step 1
(`#@ loop invariant 0 <= i` / `#@ loop variant n - i` on the outer loop; `#@ loop invariant i <= j` /
`#@ loop variant n - j` on each scan), emit with `--keep-mlw`, and attack the op-path goals in a hand `.mlw` copy
with the axiom-free levers only: (a) Why3 transformations (`split_vc`, pruning); (b) the list literal lowered once
as a `val constant _OP_TOKENS : seq string ensures { length = 14 /\ get 0 = "->" /\ ... }` (per-element facts, no
axiom); (c) a `#@ loop invariant` on the op loop stating every element has length >= 1.
- **PASSES** (all op-path goals Valid with the default Alt-Ergo -> Z3 chain, in the full emitted file, with only
  levers that the emitter / mirror can reproduce) -> build §2.
- **REFUTES** -> CERTIFIED-BOUNDARY for `lex` as a "list-literal iteration capacity" wall [COST/SCALE if a named
  emitter lever would fix it; CORRECTNESS only if no axiom-free lowering can]; record it, keep nothing in the
  mirror unless it proves, and spend no emitter effort on steps 2-4 for this stub.
- **REFINES** -> re-plan the residual; no sprawl.

## 2. Build (only after Gate S PASS), one gated increment each
1. Variants (5 `#@ loop` lines; `bin/check-mirror-loop-annotations.py` ratchet updated honestly).
2. Lever (b)/(c) as an emitter change if (b) is what unblocked: module-level list literals iterated by `for` lowered
   once with per-element facts. Byte-diff both corpora + mirror; every mover re-proved.
3. Determinism: `function py_<pred>_f` behind `py_<pred>_op` (arms 1 and 3 of the `is*` lowering), the 0/1 clause
   kept textually; movers 0447, 0605, 6820, mirrors statements / canonical / Module5_IREmitter (each re-proved —
   budget Module5's proof first).
4. Definitional `isalnum` (char-quantified, response C6; emitted only when isalnum co-occurs with a part).
5. Literal-membership fold for `<expr> in "<short literal>"` (response §3).
6. Conversion of `lex`: whole-file proof of mirror parser.py 0 non-Valid with the default chain, non-vacuous.

## 3. Gate battery (every increment)
Fidelity (sync, mirror-check, doc); corpus root + pyref byte-diff = exactly the intended movers, each re-proved;
mirror sweep, every mover whole-file re-proved; fast planes (+ --slow once per landing day); ledger 3;
`\trusted` strictly down only at step 6.

## 4. Costed scope
Step 0: 1-2 h. Steps 1-5: ~half a day each + re-proofs (Module5_IREmitter whole-file proof is the long pole).
Yield 1 stub; steps 3-5 are completeness gains for every `s[i].isX()` / `isalnum` / `in "lit"` site.
