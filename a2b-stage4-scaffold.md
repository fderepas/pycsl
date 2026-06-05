# A2b stage 4 — imported-framing-lemma prototype: validated scaffold

**Status:** scaffold / ready-to-execute (not yet built). Produced by grounding the plan
(`no-more-int-5.md` §A2b step 4; `docs/handling-aliasing.md` §3) against the *actual* implemented
machinery, so the prototype can be executed without re-discovery. **No corpus code committed** —
stage 4 is a multi-part effort (see "Why this is not a one-sitter"), and the discipline forbids a
half-working corpus driver.

## The goal (restated)
Demonstrate the novel move: a property that first-order region logic **cannot** discharge — a
*permutation / reachability* fact — is proved once in Rocq **and** Lean, cross-checked, imported as
a black-box WhyML axiom, and used to verify a Python driver. The canonical small instance:
**reversing a list preserves its multiset of elements** ("this reversal permutes exactly the cells").

## What is already implemented (verified 2026-06-05)
- **The directive:** `#@ proof rocq <FQN>` / `#@ proof lean <FQN>` (NOT `axiom_from` — that is the
  conceptual name in the docs). Worked example: `0342.py` (Euclidean GCD).
- **The registry:** `src/pycsl/module6_whyml/preamble.py::_AXIOM_REGISTRY` — a `Dict[str, str]`
  mapping each qualname to a **WhyML axiom body string**. Module6 emits each cited entry as an
  `axiom` block in the preamble. Example entry:
  ```python
  "Pycsl.Reference.Gcd.gcd_step":
      "forall a b : int. a >= 0 -> b >= 0 -> b > 0 -> gcd a b = gcd b (mod a b)",
  ```
  `gcd` here is an **uninterpreted logic symbol**; the axiom constrains it, the body uses it, the
  paired proofs justify it.
- **The proof pairing:** `NNNN.proofs/{rocq,lean}/` holds the paired theorems (0342 has
  `rocq/gcd.v` + `lean/Gcd.lean`, each a stdlib-citing proof — `no Admitted` / `no sorry`).
  Cross-validation is manual for the MVP, automated by the `proof2why3` cross-check pipeline in v1.
- **Toolchains present:** `coqc` (Coq 8.20/4.14 opam switch) and `lean`/`lake` (elan) are both on
  PATH — so the cross-check is runnable here.

## What is missing (the stage-4 work, in dependency order)

### Gap 1 — a spec surface for the framing property (PyCSL has NO `\permutation`/multiset operator)
Verified: `grep -i permut|multiset` over `Module2_Parser.py` + the static-semantics reference is
**empty**. The driver's `ensures` has no way to *state* "the result is a permutation of the input."
Options, smallest first:
- **(1a) Reuse the ghost-list surface.** `Module2_Parser` already has `NilExpr/ConsExpr/HdExpr/
  TlExpr/NthExpr/MemExpr/AppendExpr/ListLengthExpr` ghost-list nodes. Add a `PermExpr`
  (`\permutation(a, b)`) node + Module4 validation + Module5 IR + Module6 lowering to an
  **uninterpreted `predicate permut (s t : seq int)`**. This is the same shape as the existing ghost
  ops — a few hundred LOC, mechanical, low-risk.
- **(1b) Model via multiset equality** using Why3's `bag`/`Multiset` stdlib instead of a bespoke
  `permut`. Cleaner semantics but introduces a new Why3 theory import; defer unless 1a proves
  awkward.

### Gap 2 — ~~model the list as an IMMUTABLE `seq int`~~ — ✅ OBVIATED (verified 2026-06-05)
The scaffold hypothesised that a mutable `array int` "cannot participate in the pure logic of a
permutation axiom" and that a `seq int` snapshot was therefore required. **A Why3 prototype disproves
this** — the full stage-4 shape typechecks and proves Valid over `array int`:
```whyml
predicate permut (a: array int) (b: array int)
val function rev_arr (a: array int) : array int
axiom rev_is_perm : forall s: array int. permut (rev_arr s) s
goal g : forall xs: array int. permut (rev_arr xs) xs            (* Valid, alt-ergo 4 steps *)
let reverse (xs: array int) : array int
  ensures { permut result xs } = rev_arr xs                     (* Valid *)
```
The reason: in a *logic/axiom* context `array int` is just its logical model (a `length` + an
`elts: map int int`), and quantifying over it is fine. The no-aliasing restriction the A1-residual
spike hit applies only to **program** values stored in pure containers (a mutable array *inside* a
`map`), NOT to a predicate/axiom *over* arrays. So **no `seq` snapshot is needed** — Gap 1's
`\permutation` over `array int` is the right surface, and the framing lemma states directly over it.
(The one real boundary: a *logic* `function rev_arr` cannot be called in a program body — use
`val function rev_arr` so it is both program-callable and constrainable by the axiom.)

