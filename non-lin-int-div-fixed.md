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

**S0 — reproduce (above)** → committed minimal `.mlw` + the "function-level ensures-false is the reliable
probe" evidence.

**T1 · S1 — default the non-vacuity gate.** Flip `--check-vacuity` to ON by default (add
`--no-check-vacuity` escape hatch for debugging). Every successful verification now ALSO runs
`_run_vacuity_gate`: for each function, replace its `ensures` with `ensures { false }` and try to prove;
if ANY prover returns Valid, the function is VACUOUS → overall result is FAIL (not SUCCESS), with a
diagnostic naming the function. Exempt only the explicitly-marked `ensures { false }` proof functions
(NR1/NR4 in `ir_schema.py:112` — the deliberate absurd-body case). This *closes the hole* on day one.

**T1 · S2 — corpus triage.** Run the now-default gate over the full corpus; enumerate every function that
proves `ensures false`. Classify each: (a) nonlinear-div-induced vacuity (the target), (b) a genuine
contradiction in the contract (a real bug to fix), (c) an intended NR1 absurd body (exempt). Record the
list — this is the T2 work-queue and the honest scope of the hole.

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

**T2 · S4 — regression-lock the reproducers.** Every fixed vacuity gets a negative reference driver
(`# pycsl-expected: FAIL` with `ensures { false }`, and a positive driver asserting the REAL property that
the previously-vacuous function should prove). These lock the fix against reintroduction.

**S5 — unblock csys de-trust.** With the corpus genuinely non-vacuous under the default gate, the csys
de-trust (blocked on this per `vacuity_nonlinear_div`) can proceed — re-attempt it as the acceptance
consumer of the fix.

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
