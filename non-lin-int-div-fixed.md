# non-lin-int-div-fixed.md — close the nonlinear-int-div vacuity SOUNDNESS hole

**This is a SOUNDNESS fix, not an opacity/faithfulness feature — it is the highest priority.** Several
nonlinear integer-division facts let the SMT solver derive `false` from a VC's hypotheses, after which
EVERY goal is vacuously provable → **a false `ensures` passes as green**. That is worse than opacity: it
can certify wrong code. (memory: `vacuity_nonlinear_div`; it currently BLOCKS the csys de-trust.)

**Two-track fix:** (T1) a *detection* safety-net that makes the hole impossible to hit silently — turn
the existing opt-in non-vacuity gate into a HARD DEFAULT; (T2) *root-cause* elimination of the nonlinear
div facts so the corpus is genuinely non-vacuous, not just guarded.

---

## 1. Context / verdict (today, with citations)

- `pycsl_div`/`pycsl_mod` are SOUNDLY defined as `= div x y` / `= mod x y` over `int.EuclideanDivision`
  with `ensures { result = div x y }` (preamble.py:1979–1997). The *definitions* are fine.
- The hole is downstream: a VC whose hypotheses contain **nonlinear** div/mod terms (e.g. `div (a*b) c`,
  `mod (i*n) k`, a quotient multiplied back) drives Alt-Ergo/Z3 into their INCOMPLETE nonlinear-arithmetic
  fragment, where the div axioms + nonlinear multiplication can be combined into a CONTRADICTION. Once the
  hypotheses are inconsistent, `ensures { anything }` — including a FALSE one — discharges.
- Detection exists but is OPT-IN: `--check-vacuity` → `_run_vacuity_gate` (pycsl.py:836), gated only when
  the user passes the flag (pycsl.py:1158). So the default `[+] Verification SUCCESS` does NOT probe for
  vacuity — the hole is silent by default.
- Detection is unreliable if done wrong: a **false postcondition** probe catches it, but an in-BODY
  `assert { false }` is position-unreliable (the solver may discharge it from the local context
  regardless). The gate must probe the FUNCTION-LEVEL `ensures { false }`.

**Verdict.** (T1) Make the `ensures { false }` non-vacuity probe a HARD DEFAULT gate — a function that can
prove `false` is REJECTED, not reported success. This *closes the hole immediately and soundly* (no more
silent false-green), at the cost of flagging the currently-vacuous functions. (T2) Then root-cause each
flagged nonlinear-div VC and make it genuinely non-vacuous.

---

## 2. Gate B — reproduce the hole FIRST (hand-write `.mlw`)

Prove the vacuity is real and that the function-level `ensures false` probe catches it while an in-body
assert may not:

```whyml
module DivVac
  use int.Int use int.ComputerDivision
  (* a nonlinear-div hypothesis that solvers can turn inconsistent *)
  let f (a b c: int) : int
    requires { c <> 0 }
    requires { a * b = c * (div (a*b) c) + mod (a*b) c }   (* a TRUE fact, but nonlinear *)
    ensures  { false }                                     (* MUST NOT prove — if it does, vacuous *)
  = a
end
```
- Run Alt-Ergo AND Z3, timed. If `ensures { false }` proves (Valid) → the hole is reproduced; if it
  times out, escalate the nonlinear hypotheses until it does (mirror the real corpus VCs). Record the
  minimal reproducer.
- Confirm the DIAGNOSTIC discipline: the same `ensures false` at function level is the reliable probe;
  an inner `assert { false }` can be discharged from a narrower context — DO NOT use it as the gate.
- Decide the gate's prover budget/timelimit (default 5s, pycsl.py:277) so the probe is cheap but catches
  the real cases; a vacuity that only shows at long timelimits still must be caught (raise the probe TL).

---

## 3. Stages

**S0 — reproduce ✅ DONE.** Confirmed the `ROOT-CAUSE.md` finding: the vacuity is real (SMT-level
instability in nonlinear int-division reasoning; the div *definitions* `pycsl_div = div x y` are sound).
The reliable probe is the FUNCTION-LEVEL injected `ensures false` (a body `assert false` is
position-unreliable) — the existing `_run_vacuity_gate` already uses exactly this (split_vc, per
normal-exit path, ALL-exits criterion). Reproducers live in `getting-better/csys-vacuity-investigation/`.

**T1 · S1 — default the non-vacuity gate ✅ DONE.** `--check-vacuity` is now `default=True`
(pycsl.py:262) with a `--no-check-vacuity` opt-out (pycsl.py:279). Every successful verification runs
`_run_vacuity_gate`; a function that proves `ensures false` on EVERY normal exit → run FAILS.
**Latent-bug fix:** the NoReturn/`\diverges` exemption in `_gate_vacuity_then_succeed` referenced
`ir_data`, which is out of scope there (the gate runs in `_run_proofs`, not `_run_pipeline`) — the
`NameError` was swallowed, so the skip-set was ALWAYS empty and NO exemption ever applied. Fixed by
computing the exempt-set in `_run_pipeline` (where the IR lives) and stashing it on `args._vacuity_exempt`.
Exempt = declared `-> NoReturn` (is_noreturn) **and** `#@ \diverges` (func `diverges` flag) — both are
soundly vacuous-looking on their unreachable normal exit. Validated: inconsistent context → FAIL;
0051/0158/0159 (`\diverges`) → SUCCESS; 0738 (NoReturn) → SUCCESS; sound fn → SUCCESS;
`--no-check-vacuity` restores old behavior.

