# Response to wh3question.txt

## Short verdict

The recommendation is directionally correct but needs two refinements before acting on it.

---

## What is right about it

**The logic-domain point is sound.**  
Cohen & Johnson-Freyd give a denotational interpretation of Why3 formulas as Coq
propositions.  That is exactly the codomain our WP transformer targets — `wpW ws Q`
already maps a WhyML statement and a continuation record to a `Prop` in Lean/Rocq.
If we want to prove `why3VcgSound`, we need to know what it means for a Why3 formula
to hold, and Cohen & JF provide that answer grounded in the actual Why3 implementation.
Not building on them means re-deriving the same interpretation ourselves, which is
undesirable.

**The thesis check is the right first action.**  
Cohen's May 2025 Princeton thesis ("A Foundationally Verified Intermediate Verification
Language") is the decisive data point.  If it covers a verified VCgen for the WhyML
imperative core, Task 6 becomes integration work, not greenfield work.  Reading the
thesis before writing a single line of `why3Vcg` is non-negotiable.

---

## What needs refinement

### 1. Scope mismatch: logic ≠ WhyML programs

Cohen & JF formalize **Why3's logic** (terms, formulas, types, inductive predicates).
Our Task 6 target is the **WhyML program language** and its WP transformer — a
different layer that the POPL 2024 paper explicitly leaves out.  The table in the
question correctly identifies this gap, but the "concrete recommendation" paragraph
slides over it: building on Cohen & JF gives us the formula semantics for free, but
we still have to build the WhyML big-step semantics and the WP transformer ourselves,
possibly from scratch.  The amount of work saved is real but not as large as the
recommendation implies.

### 2. Prover ecosystem friction

Cohen & JF work in Coq/Rocq.  Our primary formalization is now Lean 4
(with Rocq as a secondary mirror).  Two options, neither free:

| Option | Cost |
|--------|------|
| Use their work in Rocq only, then cross-reference from Lean 4 | The Lean 4 side still needs its own VCG proof; the Rocq proof does not help Lean directly |
| Port Cohen & JF to Lean 4 | Substantial effort; their W-type encoding of ADTs is non-trivial in Lean 4's type theory |

The friction does not make the recommendation wrong, but it does mean the
integration architecture needs to be planned explicitly rather than assumed.

### 3. Our `wpW` is already self-contained for the 13-construct subset

The current `WPW.lean` / `Phase6b_WPW.v` defines `wpW` over exactly the 13
constructors that Module6 emits.  `wpW` is already the correct semantic object —
it does not need to be re-derived from Cohen & JF's formula interpretation.
What `why3VcgSound` needs is not a new semantic domain but a proof that a boolean
decision procedure over those 13 cases implies the already-existing `wpW` predicate.
Cohen & JF help with the *postcondition* side (what a Why3 formula means), less so
with the *structural induction* over WhyML statements.

---

## Revised recommendation

### Step 1 — Read Cohen's 2025 thesis immediately (before any Task 6 code)

Specifically: does it include a verified WP/VCgen for the WhyML imperative core
(assignment, while, try-catch, assertions)?  If yes, the integration path is:

```
Cohen 2025 VCgen soundness
    ↓ restrict to 13-constructor subset
why3Vcg ws Q = true  →  Cohen_wp ws ≡ our_wpW ws  →  wpW ws Q
```

The bridge lemma (`Cohen_wp = wpW` for 13 constructs) is the residual proof
obligation, and it is likely tractable because both sides compute the same WP
by construction.

If the thesis does **not** cover VCgen, the self-contained approach is faster:
define `why3Vcg : whyml_stmt → wp_conts → Bool` directly and prove soundness
by structural induction, without any external dependency.

### Step 2 — Use Cohen & JF for formula semantics only, in Rocq

For the Rocq formalization, import `joscoh/why3-semantics` for the
`eval_formula : why3_formula → coq_prop` function.  This gives the correct
interpretation of Why3 postconditions as Coq propositions, which is needed to
state the VCG soundness theorem precisely.  Do not try to use it in Lean 4
directly — reproduce only the formula-semantics bridge lemma there.

### Step 3 — Keep `wpW` as the internal semantic interface

Do not replace `wpW` with Cohen & JF's semantic domain.  `wpW` is already proved
correct (via `wpGenCorrect`) and is the bridge between the PyCSL semantics and the
WhyML-level reasoning.  Cohen & JF's work should connect *to* `wpW`, not replace it.

---

## Summary table

| Question | Answer |
|----------|--------|
| Build on Cohen & JF at all? | Yes — for formula semantics in Rocq |
| Port to Lean 4? | No — reproduce only the bridge lemma |
| Replace `wpW`? | No — keep as is; connect Cohen & JF to it |
| First action? | Read Cohen May 2025 thesis before any Task 6 code |
| Self-contained `why3Vcg` still viable? | Yes — fallback if thesis doesn't cover VCgen |
