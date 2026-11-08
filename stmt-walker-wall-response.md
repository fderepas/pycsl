# Independent review: the stmt-walker wall — Why3 oracle verdict

*External reviewer, 2026-07-11. Input: `stmt-walker-wall.md` ONLY (no internal campaign files were
read), plus the actual Why3 oracle. Evidence artifact:
`getting-better/composition-wall/stmt-walker-spike.mlw` (hand-written for this review).
Environment: Why3 1.8.2, Alt-Ergo 2.6.2, Z3 4.13.3.*

## 1. Verdict

**BOUNDED FEATURE.** The recursive statement-tree READER — including the multi-list-child `Try`
shape at full strength — discharges axiom-free on BOTH solvers, in milliseconds, with the
element-decrease lemma PROVED (not assumed) and a non-vacuous negative control. Nothing in
(R)/(L)/(T) resists at the target level. The residual is emitter-generation work (§5), exactly as
the report's §4.3 predicted.

## 2. The spike and its per-goal results

`stmt-walker-spike.mlw` contains two modules.

**Module `StmtWalkerSpike`** (must be all-Valid) defines:

- `stmtir` = `SReturn | SPass | SExpr | SIf (list stmtir) (list stmtir) | SWhile (list stmtir) |
  STry (list stmtir) (list handler) (list stmtir) (list stmtir)`, mutually recursive with
  `handler = EHandler (list stmtir)`. This is deliberately HARDER than the report's minimum: `STry`
  carries FOUR list children (`body`, `handlers`, `orelse`, `finalbody`), and handlers are a
  separate sum whose constructor carries its OWN `list stmtir` body — the "each handler has its
  own body" schema at full strength, two list-nesting levels deep.
- A four-way mutually-recursive size measure `size` / `size_list` / `size_handler` / `size_hlist`,
  counting cons cells (`1 +` per element — the strict measure), with `result >= 1` / `>= 0`
  positivity ensures.
- The element-of-list-child decrease as PROVED `let rec lemma`s (`size_mem`, `size_mem_h`), plus
  three plain corollary lemmas covering every child position of `SIf` and `STry`, including the
  handler-body-inside-handler-list case (`size_try_handler_body`).
- The reader `ends_with_return : stmtir -> bool` mirroring the report's §2 witness (`Return` leaf
  true; `If` = both branches; `Try` = body AND all handlers; last-element list recursion), as
  THREE mutually-recursive program functions over the three sorts, with
  `variant { size s }` / `variant { size_list l }` / `variant { size_hlist hs }`. Read-only: it
  returns a bool and constructs no tree.

**Module `NegativeControl`** (must FAIL): `bad_walk` re-passes the SAME node it matched
(`SIf body orelse -> bad_walk (SIf body orelse)`), so its variant VC demands
`size (SIf body orelse) < size (SIf body orelse)` — false. A prover reporting it Valid would mean
the setup is vacuous.

Results (`why3 prove -P <p> getting-better/composition-wall/stmt-walker-spike.mlw`):

| Goal | Alt-Ergo 2.6.2 | Z3 4.13.3 |
|---|---|---|
| `size'vc` | Valid (0.08s) | Valid (0.02s) |
| `size_list'vc` | Valid (0.04s) | Valid (0.01s) |
| `size_handler'vc` | Valid (0.03s) | Valid (0.01s) |
| `size_hlist'vc` | Valid (0.05s) | Valid (0.01s) |
| `size_mem'vc` (proved element lemma) | Valid (0.05s) | Valid (0.02s) |
| `size_mem_h'vc` (proved handler-elem lemma) | Valid (0.04s) | Valid (0.01s) |
| `size_if_child` | Valid (0.04s) | Valid (0.01s) |
| `size_try_child` | Valid (0.04s) | Valid (0.02s) |
| `size_try_handler_body` | Valid (0.04s) | Valid (0.02s) |
| `ends_with_return'vc` (the READER) | Valid (0.05s) | Valid (0.02s) |
| `ends_with_return_list'vc` | Valid (0.04s) | Valid (0.02s) |
| `all_handlers_return'vc` | Valid (0.06s) | Valid (0.02s) |
| **Main module total** | **12/12 Valid** | **12/12 Valid** |
| NegativeControl `size'vc`, `size_list'vc` | Valid, Valid | Valid, Valid |
| NegativeControl `bad_walk'vc` | **Timeout (5s)** — FAILS, as required | **Timeout (5s)** — FAILS, as required |

Whole-file wall time ~6.5s per solver (dominated by the negative control's 5s timeout; every real
goal is < 0.1s).

- **Axiom count:** `grep -c '^axiom ' stmt-walker-spike.mlw` = **0**. The file's only non-defined
  symbols are the ADT constructors themselves (Why3-intrinsic, same trust class as `list`); unlike
  the term-rewriter spike it needs no abstract `val function`s at all.
- **Negative control:** fails on both solvers (Timeout on a goal that is semantically false —
  `x < x` — the expected failure mode). The setup is non-vacuous.

## 3. Report §4 fault lines: CONFIRMED vs KILLED

