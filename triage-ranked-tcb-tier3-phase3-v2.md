# triage-ranked-tcb-tier3-phase3-v2.md — corrected tier-3 forward plan (post independent review)

**Supersedes §4 of `triage-ranked-tcb-tier3-phase3.md`.** Written from three inputs: the certified
foundation (independently verified), the adversarial review (`getting-better/tier3/plan-review.md`,
summarized in phase3 §7), and the plain-English Phase-3↔formal-proof link
(`triage-ranked-tcb-tier3-phase3-step-back.md`). Date 2026-07-06. Branch `ghost-assign-bc6`, green,
`\trusted` count **1249**.

---

## 0. What is SETTLED (do not re-litigate)

Independently reproduced by the reviewer — treat as fact:
- **The foundation is certified.** Rocq `make` green + `Print Assumptions` = base axioms only (no 4th);
  Lean `lake build` 39/39 + `#print axioms` = the 3-axiom ledger (no `sorryAx`); Phase2b all-`Qed.`;
  the Phase-0 spike discharges on both provers with false-twins unproven; conformance 38/38.
- **The de-risking is real:** ADT self-verification is *feasible* and *sound*, and it costs **zero new
  trust** (ledger stays at 3). That is genuine, durable value — the hard research question is answered.
- **But: 0 ADT-enabled `\trusted` conversions so far.** The count moved 1252→1249 only on 3 incidental
  non-ADT string leaves. The *marker payoff* has not started.

This plan is only about the **remaining marker payoff** — the foundation itself needs no more work.

---

## 1. The CORRECTED diagnosis — why the payoff is harder than v1 assumed

v1 assumed the blocking axis was **node kind** (so "add the list kinds" would free the `ir_scanner`
cluster). The review proved the real axis is **reflection STYLE**. Every IR-reading emitter stub is one
of:

| class | how it reads IR | ADT-addressable? |
|---|---|---|
| **Typed-node reader** | dispatches on `ir.get("type")`, projects named fields (`.get("left")`) | **YES** — this is the ADT's target. Split by node family: **expr = done**; stmt, contract = not yet. |
| **Generic-Any-tree walker** | `for v in obj.values()` / index over an untyped `Dict[str,Any]` with no type dispatch | **NO** — a typed WhyML variant has no `.values()`. Unreachable without rewriting live source. A genuinely *unsolved modeling problem*, a **leave-trusted candidate**. |

Concretely, the 34-stub `ir_scanner` cluster v1 called "the payoff" splits into **~10 generic-Any
walkers (not ADT-addressable)** + **~22 structured scanners that need the STMT-node ADT**, not the
expr list-kinds v1 was about to build. **The list-kinds increment would have freed neither.**

**Consequence:** the ADT can only ever reach the *typed-node readers*. A real fraction of the frontier
is generic-Any reflection that the ADT cannot model — that fraction belongs in "leave-trusted," not
"convert-later."

---

## 2. The CORRECTED method — whole-body feasibility, always (the process fix)

v1 over-projected **twice** by measuring an idiom *in isolation* (a scratchpad probe), then finding the
whole handler doesn't discharge. **New inviolable rule:**

> Every feasibility or triage claim is a **whole-body verbatim port + FULL Why3 proof** (`--fun` per
> recursive function). No idiom-in-isolation probes. A stub counts as "convertible" only when its
> entire real body discharges — never on the strength of one reflection line lowering.

This single rule is the most important change from v1.

---

## 3. The CORRECTED coupling understanding (from the step-back)

v1 claimed "list projections are covered by the conservative `path_get` certificate — no Phase-3
needed." **That was wrong**, and the correction matters:

- The conservative certificate (`Phase2b_RecordVal`, `RecordVal.lean`) certifies **scalar nested-record
  field reads** (`path_get` read-back + frame). It is a **side-car** next to the core `val` (no `VRec`
  in the core inductive) — which is *precisely why the ledger held*.
- It does **NOT** cover: (a) the **value soundness of a list-of-sub-nodes** projection, nor (b)
  `size_list` **termination**.
- **Two DISTINCT obligations must never be conflated** for any ADT increment:
  1. **VALUE soundness** (does reading a field return the right value?) → this is the **coupling** →
     needs a co-landing **certificate lemma** in `src/formal-semantics/`.
  2. **TERMINATION** (does the recursion halt?) → a **Why3-intrinsic VC** discharged by a `variant`
     measure → NOT a certificate/axiom concern.