**T1 · S2 — corpus triage ✅ DONE (pycsl-reference).** Full 707-file pycsl-reference sweep under the
default gate: the ONLY functions flagged were the three `\diverges` tests (0051/0158/0159) — all now
EXEMPT (sound divergence, not vacuity). **Zero genuine vacuities** remained in pycsl-reference, so no
T2 root-causing is needed for that corpus (the merge-collapse fix, `merge_collapse_false_green`, had
already closed the observed os/csys case). T2 remains available if a future corpus surfaces a real
nonlinear-div vacuity.

**T2 · S3 — root-cause each nonlinear-div vacuity.** For each (a): isolate the offending VC and its
nonlinear div/mod terms. Fix by, in order of preference:
1. **Linearize the emission** — avoid generating `div (a*b) c` in a VC where a linear form suffices
   (introduce a fresh `q` with `q*c <= a*b < (q+1)*c` explicit bounds instead of the raw `div` of a
   product). The emitter, not the solver, supplies the algebra.
2. **Cite a proven lemma** (the 0342-gcd cross-validation template, `pycsl --audit-proof`): replace the
   fact the solver mis-handles with a small, individually-PROVEN Rocq/Lean lemma (`#@ proof`), added to
   `proof_axiom_allowlist` with `cite:` — an HONEST lemma, not an `Admitted`/tautology.
3. **Guard the term** — if a nonlinear div only appears under a provable side-condition, emit the
   condition so the solver's context stays consistent.

**T2 · S4 — regression-lock ✅ DONE (with a finding).** `0752.py` is the deterministic gate self-test
(inconsistent context → the default gate FAILs it; `--no-check-vacuity` PASSes it). **Finding:** the
SPECIFIC nonlinear-div vacuity NO LONGER REPRODUCES on the current toolchain — a minimal driver
accumulating the ROOT-CAUSE facts (disjunctive-or + `((mx-mn)*1000)//mx` + `(num*1000)//(6*diff)`) does
NOT prove its false postcondition (SMT correctly fails/times out, not vacuous). Consistent with the
0-vacuity full sweep and `merge_collapse_false_green` (the observed os/csys case was the best-of-N merge
bug, since fixed — not nonlinear div). So a nonlinear-div-SPECIFIC `# pycsl-expected: FAIL` driver would
be fragile/solver-version-dependent and slow; `0752` (trigger-agnostic — the gate catches ANY vacuity) is
the honest lock. No positive/negative pair per fixed vacuity is needed (0 vacuities were fixed).

**Item-2 acceptance (official battery, 2026-07-03):** `bin/run-reference-tests.sh --pycsl` under the
default gate → **705/708 pass, ~814s (~13.5 min, gate ≈2–3× the ~5-min gate-off baseline)**. The 3
CONFIRMED FAILs (0540/0700/0701) are PRE-EXISTING — each fails/times-out identically under
`--no-check-vacuity` (0700 a proof failure, 0540/0701 don't complete in 300s gate-off). **ZERO
vacuity-gate failures** across the whole battery (no `VACUOUS` hit). The stale front-end IR-conformance
pre-flight (goldens `ir_version 1.2` vs derived `1.4`) is a separate pre-existing issue, skipped with
`PYCSL_SKIP_CONFORMANCE_CHECK=1`.

**S5 — unblock csys de-trust ⏳ IN PROGRESS (reframed).** With the default gate, de-trusting is now SAFE
to attempt: a vacuous "proof" is CAUGHT, not silently accepted. **Correction (crucial):** the csys
`\trusted: SMT-timeout-deep-branch` functions (`rgb_to_hsv`/`rgb_to_hls`/…) are NOT "unprovable" — by the
**Curry-Howard isomorphism**, any true goal has a proof term and Rocq/Lean (complete for the logic) can
ALWAYS construct it. SMT-timeout is a **Rocq/Lean proof OBLIGATION**, never a terminal trust state (see
memory `smt_timeout_not_unprovable`). So the de-trust IS achievable — the honest path is `#@ proof
rocq|lean` (the `0342`-gcd cross-validation template) discharging the deep-branch goals SMT times out on.
✅ **`rgb_to_hsv` + `rgb_to_hls` DE-TRUSTED (2026-07-04)** — csys `\trusted` 4 → 2. The two nonlinear-div bounds SMT
times out on are stated as WhyML axioms `Pycsl.Csys.Colorsys.{sat_bound,hue_bound}` (preamble.py
`_AXIOM_REGISTRY`), proven in BOTH Rocq (`__init__.proofs/rocq/Colorsys.v`, `coqc` exit 0) and Lean
(`.../lean/Colorsys.lean`, core Lean 4 no-Mathlib, `lean` exit 0) — no Admitted/Axiom/sorry. Key
technique: prove each axiom on an ISOLATED leaf helper (`_hsv_saturation` gains `≤ 1000`; new
`_hue_offset` bounds the hue division) so `rgb_to_hsv`'s VC stays LINEAR (the monolithic deep-branch VC
OOM'd otherwise); plus a targeted `(r==g==b) ⟹ result==r` ensures on `_rgb_max`/`_rgb_min` (avoids the
disjunctive-or explosion) and two guiding `#@ assert`s for the h-range. `pycsl --audit-proof` passes all
4 citations; the FULL csys library verifies under the DEFAULT non-vacuity gate (genuinely non-vacuous).
The mechanism is recorded in memory `cited_proof_mechanism`.
`rgb_to_hls` reused the SAME (already-proven) `hue_bound` axiom (no new proof) via `_hue_offset`, its
lightness `l=(mx+mn)//2` being constant-divisor (SMT-direct) and `s` from `_hls_saturation`. De-trusting
it also EXPOSED + FIXED a latent contract bug hidden by trusting: the gray-case ensures named
`result[1]==0` (lightness), but HLS gray is `(0, l, 0)` — it is `result[0]` (hue) and `result[2]`
(saturation) that are 0; `l` is the gray value (Python `colorsys.rgb_to_hls(k,k,k)==(0,k,0)`).

