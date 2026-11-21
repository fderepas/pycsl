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

## 5. Gate S result (executor lx1, 2026-11-01) — VERDICT: REFINES

All op-path goals of the ported `lex` are Valid **in the full emitted file** with the default Alt-Ergo -> Z3 chain
(-t 30, `-a split_vc`), using no axiom, but NOT with levers (a)/(b)/(c) as the plan wrote them: it takes (i) two
mirror frame invariants on the `for op in _OP_TOKENS` loop (`#@` lines the mirror ALREADY emits correctly) and
(ii) lever (b) in its PROVED form (`let function` with checked per-element AND per-length facts) — the assumed
`val constant` with element equalities only does not do it. The fr1 diagnosis "prover capacity in the
`_OP_TOKENS` context" (response §4a) is REFUTED: all 10 red goals were unprovable as emitted (missing frame
facts), not slow. The residual after the gate is exactly the 2 char-class scan goals (DIGIT, IDENT) — plan
steps 2-4, outside Gate S. Diagnostic: adding fr1's steps-2-4 char-class model on top makes the WHOLE file
0 of 410 non-Valid under the chain, non-vacuous (§5.3), so `lex` is convertible with no axiom. Not a
CERTIFIED-BOUNDARY: neither COST/SCALE nor CORRECTNESS; the remaining work is plan steps 1-6 as re-planned in §5.4.
Scratch: `/home/fabrice/git/pycsl/scratchpad/lx1/` (every file, script and log named below; the mirror edit is
`mirror-lex-gateS.patch`, not committed). Why3 1.8.2,
Alt-Ergo 2.6.3, Z3 4.13.3; every run via `scratchpad/heavy/heavy.sh`.

### 5.1 Root cause of the 10 (new; refutes response §4a "context-size symptom")
The `for op in _OP_TOKENS` lowering is a `while !_idx_op < Seq.length _seqlit_idx_op` loop whose body WRITES
`i` (`i := !i + str_length_op !op`) and `matched`, and whose only emitted invariant is `0 <= !_idx_op`. Why3
therefore havocs `i` and `matched` at that loop's exit. Every outer-loop path that passes the op loop (op-match,
op-normal-exit with `matched <> 0`, DIGIT, IDENT, fall-through `OP c`) sees a FRESH `i` unrelated to the
outer-loop head: `0 <= !i` preservation and `n - i` decrease are underivable — the provers time out on a goal
that has no proof. The `matched` half is visible in a task dump of `vBLpD` (which already carries the `i` frame):
`tasks_vBLpD/vBLpD-PyCSL_Program-lexqtvc30.why` has `i8 = (i1 at OPS)`, `H55 not idx < length seq` (normal exit),
`H56 not matched1 = 0` (havocked `matched`, no other fact) and goal `n - i8 < n - i1` — false. This is why fr1's C4 ("defused" op branch) stayed at
the same 10: defusing the increment does not restore the lost `i`.