- Therefore a **list-kinds increment is NOT coupling-free**: it needs a small **co-landing Phase-3
  lemma** — "reading the i-th sub-node of a list-of-sub-nodes value reads back correctly" (a list
  analog of `path_get`, still axiom-free, still a side-car). Its `size_list` termination is a separate
  Why3 VC. v1 skipped the lemma; v2 reinstates it per the inviolable coupling rule.

*(In step-back terms: adding "a value that is a list of nodes" is a new kind of value — so the
inspector must certify it, just like nested records were certified in Phase 3.)*

---

## 4. The RE-SCOPED plan — DATA before BUILD

### Step A — the whole-body feasibility CENSUS (cheap, decisive, do this FIRST)
No `src/` edits. A harness that, for **every** IR-reading Module-6-core stub (`expressions.py`,
`statements.py`, `functions.py`, `ir_scanner.py`, `types.py`, …): splices the LIVE body into the mirror,
full-proves (`--fun`), reverts, and records one classification:
`{convertible-NOW | needs-list-kinds | needs-stmt-ADT | needs-contract-ADT | generic-Any-UNMODELLABLE |
other-blocker:<X>}`.
**Output:** the REAL convertible count per class — replacing every v1 projection with measured data.
This is the gate for whether Step B is worth doing at all.

### Step B — build ONLY what the census proves out (each with its coupling lemma)
For each ADT extension the census shows *whole bodies* actually convert (candidates: list-kinds,
stmt-node ADT, contract-node ADT): build it **with its co-landing Phase-3 certificate lemma** (§3
obligation 1) + a `variant` measure (obligation 2), gated by the full per-increment battery (spike both
provers/no axiom; reference locks; byte-diff 0; conformance 38/38; **whole-body** feasibility per §2).
Do NOT build an extension the census does not show converting real bodies.

### Step C — convert the freed cluster (Phase-2 sweep)
Streamlined SL gate (per-function proof, mirror-only, count strictly down). **Yield is measured by real
count drop, never a projection.**

### Step D — the generic-Any walkers: a leave-trusted soundness analysis
Give the ~10 generic-Any-tree walkers (and any other UNMODELLABLE class) the Phase-4 treatment: a
rigorous false-verifies-vs-fail-stop analysis (they are almost certainly fail-stop, not
false-verifying) → document leave-trusted with the residual-gap statement.

---

## 5. The DECISION (honest, given yields 8 / 0 / 0)

Two rational paths:

- **PATH 1 — bank the certified foundation and STOP marker conversions (recommended default).** The
  durable value is the *certified feasibility*; the review shows the marker payoff is smaller, harder,
  and partly unmodellable. Declare the foundation the deliverable; stop the grind.
- **PATH 2 — proceed, but CENSUS-FIRST.** Run Step A (cheap, no build). Continue to Step B **only if**
  the census shows a genuinely large convertible-typed-reader set that justifies the multi-session,
  co-landing-lemma cost. **Never build another ADT increment on a projection.**

**Recommendation:** PATH 1, unless the Step-A census (which is cheap and worth running regardless)
returns a convertible count large enough to change the calculus. The one thing v2 forbids is repeating
v1's error — building an expensive ADT extension on a projected yield.

---

## 6. Exit criteria

- **Under PATH 1:** foundation committed + green (already true); this v2 doc + the review recorded;
  marker campaign explicitly closed with the yield history (8/0/0) and the leave-trusted rationale.
- **Under PATH 2:** the Step-A census committed as data; each Step-B increment lands its ADT extension
  **and** its co-landing certificate lemma (ledger provably still at 3 via `Print Assumptions`/`#print
  axioms`); each Step-C conversion is a measured count drop with whole-body proof; the generic-Any class
  is leave-trusted-documented (Step D). "Done" = the *typed-reader* Module-6-core stubs are converted or
  classified, and the count sits at the honest floor (typed-reader-converted + generic-Any-trusted +
  the 4 irreducible floor stubs).

---

## 7. Risk register (the review's findings, as forward risks)

| risk (from review) | mitigation in v2 |
|---|---|
| feasibility-in-isolation over-projects (happened twice) | §2 whole-body-proof rule; §4 Step-A census |
| "Step X unblocks cluster Y" asserted, not measured | §4 census-before-build; never build on a projection |
| coupling under-claimed (list reads not certified by `path_get`) | §3 co-landing lemma required for each new value shape; termination separated from soundness |
| generic-Any reflection treated as "volume" | §1 reclassified as unmodellable → §4 Step-D leave-trusted |
| opportunity cost (8/0/0 yields) ignored | §5 PATH-1 default; PATH-2 gated on census data |
| conservative certificate mistaken for deep integration | §0/§3 state it's a side-car; deep `VRec` integration only if a future step needs a shape the side-car can't cover |