1. **(L) list-child recursion — KILLED as an obstacle, with the report's sub-diagnosis
   CONFIRMED.** `variant { size s }` on the node and `variant { size_list l }` on the list
   recursion discharge instantly on both solvers, including the cross-sort call from the node into
   its list children and from a handler-list into a handler's own body list. Separately, I ran an
   oracle control on the report's parenthetical: declaring `SIf (array stmtir) (array stmtir)` is
   rejected by Why3 at typing — *"This field has non-pure type, it cannot be used in a recursive
   type definition"*. So the reported live failure ("expected to have type array int") is indeed
   consistent with the current lowering picking a mutable-array child type that Why3 could never
   accept inside a recursive sum; the child type MUST be a pure `list`/`seq stmtir`. The spike
   establishes `list stmtir` as the working shape.
2. **Multi-field / handler shape — KILLED.** The FOUR-list-child `STry` (body + handlers + orelse
   + finalbody), with handlers as a mutually-recursive second sort carrying their own bodies, is
   the exact shape the spike proves. The single summed `size` measure gives a decreasing variant
   into ALL children simultaneously; the strict element lemmas (`size x < size_list l`,
   `size_handler h < size_hlist l`) and all three parent-child corollaries prove in < 0.1s. Schema
   breadth (the census's ~7 constructor shapes) is bookkeeping, not a proof obstacle: nothing in
   the discharge depended on arity, only on the positivity ensures and the cons-cell counting.
3. **Emitter-generability — CONFIRMED as the real residual.** The spike proves the *target* shape
   only. Everything I hand-wrote — the field projection as a `match` pattern, the
   `for h in handlers` as a recursive list function, the synthesized mutually-recursive signatures
   with per-sort variants — is precisely what the emitter must GENERATE from the verbatim Python
   (whose `StmtIR` handlers, per the report, currently round-trip to dicts). The oracle shows
   there is NO target-level obstruction hiding behind that build; but the build is real work and
   this review provides no evidence about its cost.

## 4. The coupling-rule note (read-only variants and the soundness certificate)

The spike's evidence: a read-only walker over the `stmtir` variant introduces **zero axioms** —
the only VCs beyond type-safety are the termination `variant` VCs and the lemma-function VCs, all
Why3-intrinsic and all discharged. No value of the new shape is ever constructed or returned, so
there is no new *value* whose soundness needs certifying: the ADT declaration itself sits in
Why3's native inductive-type theory, the same trust class as `list`, which the campaign already
accepts.

One conditional caveat, flagged without reading internal files: the report describes the expr-ADT
precedent as using `kind_of`/`left_of` *projectors*. If the stmt-family theory is emitted the way
this spike is written — constructors + pattern `match`, definitions not axioms — then the
read-only case triggers NO certificate obligation and termination is the only concern. If instead
the emitter follows a projector-AXIOM style (axiomatized `body_of`/`handlers_of` accessors),
those axioms are new trusted surface and the coupling rule fires regardless of read-only-ness —
not because a value is constructed, but because the theory's emission mode injects assumptions.
Recommendation: emit the stmt theory axiom-free (the spike proves it needs nothing more), and the
question dissolves.

## 5. Honest limits of this review

- **The spike proves the TARGET, not the emitter.** The report is right that the real residual is
  emitter-generation: lowering `s["body"]` to a typed field projection, `for h in s["handlers"]`
  to a list recursion/map, and synthesizing the mutually-recursive signature group with per-sort
  variants. None of that is exercised here; this review certifies only that when the emitter
  produces this shape, Why3 will discharge it axiom-free.
- The spike's schema is 6 constructors + 1 handler sort, not the full ~7-shape census
  (`Match`/`Case` are absent); given that nothing in the discharge was arity- or shape-sensitive,
  I judge the extrapolation safe, but it is an extrapolation.
- The spike proves ONE reader (`ends_with_return`). The 34-method claim is the report's census,
  not something this review verified; each conversion still owes its own proof under the
  campaign's three oracles.
- The negative control fails by Timeout (5s default), not by a counterexample certificate; a
  timeout on a semantically false goal (`x < x`) is the expected and standard failure mode, but
  strictly speaking Why3 reports "not proved", not "disproved".
- The reader's contract here is the type-safety shape (`requires/ensures { true }`) plus
  termination, matching the campaign's discipline as the report states it; value-level
  postconditions for individual walkers (e.g. relating the bool to a spec predicate) are a
  separate, per-method concern not probed.

## 6. Bottom line

Route 1 of the report's §6 is GO: build the stmt-family typed-node ADT with pure `list stmtir`
children (never `array` — Why3 type-rejects it, confirmed by oracle), a summed cons-cell `size`
across all sorts, the element-decrease as `let rec lemma`, and emit it axiom-free. The
make-or-break spike the report demanded exists, is in-tree at
`getting-better/composition-wall/stmt-walker-spike.mlw`, and is 12/12 Valid on Alt-Ergo AND Z3
with 0 axioms and a failing negative control. The wall is not a boundary.