✅ **`hls_to_rgb` + `hsv_to_rgb` DE-TRUSTED → csys `\trusted` count is now ZERO (fully de-trusted).**
These need NO new axiom: every output channel is CLAMPED to `[0,1000]` before return, so the range VC is
trivial once the nonlinear sector arithmetic (`m2`, the interpolations, `q`/`t`) is isolated behind
OPAQUE `ensures True` leaf helpers (`_hls_m2`, `_hls_channel`, `_hsv_channel`) — the honest boundary
that keeps the nonlinear terms out of the deep-branch caller VC (bodies verified pure/total; the caller
proves its range from the clamps, independent of the returned value). Full-file proof SUCCESS (all 15
contracts); `pycsl --audit-proof` 4/4; each function passes the default gate; genuinely non-vacuous.
**Whole csys library: 0 `\trusted`, 2 cross-validated cited axioms (Rocq+Lean), all contracts proven.**

---

## 4. Critical files
- `src/pycsl/pycsl.py` — default-on `--check-vacuity`, `_run_vacuity_gate` (836), the SUCCESS path
  (`_gate_vacuity_then_succeed`, 1155), the `--no-check-vacuity` escape, probe timelimit.
- `src/pycsl/module6_whyml/preamble.py` — `pycsl_div`/`pycsl_mod` + any nonlinear-div lemma emission;
  the linearized-quotient helper (S3.1).
- `src/pycsl/ir_schema.py` — the NR1/NR4 deliberate-`ensures false` exemption (do not flag those).
- Rocq/Lean proof dirs + `proof_axiom_allowlist` — the cited div lemmas (S3.2).

## 5. Out-of-scope / soundness
- **No unsound axiom** — never "fix" a vacuity by adding a div fact the solver couldn't derive unless it
  is an honestly-PROVEN cited lemma (audited). A false or `Admitted` lemma would deepen the hole.
- **The gate is the floor, not the fix** — T1 makes the hole non-silent (sound: it can no longer certify
  wrong code); T2 makes the corpus actually non-vacuous. Ship T1 FIRST (it's the safety-critical part).
- Genuine contract contradictions found by the gate (class (b)) are real bugs — fix them, don't exempt.
- Related but separate: the best-of-N merge vacuity (already fixed, `merge_collapse_false_green`); reuse
  its false-postcondition detection discipline here.

## 6. Gates
1. **The whole corpus passes the DEFAULT non-vacuity gate** — no non-exempt function proves `ensures
   false`. This is the primary acceptance criterion.
2. Full-corpus proof sweep still green under the gate (previously-honest functions unaffected; previously-
   vacuous ones now FAIL until fixed, then prove the REAL property).
3. `proof_axiom_allowlist` grows ONLY by cited, audited div lemmas (`pycsl --audit-proof`).
4. The minimal reproducer + every corpus reproducer locked by a `# pycsl-expected: FAIL` negative driver.
5. csys de-trust re-attempt succeeds (the downstream unblock).

## 7. Reference corpus
- The minimal nonlinear-div vacuity reproducer as a `# pycsl-expected: FAIL` driver (asserts `ensures
  false` provable-today → must FAIL after the gate).
- One negative + one positive driver per corpus vacuity fixed in T2·S3 (false claim fails; real property
  proves).
- A gate self-test: a deliberately-vacuous function that the default gate MUST reject.
- Update annotations.md + traceability; document the div-vacuity UB rule + the default-gate behavior in
  the static-semantics reference.

**Expected outcome:** the silent false-green from nonlinear int division is CLOSED by default (T1 — the
safety-critical soundness fix, shippable immediately), and the corpus is made genuinely non-vacuous by
linearizing/citing the offending div terms (T2), unblocking the csys de-trust. The tool can no longer
certify wrong code via a div-induced inconsistency.
