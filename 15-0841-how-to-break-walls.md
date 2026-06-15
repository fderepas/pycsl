# How to break walls: discovering a structural limit, and the strategy shift it forced

*A reflective report on a multi-attempt verification effort (2026-06-15). Self-contained: all
project-specific terms are explained inline.*

---

## 0. Why this report exists

Over several attempts to finish one proof, three reasonable-looking fixes all failed in the *same*
way. The valuable outcome was not a fix but a **diagnosis**: the obstacle was not a missing fact, it
was a *structural* property of the tool. Recognizing that flipped the strategy from "find the right
lemma" to "change how the tool is fed." This report records how that recognition happened and the
general method it suggests, because the pattern recurs.

## 1. Just enough background to follow the story

**The system.** PyCSL is a deductive verifier: it translates annotated Python into an intermediate
mathematical language (WhyML), from which the Why3 platform generates *verification conditions* (VCs)
— logical formulas that are true iff the code meets its contract — and discharges them with automated
SMT solvers (Alt-Ergo, Z3). A solver proves a VC by showing its negation is unsatisfiable.

**The target.** We model a Unix filesystem in Python and verify it. The directory lives in a fixed
disk region of 16 "slots"; each slot decodes to an inode number (`slot_inode`) and a name
(`slot_name`). A key invariant, `uniq`, says no two *live* slots share a name. Removing a file
(`unlink`/`rmdir`/`rename`) zeroes the target slot, then must prove the **absence** property:

> after removal, no *other* slot still carries the removed name.

This absence is the obligation the rest of the proof consumes to conclude "the name is gone."

**How solvers use facts: triggers and E-matching.** Universally-quantified facts (axioms) are not
applied blindly — that would be infinite. Instead each quantified axiom carries a *trigger*: a
syntactic pattern. The solver instantiates the axiom only when a term matching the trigger appears in
the proof context. This matching process is called **E-matching**. Its danger: if a trigger matches
*many* terms, the solver generates a flood of instantiations — which generate yet more matching terms
— and the search explodes (millions of steps, then timeout or out-of-memory). A single badly-scoped
quantified axiom in a term-rich context can sink an otherwise-trivial goal.

**The relevant axioms.** `uniq` is an *abstract predicate* fixed by two definitional axioms:
- `uniq_intro`: from "no duplicate live names" you may conclude `uniq d` (used to *establish* the
  invariant);
- `uniq_elim`: from `uniq d` you may conclude "no duplicate live names" — specifically the quantified
  body `∀ i, j. (i and j both live with the same name) → i = j` (used to *consume* the invariant).

A second invariant `slots_lt32` (every slot's inode number is in range) has the same intro/elim
shape. Both elims are emitted **module-globally** and triggered on the predicate atom (`uniq d`),
which appears almost everywhere because it is a class invariant.

**The two roles of the same axiom.** `uniq_elim` is needed for **maintenance**: when code mutates the
disk, it must re-prove `uniq` holds afterward, which requires unfolding the old `uniq` (elim) and
refolding the new one (intro). But `uniq_elim` is *also* what the **absence** proof would use — and
its body is the `∀ i, j` form that E-matches combinatorially over the 16 slots.

## 2. The wall, met three times

The absence proof failed for `unlink`/`rename` (timeout / out-of-memory at 6–13 million solver
steps) but *succeeded* for `rmdir`. The only structural difference: `unlink`/`rename` have a loop
(freeing the file's blocks) that accumulates many slot-related terms across several disk versions,
whereas `rmdir`'s body is lean. That clue — *same logic, fails only in the term-rich body* — was the
first hint the problem was about *search*, not *truth*. Three attempts followed.

**Attempt 1 — supply the missing frame.** Hypothesis: the remover's helper drops the "other slots
unchanged" frame at its boundary, so the absence is unprovable for lack of a fact. We restored the
frame. Result: it helped the simple removers but, exposed broadly, its trigger fired on every slot
access and *poisoned* unrelated goals (array-bounds checks blew up). Lesson: the fact was real, but
*delivering* a quantified fact has a cost — the trigger is a global side-effect.

**Attempt 2 — supply the uniqueness consequence as a lemma (`uniq_absent`).** Hypothesis: the solver
can't derive the absence from raw `uniq_elim` (the `∀ i, j` explosion), so give it the *specialized*
consequence directly, applied in one step. Result: it proved the *pre-removal* absence — genuine
progress — but the *post-removal* version still exploded, and the new always-emitted axiom *regressed*
a sibling syscall via its own trigger noise. Lesson: a correct, more-direct lemma did not stop the
explosion, because the explosive `uniq_elim` was *still in scope* and the solver still explored it.

**Attempt 3 — the combined removal lemma (`remove_unique_absent`).** Hypothesis: fold the whole
removal — uniqueness + the zeroing frame → absence — into one axiom the solver applies in O(1), with
a tight two-pattern trigger so it fires exactly once. We built it; it is mathematically correct (a
first-order consequence of the existing definitional axioms, hence zero new trust). Result: the
absence *still* timed out at ~7 million steps, *with the correct O(1) lemma sitting right there in
scope*, and it *again* regressed the sibling syscall via added noise. 

Three different fixes; one identical failure mode.

## 3. The recognition: "missing fact" vs "structural wall"

The decisive reframing was to stop asking *"what fact is missing?"* and ask *"why does supplying the
fact not help?"* The answer:

> The solver was not failing for lack of the absence fact. It was failing because the **explosive
> `uniq_elim` is unavoidably in scope** — the surrounding code *needs* it for invariant maintenance —
> and the solver explores its combinatorial `∀ i, j` instantiations regardless of any O(1) lemma also
> present. A correct lemma cannot win a race it is not allowed to skip.

And the reason it *must* stay in scope is the tool's emission model: **axioms are module-global; there
is no per-goal (or per-sub-goal) scoping.** The maintenance obligation and the absence obligation are
different sub-goals of the same function, but every axiom is visible to *both*. You cannot say "use
`uniq_elim` for the maintenance sub-goal but hide it from the absence sub-goal."

This is the wall, stated precisely:

> **The wall is structural: Why3 has no per-goal axiom scoping. The absence proof needs the
> uniqueness *fact* but is poisoned by the uniqueness *elim* that must stay in scope for the loop's
> maintenance. A correct lemma can't help while the prover still explores the explosive elims.**

The three attempts were not wasted: each one *eliminated a hypothesis*. Attempt 1 showed the fact was
real (not the issue). Attempt 2 showed a direct lemma doesn't help (the explosion is independent of
having the answer). Attempt 3 showed even a perfect O(1) lemma doesn't help (confirming the explosion
is about *what else is in scope*, not the lemma). Together they triangulated from "we lack a fact" to
"we cannot lack the *noise*." A wall is only proven structural by ruling out the non-structural
explanations — and that is exactly what a sequence of honest, differently-aimed attempts does.

