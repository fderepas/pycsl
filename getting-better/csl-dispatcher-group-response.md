# `csl-dispatcher-group-response` — independent review

*Reviewer: independent session, 2026-08-31. I did not see the producing session's reasoning.
Everything below is re-derived from the repository, the worktree at `scratchpad/w3/wt`
(HEAD `1b56211d`, exactly one modified file: the Module5 mirror), the two pre-emitted trees
`scratchpad/w3/mlw` / `scratchpad/w3/mlw_spike`, and my own oracle runs. My scratch files are
under `scratchpad/w3/rev/`.*

## VERDICT: ACCEPT-WITH-CARVE-OUT

The change is sound in direction and in mechanism: every directive added is either true of the
live source or strictly weaker than what the baseline silently assumed. The baseline modeled all
92 recursive `_csl_to_ir` sites through `val self__csl_to_ir_1 (x0: emit_ir) : emit_ir` — a
contract-free abstract oracle that Why3 treats as PURE, TERMINATING and NON-RAISING, all three of
which are false of the live dispatcher. The new `let rec … with` group replaces those three false
assumptions with checked declarations. Nothing a caller could previously prove correctly becomes
easier; several things a caller could previously prove WRONGLY become impossible.

Carve-outs (none blocks acceptance of the directive change itself; all must be recorded):

1. **The whole-file proof plane is OPEN at review time.** The proof of the changed file is still
   running (PID 1115733, cwd `scratchpad/w3/wt`, started 10:18). The report itself only claims the
   PRE-diverges run (1481/1595, 114 termination subgoals). Acceptance is conditional on that run
   finishing 0 non-Valid. Every other plane is closed below.
2. **The report's `\diverges` count is wrong** (§Q6, item 1): 53 members + the dispatcher carry
   it, not "74 members".
3. **"the 75 `_csl_*` handlers it names are ALREADY converted" is false twice over** (§Q6,
   item 2): `_csl_in` — which IS in the dispatch table — is still a `\trusted` facade emitted as
   an abstract `val` whose contract understates the live body's effects, and two live handlers
   (`_csl_subscript_field`, `_csl_nested_subscript`) have no mirror def at all (known mirror
   drift, but it makes "75" the wrong population for every per-member count in the report).
4. **Latent cross-module hazard, currently unexercised**: in the three other mirrors the imported
   `val pycsltojsonemitter___csl_to_ir` carries only `raises { PyCSLIRError }` — no
   `PyCSLSemanticError`, no `diverges`, no `writes` — and the imported member vals carry no
   `writes`. Today there are ZERO cross-module call sites (1 occurrence each = declaration only),
   so nothing is unsound NOW, but the first future cross-module caller would prove against an
   effect-understating contract. This should be a named follow-up.

## Oracle runs (all with `export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH`)

