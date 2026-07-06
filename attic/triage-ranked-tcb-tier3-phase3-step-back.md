# How tier-3 Phase 3 links to the formal proof in `src/formal-semantics/` — in plain English

A step-back explanation, no math background assumed.

---

## The 30-second version

`src/formal-semantics/` is a **mathematical proof, machine-checked by two independent theorem provers
(Rocq and Lean), that PyCSL's verification method is trustworthy** — i.e. when PyCSL puts a green
checkmark on a program, the program really does what its contract says.

Tier-3 wants PyCSL to **verify its own emitter code**. To do that, the emitter's internal data (the
"IR nodes" — little nested records like `{type: "BinOp", left: …, right: …}`) has to be given a proper
mathematical type inside the verifier. That's a **new kind of value** the verifier didn't use before.

**Phase 3 is the step that goes to the formal proof and gets that new kind of value blessed** — it
proves the new nested-record values are mathematically well-behaved, in both Rocq and Lean, *without
weakening the existing trust*. Only after that blessing is the emitter allowed to use them. That's the
whole link: **Phase 1 builds the new capability; Phase 3 gets the formal proof to certify it's sound.**

---

## 1. What is `src/formal-semantics/`?

Think of PyCSL as a machine that reads a Python program + its contract and stamps it "correct" or
"not correct." A fair question is: **why should you believe the stamp?** Maybe the machine's *method*
of checking is itself flawed.

`src/formal-semantics/` answers that question with a **proof**. It writes down, in precise
mathematics:
- **What running the program actually means** (called the "operational semantics" — a rulebook for how
  a Python statement changes memory, step by step).
- **What PyCSL's checking method computes** (called the "weakest-precondition calculus," or WP — the
  logic PyCSL uses to turn a program+contract into math problems for the SMT solver).

Then it **proves these two agree**: *if PyCSL's WP method says "correct," then the program really is
correct when you run it.* This proof is checked twice, by two different, independent proof-checkers
(Rocq and Lean), so you don't have to trust one tool.

## 2. The "3-axiom trust ledger" — what PyCSL still asks you to take on faith

No proof is built from nothing; it rests on a few starting assumptions ("axioms"). The remarkable
thing about this one is that it rests on **exactly three**, all clearly named:
1. the SMT solver (Alt-Ergo / Z3) is correct when it says "proved,"
2. a contract you explicitly marked `\trusted` really holds,
3. Why3 (the tool PyCSL emits to) correctly does its job.

Everything else is *proven*, not assumed. Keeping this list at **exactly three** is the crown jewel.
Any change that would add a 4th item is a big deal — it means PyCSL now asks you to trust one more
thing. **A core rule of the whole tier-3 effort is: never add a 4th axiom.**

## 3. Why does tier-3 have to touch the formal proof at all?

Tier-3's goal is to make PyCSL **verify its own emitter** (PyCSL checking PyCSL — "eating its own dog
food"). The emitter's code constantly inspects little tree-shaped data structures — an expression node
like `BinOp` that *contains* a left child and a right child, each of which is itself a node.

To verify code that reads `node.left`, the verifier needs a **type for "a node that contains other
nodes"** — a *nested record*. The verifier's existing repertoire of value types (integers, arrays,
simple maps) didn't include this "record that holds sub-records" shape.

Here's the catch, and it's the heart of the link:

> If the emitter starts using a new kind of value (nested records), but the **soundness proof** in
> `src/formal-semantics/` doesn't cover that new kind of value, then PyCSL would be verifying its own
> code using a tool the trustworthiness proof says nothing about. You'd have **capability that
> outruns its certificate** — a green checkmark you can't actually justify.

This is called the **coupling rule** in the plan: *the new emitter capability (Phase 1) and the proof
that it's sound (Phase 3) must arrive together — neither ships alone.* Phase 3 exists precisely to keep
the emitter honest.

## 4. What Phase 3 actually did

Phase 3 added **one new file to each prover** — `Phase2b_RecordVal.v` (Rocq) and `RecordVal.lean`
(Lean) — that:
1. **Defines the new nested-record value** (called `val7`): a value that can be a number, an array, or
   a *record* — a labelled bag of sub-values, which can themselves be records, and so on (nesting).
2. **Proves the two facts that matter for reading tree data:**
   - **Read-back:** if you set field `a.b.c` to some value and then read `a.b.c`, you get that value
     back. (Sounds obvious; in a proof, "obvious" still has to be demonstrated.)
   - **Frame (no cross-talk):** setting `a.b.c` does **not** disturb `a.b.d`. Reading a different field
     still gives its old value.
3. **Proves it changes nothing for existing programs** ("conservative"): a program that never uses a
   nested record behaves exactly as before. The big existing soundness theorem still holds, untouched.

## 5. The two guarantees Phase 3 had to hit (and did)

These are the "make-or-break" checks — the reason we can call the result *certified* rather than just
*plausible*:

- **No new trust.** After adding the new value, both provers were asked "list every assumption this
  proof depends on" (`Print Assumptions` in Rocq, `#print axioms` in Lean). The answer came back
  **byte-identical to before** — still the same three axioms, no fourth, no hidden "trust me" (`sorry`)
  gap. So the new capability cost **zero** extra trust.
- **Nothing broke.** The central soundness theorem (`pycsl_soundness` / `pycslSoundnessVerified`)
  re-proved with **no changes and no gaps** ("0 Admitted / 0 sorry"). The extension sits alongside the
  existing proof rather than reopening it.

## 6. "Conservative" now vs. "deep" later — in plain terms

Phase 3 did the **conservative** version: it added the new value type *next to* the language and proved
its key properties, which is enough to justify the specific reads the emitter does today (reading a
field out of a node).

The **deep** version — actually rewiring the new value type into the very core definition of "a PyCSL
value" and re-running the entire step-by-step soundness argument for all 22 kinds of statement — was
**deliberately not done**, because (a) it's a large, cascading change, and (b) it isn't needed for what
the emitter reads. If a future step ever needs a value shape the conservative version doesn't cover,
*that* is when the deep version gets pulled in — and only then.

## 7. One analogy to tie it together

Imagine the formal proof is a **safety inspector** who has certified that a factory's entire assembly
line is safe. Tier-3 wants to add a **new machine** to the line (the emitter's nested-record handling).

- **Phase 1** builds and installs the new machine.
- **Phase 3** is calling the inspector back to **certify the new machine is safe** — *before* you run
  production through it.
- The **coupling rule** is the factory policy: "no uncertified machine goes live."
- **"No 4th axiom"** is the inspector certifying it **without lowering the safety standard** — the
  factory is exactly as safe as before, just with one more certified machine.

## 8. Why this matters — what would go wrong without the link

If we skipped Phase 3 and just let the emitter use nested records (Phase 1 alone):
- PyCSL might stamp its own emitter "verified" — but that stamp would rely on a value type the
  soundness proof never vouches for. A subtle bug in how nested records behave could let a *false*
  claim slip through, and the formal guarantee ("green checkmark ⇒ really correct") would quietly no
  longer apply to the emitter.
- With Phase 3 done, the guarantee **does** still apply: the emitter's self-verification is backed by
  the same two-prover, three-axiom proof that backs everything else. That is exactly what "certified"
  means here, and it's why the tier-3 foundation can honestly be called *de-risked*.

---

**In one sentence:** `src/formal-semantics/` is the machine-checked promise that "PyCSL's checkmark is
trustworthy," and Phase 3 is the work that **extends that promise to cover the new nested-record values
the emitter needs — proven in both Rocq and Lean, adding no new trust and breaking nothing** — so that
when PyCSL verifies its own emitter, the promise still holds.