### 5.2 Measurements — `lex'vc` goals of the full file, chain = Valid iff AE or Z3 Valid
| file | levers | lex'vc non-Valid (chain) | what is left |
|---|---|---|---|
| `lex-v.mlw` (real emission: ported lex + 5 `#@ loop` lines) | none (baseline) | **10 / 43** | 5 outer paths × (inv `0<=i` preservation + variant), all Timeout/OOM both provers |
| `vC.mlw` | (c) alone: `invariant forall k. len(seq[k]) >= 1` | 11 / 45 | the 10 + (c)'s own init (Timeout both) |
| `vBLp.mlw` | (b) alone, proved form | 10 / 43 | the 10 |
| `vD.mlw` | frame `!i = (!i at OPS)` alone | 4 / 45 | op-break variant, op-normal-exit variant, DIGIT, IDENT |
| `vDM.mlw` | frame `i` + `!matched = 0` | 3 / 47 | op-break variant (needs `len(op) >= 1`), DIGIT, IDENT |
| `vCD.mlw` / `vCDM` | frame + (c) | 4 / 47, 3 / 49 | (c)'s init (line 738) Timeout both; DIGIT; IDENT |
| `vCDM` + (a) `remove_unused` / `remove_unused_from_context` / `remove_triggers` / `compute_in_goal` | frame + (c) + (a) | 3/49, 3/47, 3/49, 3/49 | (c)'s init stays red under every transform |
| `vCDM` + (a) `inline_all` + `compute_in_goal` | | no result | Why3 `anomaly: Stack overflow` after 11 goals (`raw_inline.txt`) |
| `vBDM.mlw` | frame + (b) AS WRITTEN (assumed `val constant`, element equalities only) | 3 / 47 | op-break variant still red: AE has no literal lengths, Z3 Timeout/OOM |
| `vBLpD.mlw` | frame `i` + (b′) | 3 / 45 | op-normal-exit (no `matched` frame), DIGIT, IDENT |
| `vBLpDM.mlw` | frame `i` + `matched` + (b′) | **2 / 47** | DIGIT (#38, `isdigit_1` vs `py_isdigit_op`), IDENT (#43, `isalnum_1`/`str_contains_op`) |

(b′) = `let function _OP_TOKENS_lit () : seq string ensures { Seq.length result = 14 /\ Seq.get result k = <elem k>
(14 facts) /\ String.length (Seq.get result k) = <len k> (14 facts) /\ forall k. 0 <= k < 14 -> length >= 1 } =
<the emitted 14-cons literal>`, and `let _seqlit_idx_op = (_OP_TOKENS_lit ()) in`. Its own VC
`_OP_TOKENS_lit'vc`: Alt-Ergo Timeout, **Z3 Valid (1.28 s)** — so the chain proves it, and the `lex` context
carries only the postcondition (no cons chain, no `pystr_chr` 95-disequality terms). Axiom-free: the facts are
checked, not assumed. Lever (a) alone was not run on the baseline: the 10 baseline goals are not derivable
(§5.1), and on `vCDM` no transform changed any count.

### 5.3 The gate file (whole file, not just `lex'vc`)
`gateG.mlw` = the REAL mirror emission `lex-mirrorDM.mlw` (worktree `pycsl-lx1`, mirror `parser.py` with the
ported body + the 5 planned `#@ loop` lines + `#@ label OPS` + `#@ loop invariant i == \at(i, OPS)` +
`#@ loop invariant not matched` before `for op in _OP_TOKENS:`; `--no-proof` L3-tc ✓; it emits
`label OPS in` and `invariant { (!i = (!i at OPS)) }` / `invariant { (not (!matched <> 0)) }` — byte-equal to
the hand `vDM` modulo invariant order) + lever (b′) only (`mkG.py`). `full.sh gateG.mlw` (`gateG.log`):
```
== gateG alt-ergo: goals 410; non-Valid 3   (_OP_TOKENS_lit'vc Timeout; lex'vc #38, #43)
== gateG z3:       goals 410; non-Valid 2
CHAIN non-Valid: 2 of 410  ->  lex'vc #38 (DIGIT scan exit variant), lex'vc #43 (IDENT scan exit variant)
```
Every op-path goal (op loop init/preservation/variant, `Seq.get` bounds, op-match and op-normal-exit outer
invariant + variant) is Valid. Diagnostic only (plan steps 2-4, NOT Gate S levers): `gateG_full.mlw` = gateG +
fr1's char-class model (determinism via logic fns, char-quantified `isalnum`, `in "_'"` literal fold, lemma
dropped; `mkF.py`, `gateG_full.log`): **CHAIN non-Valid 0 of 410** (AE misses only `_OP_TOKENS_lit'vc`,
Z3 only one `lex'vc` variant, Out of memory 7.6 s, which AE proves). Non-vacuity: `gateG_full_vac.mlw` (`lex`
with `ensures { false }`) -> Postcondition AE Timeout, Z3 Unknown (`vac.log`) — the green is not vacuous.

### 5.4 Consequences for §2 (re-plan, no sprawl)
1. Step 1 becomes **5 + 3 `#@` lines**: the 5 variant/invariant lines, plus `#@ label OPS`,
   `#@ loop invariant i == \at(i, OPS)`, `#@ loop invariant not matched` on the op loop (mirror-only, already
   emitted correctly; ratchet +7 `#@ loop` lines, plus the `#@ label`). Alone this takes `lex` from 10 to 3 red.
2. Step 2 lever is (b′), and it must be the PROVED form with LENGTH facts: an emitter change lowering a
   module-level list literal iterated by `for` once as a `let function` whose ensures lists element equalities
   AND `String.length` of each element (Z3 discharges them in its own small goal). The plan's assumed
   `val constant` with element equalities only is refuted (vBDM). (c) is not needed and is harmful alone
   (its init never proves against the inline literal). (a) buys nothing.
   COST/SCALE note: (b′) is a named emitter lever; without it the mirror alone stops at 3 red (vDM).
3. Steps 3-5 (determinism, definitional `isalnum`, literal fold) remain necessary and sufficient for the last 2
   goals (`gateG_full`: whole file 0 of 410 under the chain, non-vacuous). Then step 6.
4. Generalisable finding (for the emitter, not this stub): every `for x in <seq>` lowering havocs every
   variable its body writes — any loop with an early `break` that updates an outer variable needs a frame
   invariant; the emitter could synthesise `x = x at L` for variables written only on the `break` path.
