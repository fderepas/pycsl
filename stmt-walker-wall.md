# The Stmt-walker wall — a reviewer's map of recursive statement-tree walking in a deductive verifier

*External-review statement, 2026-07-11, produced by the self-tcb-reduction-driver (Gate W ESCALATED this
as a genuine, high-value, breakability-worth-checking wall). Self-contained: assumes no prior PyCSL
knowledge. It reports the single LARGEST convertible cluster the self-verification campaign has found — **42
recursive statement-tree walkers**, 34 of them behind one shared foundation — and asks the reviewer to
judge whether that foundation is a genuine boundary or a bounded, buildable feature, by RUNNING Why3 on a
make-or-break spike. Every claim is reproducible from the cited evidence.*

---

## 1. The global picture (what PyCSL is, and where this sits)

**PyCSL** is a deductive verifier for a Python subset: it compiles annotated Python through a 6-module
pipeline into **WhyML** (the [Why3](http://why3.org) language), whose verification conditions are
discharged by SMT solvers (Alt-Ergo, Z3) and, when those fail, by Rocq and Lean. It **verifies a mirror of
its own emitter** — the compiler's WhyML-generation code is itself annotated Python that PyCSL proves
type-safe, frame-correct, and terminating. The self-verification campaign converts the mirror's `\trusted`
stubs (assumed contracts) into verified bodies, one at a time, each held to three disjoint oracles
(fidelity to the live code, Why3 discharge, corpus byte-diff-0). ~1226 stubs remain; the campaign is at its
*cheap-conversion floor* — the residual is dominated by a few feature-gated foundations, of which THIS is
the largest single one.

This wall lives across the compiler's analysis passes: methods that **walk a Python statement tree** to
collect facts (which variables are assigned, whether a body always returns, which exceptions escape, etc.).
A census (below) found **42** such methods still trusted; **34** of them would be unlocked by ONE shared
foundation. That 34-method unlock is ~4× the campaign's usual "worthwhile cluster" threshold — hence the
escalation.

## 2. The method class

A **statement** in PyCSL's intermediate representation (IR) is a dictionary tagged by a `"stmt"` key, whose
compound forms carry **nested statement-list children**: an `If` has `body` and `orelse` (each a *list* of
statements); a `While`/`For` has `body` (and `For` an `orelse`); a `Try` has `body`, `handlers` (each with
its own `body`), `orelse`, `finalbody`; a `Match` has `cases` (each with a `body`). A **walker** consumes a
statement (or a list of them) and RECURSES into those nested list-children to accumulate a result. The
representative witness, a "does this body always return?" check:

```python
def _ends_with_return(stmts: List[Dict[str, Any]]) -> bool:
    if not stmts:
        return False
    last = stmts[-1]
    kind = last.get("stmt")
    if kind == "Return":
        return True
    if kind == "If":
        # BOTH branches must return — recurse into each nested stmt-LIST child
        return _ends_with_return(last["body"]) and _ends_with_return(last.get("orelse", []))
    if kind == "Try":
        return _ends_with_return(last["body"]) and all(
            _ends_with_return(h["body"]) for h in last.get("handlers", []))
    return False
```

Three properties together define the class:
- **(R) read-only accumulation** — the walker READS the tree and returns a scalar (`bool`/`Set[str]`/`int`),
  it does NOT construct a new tree (this is *strictly easier* than a tree-*rewriter*, which constructs);
- **(L) list-of-substatements recursion** — it recurses over a *variable-length list of child statements*
  (`for h in s["handlers"]`, `_ends_with_return(s["body"])`), the list accessed by a named subscript;
- **(T) structural termination** — the recursion is well-founded on the *subtree* order; a WhyML
  `variant { size s }` over the statement ADT is the natural measure.

## 3. What is known, and the open question

- PyCSL **already models a recursive-ADT for the EXPRESSION family** (the `emit_ir` node ADT: a WhyML
  variant with `kind_of`/`left_of`/… projectors, a `size` measure, and proven size-decrease lemmas;
  converted expression readers like `_is_float_expr`, `_rhs_yields_map` discharge against it). Reading an
  *expression* tree and returning a scalar is a *solved* class in this campaign.
- An independent review of a sibling wall (recursive *term*-rewriters) recently PROVED, with a hand Why3
  spike (6/6 Valid on Alt-Ergo + Z3, **0 axioms**, non-vacuous control), that a variant with a **list-child
  constructor** (`App (list term)`), a **mutually-recursive `size`/`size_list` measure**, and a recursive
  function with `variant { size t }` / `variant { size_list l }` — including the **element-of-list-child
  decrease as a proved `let rec lemma`** — discharges axiom-free. That spike CONSTRUCTS a new tree; the
  walkers here only READ, so their target should be *no harder*.
- The **statement** family, however, has **no** WhyML typed-node ADT. There IS a Python-side typed sum
  (`StmtIR` with `stmt_from_dict`/`.to_dict()`), but the walkers' handlers **round-trip** the nested
  children back through `.to_dict()` into `List[Dict[str, Any]]` before recursing. When such a body is
  lowered, the subscript on the list-child (`s["body"]`) is typed as an opaque scalar (`int`), while the
  recursive callee's synthesized signature expects a `list`/`array` of statements → the whole-file proof
  fails: *"This expression has type int, but is expected to have type array int."* (An actual, reproduced
  failure — the direct trigger for this escalation.)

**The open question for the reviewer:** is a total, structurally-terminating **recursive statement-tree
READER** — a variant `stmtir` with `list stmtir` (or `array stmtir`) body-children, a `size`/`size_list`
measure, and a walker recursing over `s.body`/`s.orelse`/`s.handlers[i].body` with `variant { size s }` —
expressible and provable in WhyML under PyCSL's discipline (type-safety + frame + termination, no new
axiom)? I.e. is this a **bounded feature build** (the stmt-family analogue of the already-certified expr
ADT, and *easier* than the proven term-rewriter because it does not construct), or does one of (R)/(L)/(T)
resist — making it a **genuine boundary** (leave-trusted)?

## 4. The suspected fault lines (for the reviewer to confirm or refute against the oracle)

Reasoning suggests three candidate obstacles; the review should *run* Why3 to confirm or kill each:

1. **The list-child recursion (L).** A walker recurses `f(s.body)` where `s.body : list stmtir`. WhyML can
   express `size_list`, and the term-rewriter spike proved the *element decrease* lemma axiom-free — but for
   a **reader** over a variant whose fields are themselves `list stmtir`, does `variant { size s }` on the
   node, plus `variant { size_list l }` on the list-recursion, discharge? (Recall a related campaign
   finding: `array (seq τ)` with a *mutable* element is Why3-type-rejected; the inner child MUST be a pure
   `list`/`seq stmtir`, never a mutable `array`. The reported live failure expects `array int` — this
   suggests the current lowering picks the WRONG (mutable-array) child type. The spike should establish the
   RIGHT one, `list`/`seq stmtir`.)
2. **The multi-field / handler shape (schema breadth).** Unlike the binary expr nodes (`left`/`right`), a
   `Try` has FOUR stmt-list fields (`body`/`orelse`/`finalbody` + `handlers`, and each handler has its own
   `body`). Does a single `size` measure summing over all list-children still give a decreasing `variant`
   for a walker that recurses into all of them? How many distinct constructor shapes does the ADT need to
   cover the 34-method cluster (the census suggests ~7: If/While/For/Try/ExceptHandler/Match/Case)?
3. **Emitter-generability, NOT target-provability (the real residual).** Even if the *target* `.mlw` proves
   (§3's precedent strongly suggests it will), the campaign's recurring gap is that the **emitter must
   GENERATE that shape from the verbatim Python** — lower `s["body"]` to a projection of a `list stmtir`
   field (not an opaque `subscript_get`), lower `for h in s["handlers"]` to a list-map, and synthesize the
   recursive signature over `stmtir`. The Python-side `StmtIR` sum exists but its handlers round-trip to
   dicts. Is the residual purely this emitter feature (a build), or is there a target-level obstruction too?

## 5. State of the art — why this is a fair lens

Verified analysis of inductive syntax trees is the *native* territory of proof-assistant-based verification
(Rocq/Lean/Agda/Dafny/F*): a `Stmt → bool` structural recursion is textbook, its termination automatic from
the recursion principle. The question is whether the *SMT-backed, contract-shaped* setting PyCSL targets
(Why3 + a type-safety+frame+termination contract, no interactive induction) can express the same walk — and
crucially whether PyCSL's *emitter* generates that shape from verbatim Python, or whether the mirror methods
must stay `\trusted`. The expr-family ADT already answers "yes, for expression readers"; the term-rewriter
spike answers "yes, even for list-child constructors, axiom-free." This wall asks whether that foundation
extends to the **statement** family — a larger schema (multi-field compound nodes) but a strictly easier
operation (read, not construct). It is a crisp probe of *how far the certified reader-ADT foundation scales*.

## 6. The routes, honestly costed (for the reviewer to weigh)

1. **Build the stmt-family typed-node ADT** (Schema 1: a WhyML `stmtir` variant with `list stmtir`
   body-children + `size`/`size_list` + the element-decrease lemma), teach the emitter to lower the existing
   Python `StmtIR` sum's field-projections (`s.body`) and list-maps (`for h in s.handlers`) to it, and
   convert the 34 dict-IR walkers. Bounded IF (R)/(L)/(T) compose (the spike settles this) and the emitter
   feature lands. Make-or-break: a hand `.mlw` that defines `stmtir` as a variant with a `list stmtir` child,
   writes a reader `ends_with_return : stmtir → bool` recursing over the child list with `variant`, and
   discharges axiom-free — spiked BEFORE any emitter work.
2. **A second, smaller pure_ast-node schema** (Schema 2) for the remaining 8 attribute-based walkers
   (`ConcurrencyChecker`, the unparser) — a follow-on, out of this report's primary scope.
3. **Accept the boundary** (leave-trusted): if the spike shows the list-child reader needs a new axiom or
   interactive induction, the class is a certified boundary, recorded like the map-iteration wall.

## 7. Honest limits of this report

- The three fault lines in §4 are *reasoned hypotheses*, not measured — the whole point of the review is to
  RUN Why3 (a hand `.mlw` spike) and confirm/refute each; a review that only re-reasons from this prose has
  added no evidence. The strong prior (the term-rewriter spike proved the harder constructor case
  axiom-free) suggests the target WILL prove — but the reviewer must SHOW it for the statement/multi-field
  shape, and probe the negative control (a non-decreasing self-call must FAIL, proving non-vacuity).
- The 34-method count is a census over the trusted mirror stubs' *live bodies*; it is a statement about the
  current converted set, not a proof that all 34 lower identically — the reviewer's spike establishes the
  *shape*, the build establishes each conversion.
- Soundness is untouched: the 3-axiom ledger is unchanged; a `\trusted` walker is an assumption made
  explicit, not a hidden gap. Any new value shape (the `stmtir` variant) carries the campaign's standing
  **coupling rule**: it must co-land with a Rocq/Lean certificate that the value is sound (ledger stays at 3)
  — the reviewer should note whether a *read-only* variant (no constructed value returned) even triggers
  that obligation, or whether termination (a Why3-intrinsic `variant` VC) is the only concern.
- Evidence to reproduce: the census in `getting-better/wall-lessons.md` (2026-07-11 entry: the 42-method
  A/B/C bucketing, the 34/8 schema split, the `ir_scanner.py` "stateless recursive walkers over the IR dict
  tree" class); the expr READER ADT precedent (`preamble.py::_emit_exprir_theory` — variant + `size` +
  size-decrease lemmas); the term-rewriter spike (`getting-better/composition-wall/term-rewriter-spike.mlw`
  — 6/6 Valid, 0 axioms, the list-child `size_list` + element-decrease lemma); the Python-side `StmtIR` sum
  (`statements.py::stmt_from_dict`/`.to_dict()`); the `array (seq τ)`-immutability finding
  (`getting-better/nested_list_project` per the campaign memory).

## 8. The one thing this review must produce

A hand-written `stmt-walker-spike.mlw` and its Why3 verdict: a `stmtir` variant with at least one
**multi-list-child** constructor (a `Try`-like node with `body : list stmtir` AND `handlers : list stmtir`),
a `size`/`size_list` measure, a **reader** `ends_with_return : stmtir → bool` recursing over the child lists
with `variant { size s }` / `variant { size_list l }`, and the element-of-list-child decrease as a **proved
`let rec lemma` (NOT an axiom)** — reported Valid/Invalid per goal, with the axiom count (`^axiom ` must be
0) and a negative control (a non-decreasing recursion that MUST fail). That verdict — BOUNDED FEATURE vs
BOUNDARY — is the deliverable. Write it to `stmt-walker-wall-response.md`.