## 4. The strategy shift it forced

Once the obstacle is *what is in scope* rather than *what is provable*, the search space of fixes
changes completely. You stop writing lemmas and start controlling **emission** — *which* axioms the
tool puts in front of the solver for *which* code. The new plan:

> **The real fix is bigger than a lemma: remove the explosive elims from the syscalls' VC context
> while keeping them where maintenance needs them — i.e., prove the removal lemma once in a separate
> minimal theory (no surrounding code, no loop) and import it as an applied fact, or as an opaque
> externally-proven cited axiom. That is an emission change (scoped / cited axioms), not a new
> axiom.**

Concretely, this works because the explosive elims are only genuinely *needed* by the small,
lean leaf routines that mutate the disk one write at a time — where the same `∀ i, j` instantiation is
harmless (few terms, like the `rmdir` body that always succeeded). So:

- **Push the elims down** to those leaf writers (cite them only there), and have each leaf writer
  *prove and then guarantee* that it preserves the invariants.
- **The syscalls inherit** invariant maintenance from the leaf writers' guarantees, so they no longer
  need the elims at all — and with the elims gone from their context, the absence lemma, now applied
  in a quiet context, discharges in one step.

The lemma did not change. *Where the noisy axioms are visible* changed. That is the whole fix.

## 5. The general method: how to break walls

The episode distills into a repeatable discipline.

1. **A contrast is a clue.** The same logic failing in a rich context but passing in a lean one
   (`unlink` vs `rmdir`) is a signal that the problem is *search cost*, not *missing truth*. Hunt for
   such contrasts deliberately.

2. **Attempt to *eliminate hypotheses*, not just to *succeed*.** Frame each attempt so that its
   failure teaches something. "Supply the fact," then "supply the consequence," then "supply the
   perfect O(1) lemma" is a *designed sequence*: each rules out one explanation. Random variations on
   one idea teach nothing; orthogonal attempts triangulate.

3. **When fixes of escalating strength all fail identically, suspect the *environment*, not the
   artifact.** If even the ideal version of your fix (a correct, O(1), tightly-triggered lemma) does
   not move the needle, the obstacle is not the artifact you keep improving — it is the context the
   artifact lives in.

4. **Name the limit in the tool's own terms.** "It's slow" is not actionable. "Axioms are
   module-global; there is no per-goal scoping; a needed axiom is unavoidably visible to a goal it
   poisons" *is* — it directly implies the class of fixes (control scope/emission) and rules out the
   class that kept failing (write a better fact).

5. **A structural wall promotes the problem one level up.** The fix moved from the *logic* layer
   (axioms and lemmas) to the *emission* layer (which axioms are presented to which goals). Breaking a
   structural wall almost always means acting at a higher layer than the one you were fighting in.

6. **Keep the failed attempts cheap and reversible, and write down what each ruled out.** The three
   attempts were each built, measured, and reverted, with the negative result recorded. The reverts
   kept the verified baseline intact; the records turned three "failures" into one solid diagnosis and
   a specified fix. A documented dead-end is an asset.

7. **Separate "correct" from "effective."** The final lemma was *correct* long before it was
   *effective*. Conflating the two ("the lemma is right, so it should work") hides structural walls.
   Track them as independent properties: does the fact hold, *and* will the solver actually use it in
   this context?

## 6. Outcome

The proof itself is not yet closed — but the work converted an open-ended "make the prover faster"
struggle into a bounded engineering task with a written specification: re-scope two axioms from
always-present to cited-only, give the leaf writers maintenance guarantees, and deliver the removal
lemma as one applied fact in the now-quiet context. The deliverable of hitting the wall was the
*shape of the door*.