| # | Command | Result |
|---|---------|--------|
| O1 | `python3 bin/check-shadowed-selfcalls.py --emit-dir scratchpad/w3/mlw` | `14 CONVERTED method(s) … 125 bypassing call site(s)` |
| O2 | `python3 bin/check-shadowed-selfcalls.py --emit-dir scratchpad/w3/mlw_spike` | `13 CONVERTED method(s) … 33 bypassing call site(s)` — **report's 14/125 → 13/33 CONFIRMED** |
| O3 | `git -C scratchpad/w3/wt diff … \| grep -vE '^[+-][[:space:]]*#@' \| wc` on the ±lines | **0 non-directive changed lines — report §4 CONFIRMED** |
| O4 | `PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py src/self-annotate/src/frontend/Module5_IREmitter.py --import-path src/pycsl --no-proof --keep-mlw` (in wt) | `[level] L1 ✓ L2 ✓ L3-tc ✓ … Verification SUCCESS (--no-proof …)` |
| O5 | `diff <fresh emit> scratchpad/w3/mlw_spike/…Module5_IREmitter.py.mlw` | exactly one line: `< diverges` — **mlw_spike is STALE by the final iteration**; the worktree DOES emit `diverges` on the dispatcher's `with` clause |
| O6 | `why3 prove -P alt-ergo scratchpad/w3/rev/rev_effects.mlw` | both goals **Valid** — a `let rec … with` group with `raises { E -> true }` + `diverges` proves; a catching caller must establish its post from the handler alone |
| O7 | `why3 prove -P alt-ergo scratchpad/w3/rev/rev_neg_raises.mlw` | **`this expression raises unlisted exception E`** — a caller can NOT silently ignore a declared raise (hard error, not a warning) |
| O8 | `why3 prove -P alt-ergo scratchpad/w3/rev/rev_neg_exploit.mlw` | `ensures { result = 42 }` behind a handler: **Unknown** — the trivial exceptional post grants a caller nothing |
| O9 | `why3 prove -P alt-ergo scratchpad/w3/rev/rev_neg_div.mlw` | caller of a `diverges` val without declaring it: **WARNING only** (`termination of this expression cannot be proved, but there is no 'diverges' clause…`), module still checks — Why3 1.8.2's divergence check is advisory at call sites |
| O10 | `why3 prove -P alt-ergo scratchpad/w3/spike_cc.mlw` / `spike_cc_neg2.mlw` | **Valid** / **`this expression produces an unlisted write effect`** — report §5's spike + negative control REPRODUCE |
| O11 | `python3 bin/count-trusted-directives.py` (in wt) | `markers 491 · grep-substring 516 · offset 25 · attached 491 · unattached 0 · OK` — **491/516 unchanged CONFIRMED** |
| O12 | `python3 bin/check-trusted-frame-honesty.py --verbose` (in wt) | `OK (trusted ratchets 6/76, converted ratchets 63/130)`; lists `_csl_mktuple` and `_csl_call_expr` as `via-callee MODEL-VISIBLE ['_fresh_var_counter']` — the two erasures are ON the fourth plane's radar, ratcheted, not hidden |
| O13 | `bash bin/check-self-annotate-sync.sh` / `bash bin/self-annotate-mirror-check.sh` (in wt) | exactly the standing baseline: 2 DIVERGED (both module6 files, NOT Module5), 3 mirrors drifted — no new fidelity violation |

## Q1 — is `#@ raises E when True` on 53 members sound? Could it weaken a caller?

**SOUND, and it cannot weaken anything. It strictly strengthens caller obligations.**

Emitted form (spike mlw, e.g. line 2796ff): `raises { PyCSLSemanticError -> true }` /
`raises { PyCSLIRError -> true }` on each `let rec`/`with` member — a DEFINED function whose body
Why3 checks (exceptions must be listed exactly; O7 shows an unlisted raise at a caller is a hard
error, and the report's own converged fix-loop shows over-listing is rejected too).

The weakening question has a crisp answer because the baseline is on disk: in
`scratchpad/w3/mlw/…Module5_IREmitter.py.mlw:1592` the recursion went through
`val self__csl_to_ir_1 (x0: emit_ir) : emit_ir` — no raises clause at all. So BEFORE, every
caller's proof was entitled to assume the recursive call NEVER raises (a false assumption:
the live dispatcher raises `PyCSLIRError` on an unknown node type and propagates handler
exceptions). AFTER, callers must either declare or catch, and a catching caller learns only
`true` on the exceptional path (O8: a post depending on the handler value being reached with
extra facts is Unknown). Assumptions were removed, none added. No previously-should-fail caller
proof can now pass: the direction of change at every call site is monotonically MORE obligations
(O7) and LESS hypotheses (O8).

One asymmetry to record: the dispatcher's own clause is `raises { PyCSLIRError,
PyCSLSemanticError }` (bespoke producer) and the cross-module import val carries only
`raises { PyCSLIRError }` — see carve-out 4.

## Q2 — is `#@ \diverges` sound? Does it "assert nothing"?