### Gap 3 — the registry entry + the WhyML symbols
Add to `_AXIOM_REGISTRY`:
```python
# Pycsl.Reference.Rev — reversal preserves the element multiset.
# Cross-validated by 0531.proofs/rocq/Rev.v + 0531.proofs/lean/Rev.lean.
"Pycsl.Reference.Rev.rev_permutation":
    "forall s : seq int. permut (rev s) s",
```
with `rev` and `permut` declared as the uninterpreted `function rev (seq int) : seq int` /
`predicate permut (seq int) (seq int)` the Gap-1 lowering introduces (mirroring how `gcd` is
declared for 0342 — see `_AXIOM_REGISTRY`'s companion "functions an axiom block needs declared"
table in `preamble.py`).

### Gap 4 — the paired proofs (these are the EASY part — stdlib one-liners)
- **Rocq** (`0531.proofs/rocq/Rev.v`), modeled on `gcd.v`:
  ```coq
  Require Import List Coq.Sorting.Permutation.
  Module Pycsl. Module Reference. Module Rev.
  Theorem rev_permutation : forall (l : list Z), Permutation (rev l) l.
  Proof. intro l. apply Permutation_rev. Qed.
  End Rev. End Reference. End Pycsl.
  ```
- **Lean** (`0531.proofs/lean/Rev.lean`), modeled on `Gcd.lean`:
  ```lean
  namespace Pycsl.Reference.Rev
  theorem rev_permutation (l : List Int) : (l.reverse).Perm l := l.reverse_perm
  end Pycsl.Reference.Rev
  ```
  Both are single stdlib citations (`Permutation_rev` / `List.reverse_perm`) — `no Admitted`,
  `no sorry`. The cross-check confirms the two statements agree (both: reverse is a permutation).

### Gap 5 — the driver (`0531.py`)
```python
"""Test 0531 — imported framing lemma: reversal is a permutation (A2b stage 4)."""
#@ proof rocq Pycsl.Reference.Rev.rev_permutation
#@ proof lean Pycsl.Reference.Rev.rev_permutation
#@ ensures \permutation(\result_seq, xs_seq)   # exact surface = Gap-1 outcome
#@ assigns \nothing
def reverse(xs: List[int]) -> List[int]:
    ...   # pure reversal building a new list
```
The driver proves its permutation postcondition **only** via the imported axiom — SMT alone cannot
derive it (no induction over the reversal). That is the whole demonstration.

## Why this is not a one-sitter (and why no code is committed yet)
Stage 4 = Gap-1 (a new ghost spec operator: parser node + Module4/5/6 plumbing) + Gap-2 (a `seq`
view of a list in a contract) + Gaps 3–5 (registry + proofs + driver). Gap 1 alone is a self-
contained feature (~the size of an existing ghost-op). The plan budgeted "1–2 weeks" for exactly
this. Attempting it end-to-end in an unattended session would risk a broken corpus driver, violating
the byte-diff/sweep discipline. The scaffold above removes all the *discovery* risk (the mechanism,
the registry format, the exact stdlib lemmas, the mutable-vs-seq decision) so the build is now a
sequence of small, individually-gated steps.

## Recommended execution order (each its own gated commit)
1. **Gap 1 — ✅ DONE (0537).** Added the `\permutation(a, b)` spec operator end-to-end
   (Module2 grammar+`Permutation` node → Module4/5 IR → Module6 `_handle_permutation_expr`),
   lowering to an **uninterpreted** `predicate permut (a b: array int)` — mirroring `\array_eq`
   but *without* unfolding (permutation is not first-order). Plumbing driver 0537
   (`requires \permutation(a,b)` ⊢ `ensures \permutation(a,b)`) flips FAIL→PASS; additive (a
   9-file representative byte-diff is identical). The **reflexivity / reversal axioms** (`#@ proof`)
   are Gaps 3–4, not Gap 1.
2. **Gap 2** — the `seq` snapshot view of a list parameter in a postcondition.
3. **Gaps 3–4** — registry entry + paired Rocq/Lean proofs; run `coqc` + `lake build` to confirm
   both compile clean.
4. **Gap 5** — the `0531.py` reversal driver; flip FAIL→PASS via the imported axiom; full sweep.
5. **Write-up** — this is the paper-worthy artifact (`docs/handling-aliasing.md` §3): the first use
   of proof-assistant-imported framing lemmas to cross the first-order reachability wall in an
   SMT-backed verifier.
