# Framing lemmas as `axiom_from` imports — a working demonstration

**Status:** Demonstrated (corpus-backed)
**Drivers:** `test-suite/corpus/pycsl-reference/0537.py`, `0538.py`, `0539.py`
**Position it realizes:** `docs/handling-aliasing.md` §3 (the novel move); `no-more-int-5.md` §A2b;
`a2b-stage4-scaffold.md` (the build plan).

## What this demonstrates

`docs/handling-aliasing.md` argues that PyCSL should handle the hard, non-first-order parts of
framing — the reachability/permutation facts an SMT solver cannot derive — by **proving them once in
a proof assistant and importing them as black-box axioms** (`#@ proof rocq` / `#@ proof lean`),
rather than building separation-logic machinery into the verifier. It calls this, *as far as the
literature shows, novel*: nobody has used proof-assistant-imported framing lemmas to cross the
first-order reachability wall in an SMT-backed verifier.

This document records that the mechanism is now **working and gated in the corpus**, end to end, on
the canonical example: *reversing a list is a permutation of it*. The SMT solver proves the driver's
postcondition **only** by citing a lemma proved in Rocq and Lean — it cannot derive it itself.

## The three drivers

The build went in three gated steps (each committed FAIL-first, then flipped to PASS).

### 0537 — the `\permutation` spec operator (the surface)
`\permutation(a, b)` asserts `a` is a permutation of `b`. Crucially, unlike `\array_eq` (which
PyCSL unfolds to a per-index quantified formula the SMT solver can E-match), `\permutation` lowers
to an **uninterpreted** predicate:

```whyml
predicate permut (a: array int) (b: array int)
```

There is deliberately no body and no unfolding — permutation is not first-order expressible, so the
operator is precisely the *surface a proof-assistant-imported axiom will constrain*. The plumbing
driver 0537 (`requires \permutation(a,b)` ⊢ `ensures \permutation(a,b)`) proves only because the
uninterpreted `permut a b` term is invariant under `assigns \nothing`.

### 0538 — the first imported axiom (the bridge)
0538 proves `\permutation(a, a)` via an imported reflexivity axiom:

```python
#@ proof rocq Pycsl.Reference.Perm.permut_refl
#@ proof lean Pycsl.Reference.Perm.permut_refl
#@ ensures \permutation(a, a)
def self_perm(a: List[int]) -> int: ...
```

Module 6 emits the cited axiom into the preamble — `axiom … : forall s : array int. permut s s` —
and the SMT solver discharges `permut a a` by instantiation. The axiom is **cross-validated**: the
paired proofs `0538.proofs/rocq/Perm.v` (`Permutation_refl`) and `0538.proofs/lean/Perm.lean`
(`List.Perm.refl`) both compile clean (`coqc` / `lean` exit 0), establishing the same fact in two
independent proof assistants.

### 0539 — reversal is a permutation (the headline)

```python
#@ proof rocq Pycsl.Reference.Perm.rev_permutation
#@ proof lean Pycsl.Reference.Perm.rev_permutation
#@ ensures \permutation(\result, xs)
#@ assigns \nothing
def reverse(xs: List[int]) -> List[int]:
    return list(reversed(xs))
```

`reversed(xs)` models the reversed sequence as an abstract `array_rev xs` (a `val function` — both
program-callable and constrainable by a logic axiom), and `list(·)` over an array passes through. So
the body lowers to `(array_rev xs)`, giving `result = array_rev xs`. The imported lemma

```whyml
axiom … : forall s : array int. permut (array_rev s) s
```

instantiated at `s = xs` yields `permut (array_rev xs) xs`, i.e. `permut result xs` — the
postcondition. **The SMT solver does no permutation reasoning; the lemma does all of it.** The lemma
is proved once and cross-validated:

| Prover | File | Lemma | Note |
|---|---|---|---|
| Rocq | `0539.proofs/rocq/Rev.v` | `Permutation_rev` + `Permutation_sym` | Coq states it `Permutation l (rev l)`; the axiom direction is `permut (array_rev s) s` = `Permutation (rev l) l`, hence symmetry |
| Lean | `0539.proofs/lean/Rev.lean` | `List.reverse_perm` | already `l.reverse ~ l`, the axiom direction |

Both compile clean. The Why3 axiom over `array int` is the array-model image of these list
statements.

## Why it works over `array int` (no `seq` snapshot)

The scaffold (`a2b-stage4-scaffold.md`) originally hypothesised that a mutable `array int` could not
participate in the permutation axiom — that an immutable `seq int` snapshot would be required. **A
Why3 prototype disproved this**, and the corpus drivers confirm it: the whole shape typechecks and
proves over `array int`. The reason is the program/logic distinction at the heart of
`handling-aliasing.md`:

- In a **logic / axiom** context, `array int` is just its logical model — a `length` and an
  `elts : map int int`. Quantifying over it (`forall s : array int. …`) is unrestricted.
- The no-aliasing rule that blocked **A1-residual** (`no-more-int-5.md`) applies only to **program**
  values stored in pure containers — a mutable array placed *inside* a `map`. A predicate or axiom
  *over* arrays is fine.

So **Gap 2 of the scaffold is obviated** — `\permutation` over `array int` (0537) is the right
surface, and the framing lemma states directly over it. (The one real constraint: a *logic*
`function` cannot be called in a program body, so `array_rev` is declared `val function` — both
program-callable and axiom-constrainable, the same idiom `bit_and` uses.)

## How it ties back to the position

This is the `handling-aliasing.md` §3 move, realized:

- The reachability/permutation reasoning that *cannot* be done first-order is **confined to the
  proof assistant**, where induction over list/heap shape is natural (`Permutation_rev` is a one-line
  stdlib citation).
- The **cross-check** (Rocq *and* Lean agreeing) guards the imported axiom — the *CSL family's
  distinctive `axiom_from` contribution, not a new heap logic.
- Why3's SMT path uses the lemma as a **black-box first-order axiom** and stays fully tractable.

It also shows the same mechanism is **not a one-off**: `handling-aliasing.md`'s footnote observes
that a JSON round-trip `loads(dumps(x)) == x` is the *same* shape — a proof-assistant lemma crossing
a wall SMT can't climb. The permutation demonstration is the first instance; verified serialization
(Narcissus / EverParse) would be the second, through the identical `#@ proof` path.

## Honest boundaries

- **`array_rev`/`reverse` is a trusted primitive here**, exactly as `os.open` is in `os_demo`: the
  imported lemma states *what* reversal does (it permutes), not that the Python body *is* a correct
  reversal. Proving the body computes `array_rev` (a full reverse-correctness loop proof) is a
  separate, harder obligation — out of scope for the framing demonstration and not claimed.
- The axioms are **manually cross-validated for the MVP** (the registry records the paired proof
  files; the `proof2why3` cross-check pipeline automates the statement-agreement check in v1 — see
  `docs/cross-validated-spec-sources.md`).
- This demonstrates the **mechanism**, not a general permutation theory: `permut` stays
  uninterpreted, constrained only by the cited axioms (reflexivity, reversal). Transitivity,
  symmetry-as-lemmas, `Counter`-style multiset facts, etc. are added the same way, on demand.

## Pointers
- Mechanism: `src/pycsl/module6_whyml/preamble.py` (`_AXIOM_REGISTRY`, `_AXIOM_FUNCTIONS`,
  `_emit_preamble_axioms`); `expressions.py::_handle_permutation_expr` + the `reversed`/`list`
  lowering; `Module2_Parser.py` (`\permutation` grammar + `Permutation` node).
- Proofs: `test-suite/corpus/pycsl-reference/0538.proofs/`, `0539.proofs/` (Rocq + Lean).
- Position: `docs/handling-aliasing.md`; plan: `no-more-int-5.md` §A2b; build log:
  `a2b-stage4-scaffold.md`.