**Sound here; the "asserts nothing" claim is TRUE in the hypothesis direction and needs one
caveat in the obligation direction.**

Confirmed with O6/O9: `diverges` adds no assumption a prover could use (it is not a fact, it is
the ABSENCE of a termination obligation), so it cannot be "the source of a false claim" — the
report's statement is correct as far as it goes. Two qualifications the report does not make:

* `diverges` is not inert — it is precisely what DELETED the 114 `Sub-goal termination of
  pycsltojsonemitter___csl_to_ir'vc` failures. The group's termination is now UNPROVEN AND
  UNDECLARED-AS-PROVEN, which is honest (the report's §5 says so), but the baseline comparison
  matters: the old shadow `val` (no `diverges`) let every caller assume the recursion
  TERMINATES. The change replaces a false termination assumption with an honest refusal to
  claim termination. Strictly better.
* In Why3 1.8.2 a NON-diverges caller of a diverges function gets only a WARNING (O9), not an
  error. Inside this artefact that is moot — every caller of a diverging member is in the group
  and declares `diverges`, and the fresh emit (O5) puts `diverges` on the dispatcher too — but
  the discipline is advisory, not enforced, should a future out-of-group caller appear.

**Count correction**: the mirror carries `#@ \diverges` on **53 members + the dispatcher = 54**
(diff: `+54 #@ \diverges`; census of the wt mirror: 53 of 74 handler defs), not "74 members".
The 21 without it = 19 `assigns \nothing` members + the 2 still-trusted (`_csl_in`,
`_csl_list_to_ir`).

## Q3 — exactly 2 erased, 17 genuine leaves?

**CONFIRMED, independently, from both directions.**

* Emitted (spike mlw): the group has 56 members; exactly 2 carry `writes {  }` with a
  comprehension-oracle body — `_csl_mktuple` = `(IrMkTupleN (list_content_comp_3 …))` (line
  3038), `_csl_call_expr` = `(IrCallN node.func (list_content_comp_4 …))` (line 3244). Both
  also lost `raises` and `diverges` (see Q6 item 5). The other 17 `\nothing` members are
  emitted as standalone non-recursive `let`s (lines 2653–2780) — the same 17 names as the
  mirror's `\nothing` list minus the two erased.
* Source (AST walk over LIVE `src/pycsl/frontend/Module5_IREmitter.py`): each of the 17 leaves
  makes ZERO `self.<m>(…)` calls and ZERO attribute writes — `assigns \nothing` is true of the
  source. The 2 erased members are the ONLY handlers whose `self._csl_to_ir` calls occur
  exclusively inside a comprehension — exactly the report's stated mechanism.
* The erasure is NOT introduced by this change: the baseline mlw has the identical
  `writes {  }` + `list_content_comp` body for `_csl_mktuple` (baseline line 2934). And O12
  shows the frame-honesty plane sees both as `via-callee MODEL-VISIBLE ['_fresh_var_counter']`
  under ratchet — tracked, not hidden.

## Q4 — 0 non-directive lines in the mirror diff?

**CONFIRMED** (O3). Composition of the diff: `+105 #@ raises`, `+75 #@ sibling_concrete`,
`+54 #@ \diverges`, `+55/-55 #@ assigns` (55 handlers flipped `\nothing` →
`self._fresh_var_counter`; the dispatcher's `assigns` pre-existed, giving the report's "56 of
75"). Both fidelity gates then run at exactly the standing baseline (O13): 2 DIVERGED, both in
module6 files, neither of them Module5. Fidelity preserved.

## Q5 — can this make a previously-failing proof pass for a WRONG reason?

**No mechanism found.** Checked specifically:

* **Sibling `ensures` assumption in the `let rec … with` group**: every member's contract is
  literally `requires { true } ensures { true }` (56× each, counted in the fresh emit). There is
  no functional postcondition to assume, established or not; the only inter-member contract
  content is the effect row, which Why3 checks exactly (O7, O10-neg). The concern is vacuous
  here by construction.
* **`diverges` masking a defect**: it masks exactly one thing — nontermination of the group —
  and the baseline masked the SAME thing more strongly (shadow val assumed termination) while
  also assuming purity and exception-freedom. No defect provable before is unprovable now;
  the reverse direction (new false greens) would need a caller gaining hypotheses, and every
  hypothesis went away, none arrived (O6–O9).
* **The 2 erased members**: unchanged from baseline (Q3), so no NEW wrong pass.
* **Corpus**: the diff touches only the mirror file, which is not an input to reference-corpus
  emission; byte-inertness holds by construction (and the live tree is untouched: `git -C wt
  status` = 1 modified mirror file).
* Residual risk is confined to the still-running whole-file proof (carve-out 1) and the
  advisory-only divergence check at future out-of-group call sites (Q2).

## Q6 — over-claims and wrong reasons

1. **"74 members carry `#@ \diverges`"** — wrong number; 53 members + dispatcher = 54 directives
   (diff count and mirror census agree). Conclusion unaffected, count wrong.
2. **"the 75 `_csl_*` handlers it names are ALREADY converted"** — false. (a) `_csl_in` is in
   the dispatch table AND still `#@ \trusted` (facade body `return {}`), emitted as
   `val pycsltojsonemitter___csl_in … writes { self._fresh_var_counter }` with NO raises and NO
   diverges — while the LIVE `_csl_in` calls `self._csl_to_ir` (may raise, may not terminate)
   and `self._fresh_var`. The group's honesty therefore still bottoms out on one trusted arm
   whose contract understates effects. Pre-existing, not introduced here — but the report's
   "family is concrete now" framing overstates. (b) The mirror's table has 77 entries / 73
   distinct (the report's 79/75 is true of the LIVE file only); `_csl_subscript_field` and
   `_csl_nested_subscript` exist live with no mirror def at all.
3. **"Emission diff over all 52 mirrors: exactly 4 change"** — the number reproduces
   (`cmp` over both trees: Module5, `frontend/__init__`, `frontend/ir_resolve`,
   `src_self-annotate_src_pycsl.py`), but the ATTRIBUTION is wrong for 2 of the 4:
   `frontend/__init__` and `ir_resolve` differ ONLY by the unrelated `m5_current_class_present`
   `val function` → unit-taking `val` demotion (commit `b261c5e5`, in wt's HEAD, absent from the
   baseline emission). Only Module5 and pycsl.py carry any trace of THIS change.
4. **`mlw_spike` is stale** (O5): it lacks the dispatcher's `diverges` that the report's §3
   narrative ends on. The worktree is right; the shipped evidence tree lags one iteration.
   A reviewer diffing only the provided trees would wrongly conclude the dispatcher directive
   was never emitted.
5. **§5 understates the erasure on the two erased members**: not only is their
   `assigns \nothing` false of the source — their emitted contracts also lack `raises` and
   `diverges`, though the source bodies can raise and recurse. Same root cause (the
   comprehension lowering to a pure oracle), but the honest-limits section names only the frame.
6. Confirmed as stated: 491/516 trusted (O11), axiom-free file (0 `axiom` lines in baseline,
   spike, and fresh emit; the diff adds no proof directives), 14/125 → 13/33 (O1/O2),
   `spike_cc` positive + negative controls (O10), 1481+114=1595 arithmetic consistent, and the
   1199-goal figure for the unchanged file matches `scratchpad/w3/proofs/RESULTS`.

## Bottom line

The central claim of the report survives independent attack: the record's blocker (3) was indeed
a two-member fact wrongly generalized to the family, and the effect rows now declared are the
weakest honest ones — every direction of change at every call site removes a false assumption or
adds an obligation. Accept once the running whole-file proof of
`src/self-annotate/src/frontend/Module5_IREmitter.py` completes with 0 non-Valid; record
corrections (Q6 items 1–5) and the cross-module import-val understatement (carve-out 4) in the
ledger.
