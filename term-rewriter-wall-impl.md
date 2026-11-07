# term-rewriter-wall-impl.md — implementation plan (the Term-rewriter wall is BREAKABLE)

*From `term-rewriter-wall.md` (report) + `term-rewriter-wall-response.md` (independent fable review).
Verdict, oracle-grounded: **BOUNDED FEATURE, not a boundary** — a `Term → Term` structural rewriter is
expressible + provable in WhyML axiom-free (the make-or-break spike `term-rewriter-spike.mlw` proves 6/6,
independently re-verified). So the wall is NOT leave-trusted. But the residual is the classic M2 gap
(target-provable ≠ emitter-generable): converting a rewriter needs the EMITTER to GENERATE that proven
shape from verbatim Python — a real multi-part emitter feature. This plan scopes it, spike-gated.*

## 0. Status of the make-or-break spike (Gate S — already PASSED)

The plan's make-or-break falsifier is `getting-better/composition-wall/term-rewriter-spike.mlw` (written by
the independent reviewer, re-proven by the driver-verifier): a `term` variant with a fixed-arity `Binop`
AND a list-child `App (list term)`; a mutually-recursive `size`/`size_list` measure; the rewriter
`flip`/`flip_list` constructing new nodes with `variant { size t }` / `variant { size_list l }`; and the
element-of-list-child decrease as a **proved `let rec lemma`, not an axiom**. **6/6 Valid on Alt-Ergo AND
Z3; 0 axiom declarations; negative control (non-decreasing self-call) correctly FAILS (non-vacuous).** So
(C) construction, (L) list-child map, (T) termination all PASS. Gate S PASSED → proceed to the emitter
build (there is NO refutation exit to take: the wall is confirmed breakable).

## 1. The emitter capabilities to build (named by the review, in dependency order)

The mirror's `Term` ADT is currently modeled for READS only (the emit_ir precedent: `kind_of`/`left_of`
projectors + `size`; the review confirmed `expressions.py:661 _IRNODE_CTORS` emits constructor applications
only for 5 leaf-ish inline-dict kinds — no recursive constructor, no dataclass-ctor-call path). To convert
a rewriter, add, in order (each spike-gated, byte-diff-0, ledger-3):

- **T-C1 — recursive-constructor emission from a dataclass call.** Recognize a Python `App(head=h,
  args=a)` / `BinOp(op, l, r)` construction (a frozen-dataclass constructor call whose class is a `Term`
  arm) → the WhyML constructor application `App h a` / `Binop op l r`. Extends `_IRNODE_CTORS` to the
  recursive arms (`IrBinOp`/`App`/`Unary`/`Forall`) and adds the dataclass-call recognizer. The value
  returned is an emit_ir/term-typed value (not opaque). Reuses the existing variant type + `size`.
- **T-C2 — comprehension over the recursive ADT → a recursive helper.** Lower
  `tuple(f(a) for a in t.args)` (a comprehension whose element is the recursive rewriter applied to a
  child) to a `let rec flip_list (l: list term) : list term` with its OWN `variant { size_list l }` — the
  review's confirmed shape. The result type `list term` composes with the `App head <list>` constructor.
  (Caution from the campaign: the child list must be a PURE `list`/`seq term`, never `array (seq τ)` with a
  mutable element — Why3 type-rejects that.)
- **T-C3 — the list-leg of the `size` measure + the element-decrease lemma.** The emitter already emits
  `size` for emit_ir; extend it to a mutually-recursive `size_list` counting cons cells (`1 +` per element
  — the review's robustness probe showed a bare-sum measure lets the rewriter through but FAILS the strict
  element lemma, so count cells), and emit `lemma size_list_elem_dec` (each element of a child list is
  `< size` of the node) as a PROVED lemma. No axiom (ledger 3).
- **T-C4 — emit_ir/term-typed function return.** A method `-> Term` returns a constructed term value; the
  return path + any early-return exception (see the `Return_<union>` U work) must carry the `term` payload.

## 2. Build order & first target

`T-C1 → T-C2 → T-C3 → convert `_flip_comparisons` (the minimal witness) → then the heavier rewriters
(`substitute`, `alpha_normalize`) as they add sub-features (`substitute` needs a `Var`-substitution map;
`_ac_normalize` needs list sorting — OUT of this plan's minimal scope)`. All-or-nothing per method (one
commit at the conversion; no facade). First target: `_flip_comparisons` — the exact shape the spike proved.

## 3. Gates (per converted rewriter)

- fidelity (52/52 + sync no-new-divergence); `--fun` + WHOLE-FILE proof of `canonical.py` SUCCESS (§10.10);
  byte-diff-0 (T-C1/T-C2 fire only on `Term`-dataclass constructions / recursive-ADT comprehensions →
  corpus-inert; authoritative worktree sweep REQUIRED — recognizer builds are the perturbation risk);
  ledger 3 (`Print Assumptions`/`#print axioms` unchanged; the new constructors extend the existing emit_ir
  variant — CONFIRM the coupling rule: a *constructed* term value must be covered by the existing
  record/variant certificate, or a side-car lemma co-lands — the review flagged this as the one unspiked
  coupling question); non-vacuity (the emitted rewriter CONSTRUCTS via `App`/`Binop`, recurses via
  `flip_list`, no opaque op); count strictly down.
- **The one open coupling-rule check (§10.5):** the read-only emit_ir ADT is certified for projection; a
  rewriter that CONSTRUCTS emit_ir/term values may need the certificate to cover the constructor eliminator
  too. Spike a hand `.mlw` + a `Print Assumptions` audit BEFORE T-C1 lands; if a new axiom would be needed,
  STOP (that would move this back toward a boundary).

## 4. Honest scope & non-goals

- The spike covers the MINIMAL witness (`_flip_comparisons`). `substitute` (needs a substitution map),
  `alpha_normalize`/`_ac_normalize` (need binder freshness / list sorting) are heavier — separate builds;
  T-C1..C4 are the reusable base.
- The emitter GENERATION is unspiked (only the TARGET is proven) — T-C1's dataclass-ctor recognizer is the
  make-or-break of the *build* (as opposed to the *target*); spike it (does the emitter emit `App h a` for
  `App(head=h, args=a)`?) before the full build.
- Ledger stays 3; if construction needs a new certificate the read-only ADT lacks, that is the coupling-rule
  obligation to co-land, not a silent axiom.

## 5. First action

**T-C1 emitter spike:** in a worktree, teach `_IRNODE_CTORS`/`_lower_irnode_construction` one recursive
constructor (`App(head, args)` → `App h a`) and confirm a mirror method that does `return App(head=x,
args=y)` emits the constructor application + type-checks — the make-or-break of *emitter-generability* (the
target-generability half the reviewer's spike did not cover). Then T-C2/T-C3, then convert `_flip_comparisons`.
