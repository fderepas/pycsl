# The Term-rewriter wall — a reviewer's map of AST-tree-rewriting in a deductive verifier

*External-review statement, 2026-07-10, produced by the self-tcb-reduction-driver (Gate W ESCALATED this
as a genuine, breakability-unknown wall). Self-contained: assumes no prior PyCSL knowledge. It reports a
class of methods the self-verification campaign cannot yet convert — **recursive AST tree-rewriters that
consume one immutable syntax tree and construct a transformed one** — and asks the reviewer to judge
whether this is a genuine boundary or a bounded, buildable feature. Every claim is reproducible from the
cited evidence.*

---

## 1. The global picture (what PyCSL is, and where this sits)

**PyCSL** is a deductive verifier for a Python subset: it compiles annotated Python through a 6-module
pipeline into **WhyML** (the [Why3](http://why3.org) language), whose verification conditions are
discharged by SMT solvers (Alt-Ergo, Z3) and, when those fail, by Rocq and Lean. It **verifies a mirror of
its own emitter** — the compiler's WhyML-generation code is itself annotated Python that PyCSL proves
type-safe, frame-correct, and terminating. The self-verification campaign converts the mirror's `\trusted`
stubs (assumed contracts) into verified bodies, one at a time, each held to three disjoint oracles
(fidelity to the live code, Why3 discharge, corpus byte-diff-0). ~1226 stubs remain; the campaign is at its
*cheap-conversion floor* — the residual is dominated by hard classes and a few feature-gated builds.

This wall is one hard class, and a representative one. It lives in `proof2why3/` — the subsystem that
canonicalizes proof terms exported from Rocq/Lean into a normal form (so a Rocq theorem and its Lean twin
compare equal). `proof2why3/canonical.py` holds a family of **term rewriters**: `_flip_comparisons`,
`substitute`, `_alpha_rename`, `alpha_normalize`, `_ac_normalize`, `_flatten_foralls`, `canonicalize`.

## 2. The method class

A **term** is a value of an algebraic syntax tree — a 9-constructor sum of frozen dataclasses:
`Var | IntLit | BoolLit | App(head, args) | BinOp(op, lhs, rhs) | UnaryOp(op, arg) | Forall(binders, ty,
body) | Exists(...) | Unsupported`. A **rewriter** consumes a `Term` and returns a *new, transformed*
`Term`. The minimal witness, `_flip_comparisons` (rewrite `a ≤ b` → `b ≥ a`, recursively):

```python
def _flip_comparisons(t: Term) -> Term:
    if isinstance(t, (Var, IntLit, BoolLit, Unsupported)): return t          # leaves: identity
    if isinstance(t, App):
        return App(head=t.head, args=tuple(_flip_comparisons(a) for a in t.args))   # CONSTRUCT + recurse over a subtree LIST
    if isinstance(t, BinOp):
        if t.op in _FLIP_COMPARISON:
            return BinOp(_FLIP_COMPARISON[t.op], _flip_comparisons(t.rhs), _flip_comparisons(t.lhs))  # CONSTRUCT, args swapped
        return BinOp(t.op, _flip_comparisons(t.lhs), _flip_comparisons(t.rhs))
    if isinstance(t, UnaryOp): return UnaryOp(t.op, _flip_comparisons(t.arg))
    if isinstance(t, (Forall, Exists)):
        kind = Forall if isinstance(t, Forall) else Exists
        return kind(binders=t.binders, ty=t.ty, body=_flip_comparisons(t.body))
```

Three properties together define the class, and each is the crux:
- **(C) construction** — it *builds* new nodes (`App(...)`, `BinOp(...)`), not just reads fields (unlike
  the emit_ir readers the campaign already converts, which return `bool`/`str`);
- **(L) list-of-subterms recursion** — `tuple(_flip_comparisons(a) for a in t.args)` maps the rewriter
  over a *variable-length list of child terms* and rebuilds the list;
- **(T) structural termination** — the recursion is well-founded on the *subtree* order; a WhyML
  `variant { size t }` over the term ADT is the natural measure.

## 3. What is known, and the open question

- PyCSL **already models recursive-ADT READERS** (the `emit_ir` node ADT: a WhyML variant with
  `kind_of`/`left_of`/… projectors, a `size` measure, and proven size-decrease lemmas; converted readers
  like `_is_float_expr`, `_rhs_yields_map`). Reading a tree and returning a scalar is a *solved* class in
  this campaign.
- PyCSL also has **inductive value types with constructors** (`pyval`/`pydict`, `RecordVal`), and a
  standing **coupling rule**: any new WhyML value shape must co-land with a Rocq/Lean certificate that the
  value is sound (the 3-axiom ledger must stay at 3).
- What is **NOT** demonstrated is a rewriter that does **(C)+(L)+(T) at once**: consume the `Term` ADT and
  *construct* a transformed `Term`, mapping over a child-list, proven terminating and type-safe. The
  emit_ir ADT is used only for *reads* (projection); no converted method *constructs* an emit_ir/Term value
  and returns it.

**The open question for the reviewer:** is a total, structurally-terminating **`Term → Term` rewriter**
expressible and provable in WhyML under PyCSL's discipline (type-safety + frame + termination contract, no
new axiom) — making this a **bounded feature build** (model `Term` as a WhyML variant with constructors +
a `size` measure + a `list`/`seq` map-combinator over `args`, and let the rewriter recurse) — or does one
of (C)/(L)/(T) resist, making it a **genuine boundary** (leave-trusted)?

## 4. The suspected fault lines (for the reviewer to confirm or refute against the oracle)

Reasoning suggests three candidate obstacles; the review should *run* Why3 to confirm or kill each:

1. **Construction into an immutable ADT (C).** Why3 variants are immutable values; constructing
   `App head args` is fine in principle. The question is whether PyCSL's emitter *emits* a constructor
   application for a Python `App(head=…, args=…)` call, or only models emit_ir/Term as *opaque projected*
   (read-only) — i.e. is there an emitter path from a Python ADT-constructor call to a WhyML constructor?
2. **The `args` child-list map (L).** `tuple(f(a) for a in t.args)` is a comprehension producing a
   *new list of terms*. WhyML can express `map f (args t)` over a `list term` — but does PyCSL lower a
   Python comprehension whose element type is the *recursive ADT itself*, and does the result type
   (`list term` / `array term`) compose with the constructor `App head <that list>`? (Recall a related
   finding: `array (seq τ)` with a mutable element is Why3-type-rejected; the inner must be a pure
   `list`/`seq`.)
3. **Termination over a constructed result (T).** The recursion is structural on the *input* subtree, so
   `variant { size t }` should discharge (the emit_ir readers already do this). But the map over `t.args`
   recurses on `a ∈ args t` — the size-decrease lemma must cover *"each element of `args t` is smaller
   than `t`"*, an element-of-list-child relation, not just the fixed `left_of`/`right_of` of the binary
   emit_ir nodes. Is that lemma provable (no axiom) for a `list`-child constructor?

## 5. State of the art — why this is a fair lens

Verified transformation of inductive syntax trees is the *native* territory of proof-assistant-based
verification (Rocq/Lean/Agda): a `Term → Term` function is defined by structural recursion, its termination
is automatic from the recursion principle, and its properties are proved by induction. **That is exactly
where PyCSL's `proof2why3` terms *come from*** — they are Rocq/Lean proof terms. So the rewriters are, in
the source world, textbook structural recursions. The question is whether the *SMT-backed, contract-shaped*
setting PyCSL targets (Why3 + a type-safety+frame+termination contract, no interactive induction) can
express the same transformation without dropping to the proof assistant. Dafny and F* can define and prove
such datatype-to-datatype functions (with `decreases` clauses and matched constructors); the open question
is whether PyCSL's *emitter* generates that shape from the verbatim Python, or whether the mirror method
must stay `\trusted` because the emitter models the ADT for reads only. The class is therefore a crisp
probe of *how far the reader-ADT foundation extends to constructors* — a known frontier, not a mystery.

## 6. The routes, honestly costed (for the reviewer to weigh)

1. **Extend the emit_ir/Term ADT to constructors + a list-child map + the element-decrease lemma**, and
   convert the rewriter. Bounded IF (C)/(L)/(T) compose; a real emitter feature (constructor emission,
   comprehension-over-recursive-ADT, the list-element size lemma) and a coupling-rule check (does a
   *constructed* Term value need a new certificate beyond the read-only ADT's?). Make-or-break: a hand
   `.mlw` that defines `term` as a variant, writes `flip : term → term` with `variant { size t }`, and
   discharges — spiked BEFORE any emitter work.
2. **Model the rewriter's result opaquely** (return an abstract `term` with only type-safety). Likely
   VACUOUS (the transformation content is lost; the campaign forbids vacuous conversions) — probably a
   non-starter, listed for completeness.
3. **Accept the boundary** (leave-trusted): if the spike shows construction/list-child/termination do not
   compose without a new axiom or an interactive induction, the class is a certified boundary, recorded
   like the map-iteration wall.

## 7. Honest limits of this report

- The three fault lines in §4 are *reasoned hypotheses*, not measured — the whole point of the review is to
  RUN Why3 (a hand `.mlw` spike) and confirm/refute each; a review that only re-reasons from this prose has
  added no evidence.
- "Not demonstrated" (§3) is a statement about the current converted set, not a proof of impossibility —
  §5 shows proof assistants do this routinely; the question is the SMT/contract setting + the emitter path.
- Soundness is untouched: the 3-axiom ledger is unchanged; a `\trusted` rewriter is an assumption made
  explicit, not a hidden gap.
- Evidence to reproduce: `src/pycsl/proof2why3/canonical.py` (`_flip_comparisons`, `substitute`,
  `alpha_normalize`, …); `src/pycsl/proof2why3/ir.py` (the `Term` dataclass sum); the emit_ir READER ADT
  (`preamble.py::_emit_exprir_theory` — variant + `size` + size-decrease lemmas, the read-only precedent);
  the `array (seq τ)` immutability finding (`getting-better/nested_list_project` per the campaign memory).
