> # ⚠ SUPERSEDED — THIS WALL DOES NOT EXIST
>
> **Resolved 2026-08-26 as REFUTED-STALE, payoff 0. Do not act on this report.**
>
> Gate R's independent review ran the whole-file proof of `ir_scanner.py` and found 409
> `_collect_mutations` subgoals and 71 `find_iteration_mutations` subgoals *proving*. A `\trusted`
> stub emits as a bodyless `val` and has no subgoals — so the target could not still be trusted.
> Confirmed: `grep -cF '#@ \trusted' src/self-annotate/src/module6_whyml/ir_scanner.py` -> **0**.
>
> The wall had already been broken, by a different route, at `c6557971` / `fdbccc77` / `4700f558`
> (the heterogeneous value-model root) — not by the structural robustification this report proposes.
> The `wall-lessons.md` chain `#18 -> #21 -> #22 -> "the ONLY remaining path is ..."` was never
> retired and propagated a reopening for a wall that no longer existed, all the way into the
> 2026-08-26 authority amendment as pre-authorized flagged build (a). **That amendment item is MOOT.**
>
> Kept only as the evidence trail for the STALE-WALL lesson (`wall-lessons.md`, 2026-08-26) and the
> Gate W FRESHNESS PRECONDITION carved into the driver skill.

# Wall report: `find_assigned_vars` structural-variant robustification (`fav-structural-robustification`)

Author: driver-coordinator (report author — this document is `U`, a *soft* claim; it may be refuted).
Date: 2026-08-26. Tree: branch `ghost-assign-bc6`, HEAD `31654938`.
Canonical `\trusted` count at HEAD: **675**
(`grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l`).

---

## 1. Global picture — what PyCSL is and where this wall sits

PyCSL is a deductive verifier for Python: `#@` contract annotations (requires / ensures / assigns /
loop invariants / variants) are parsed, woven into an IR, and lowered to WhyML, where SMT solvers
(Alt-Ergo, Z3, CVC5) discharge the verification conditions. The compiler is six modules
(Ingestor → Parser → Weaver → SemanticAnalyzer → IREmitter → WhyMLTranspiler).

**The self-TCB-reduction campaign.** PyCSL's own compiler is its own largest trusted base. The campaign
maintains a *mirror* of the compiler under `src/self-annotate/src/` in which every function is either
(a) annotated and machine-proved, or (b) marked `#@ \trusted` — an explicit, counted trust assumption.
The campaign's single metric is the count of `#@ \trusted` markers, which must strictly decrease, and
the metric is honest only because three *disjoint* oracle planes gate every conversion:

- **Fidelity** — `bin/check-self-annotate-sync.sh` + `bin/self-annotate-mirror-check.sh`: the mirror's
  un-trusted bodies must be *verbatim* the live compiler's bodies. Without this the mirror could be
  proved by rewriting it into something easy, proving a different program.
- **Type-safety / proof** — `python3 src/pycsl/pycsl.py <file> --import-path src/pycsl`: the *whole
  file* must prove 0 non-Valid goals. Per-function `--fun` is explicitly **not** a substitute.
- **Corpus inertness** — `bin/byte-diff-sweep.sh` against a worktree-at-HEAD baseline: emitter changes
  made to enable a conversion must not alter the WhyML emitted for the 800+ reference corpus programs,
  or, under the M1 discipline, the diff must be exactly the intended semantic correction and every
  affected program must re-prove.

Plus: the **axiom ledger stays at 3** (`Print Assumptions` in Rocq / `#print axioms` in Lean over the
`#@ proof` certificates), and no converted body may be a vacuous facade.

**Where this wall sits.** `src/pycsl/module6_whyml/ir_scanner.py` is the IR statement scanner. Two of
its walkers are the subject:

- `IRScanner.find_assigned_vars(stmts)` — **already converted and proved**. It is emitted by a
  dedicated recognizer/emitter pair, `recognize_find_assigned_vars` / `emit_find_assigned_vars_group`
  in `src/pycsl/module6_whyml/generic_fold.py:16916` / `:17031`.
- `IRScanner._collect_mutations(...)` — **still `#@ \trusted`**. It is the last unconverted member of
  the pydict tree-walker family in this file, and it is the target.

The wall is not "can `_collect_mutations` be modeled?" — that was answered *yes* twice. The wall is a
**solver-search interaction between the two**: converting `_collect_mutations` tips `find_assigned_vars`'
already-razor-edge proof over a cliff.

---

## 2. The wall as first seen, and the three refuted reopenings

`_collect_mutations` was built as a `ref (list pyval)` Cons-accumulator with generic
`__walk`/`__walkd`/`__walkl` structural-variant descent. The emitted provider was verified
byte-identical to the banked `scratchpad/cm_structvar.mlw`; it type-checks; it is non-vacuous
(mutation-tested: perturbing the member check and the separator moves the `.mlw`); it introduces no
axiom (ledger 3). The *build* is sound. What fails is the **whole-file proof of `ir_scanner.py`**:

`find_assigned_vars`' two size-postcondition reader goals, `find_assigned_vars__Lbody` and
`find_assigned_vars__Lorelse`, go from **Valid** to **Timeout** once another recursive walker's reader
definitions join the module. Three successive reopening hypotheses were spiked and all three were
**refuted by measurement**:

1. **`#@ no_inline` on `_collect_mutations`** (worker#18) — REFUTED. Emission was byte-identical: the
   pollution is *module-definition presence*, not call-site inlining. Recursive walkers are never
   inlined in the first place.
2. **`#@ verify_module` after fixing the recognizer-group `Sig` bug** (workers #20/#21/#22) — REFUTED
   **decisively**, and this is the load-bearing measurement. A three-proof spike whose variants differ
   *only* in `verify_module` tags:

   | variant | `find_assigned_vars` tag | `_collect_mutations` | `find_assigned_vars__Lbody/Lorelse` |
   |---|---|---|---|
   | t3 | (none — flat HEAD) | trusted | **Valid**, 0.23 s, 490 K steps |
   | t2 | `#@ verify_module VarsMod` | **still trusted** | **Timeout**, 30 s, 280 M steps |

   With `_collect_mutations` left trusted and the *only* change being the isolation tag on
   `find_assigned_vars`, its goals regress by roughly six orders of magnitude of search. The modular
   scaffolding (`use Shared` trigger set, `clone …'refn'vc` context) is itself a perturbation that tips
   a razor-edge goal. **Isolation makes it worse, not better.**
3. Bounded-iteration / `while`→`for` variants — separate boundary, breaks mirror-sync fidelity.

**Classification recorded in `wall-lessons.md`:** a COST/SCALE-adjacent **correctness** wall in the
narrow sense that there is no ADT, no certificate, and no axiom missing — the obstacle is a solver
*search cliff*. Both landing paths that **keep `find_assigned_vars`' current emission** fail: flat tips
it, modular tips it further.

---

## 3. The deeper truth — this is a modeling choice, not a fundamental limit

The razor edge is not intrinsic to the program. It is intrinsic to **how termination is currently
argued** for `find_assigned_vars`.

`emit_find_assigned_vars_group` emits the fold as

```
let rec <n>__f (stmts: list pyval) (acc: ref (map string bool)) : unit
  variant { size_list stmts }
= ... else if pystr_eq tag "While" then <n>__f (<n>__Lbody d) acc
  ... else if pystr_eq tag "If"    then (<n>__f (<n>__Lbody d) acc; <n>__f (<n>__Lorelse d) acc)
```

The recursive argument is the **result of a reader function call**, `<n>__Lbody d`, not a structural
sub-term. Why3 therefore cannot use its built-in structural ordering, and termination must instead be
argued *numerically*, via a size measure. That forces each list reader to carry

```
ensures { match result with Some v -> pv_size v <= size_dict d | None -> true end }
ensures { size_list result <= size_dict d }
```

and it is exactly these two `size_list result <= size_dict d` goals — `__Lbody` and `__Lorelse` — that
sit at the search cliff. They are arithmetic goals over a recursively-defined measure, discharged only
by an E-matching search that pycsl currently wins by best-of-N per-goal solver racing. Any enlargement
of the module's trigger population perturbs that search.

The sibling walker `_collect_mutations` **does not have this problem**, because it was built the other
way: mutual structural descent `__walk (v: pyval) variant {v}` / `__walkd (d: pydict) variant {d}` /
`__walkl (xs: list pyval) variant {xs}`, where every recursive argument is a syntactic sub-term of the
parameter. Why3 discharges those termination obligations structurally, with **no size lemma and no
arithmetic goal at all** — which is precisely why it "proves robustly" while `find_assigned_vars` does
not.

**So the claim of this report is:** the wall is a consequence of an early modeling decision
(size-measure termination via list readers) that a later, better-understood pattern
(mutual structural variants) supersedes. Rewriting `emit_find_assigned_vars_group` in the structural
style **deletes the `__Lbody`/`__Lorelse` goals from existence** rather than trying to make them
survive a larger module. This is the only reopening in the chain that has never been tried.

---

## 4. The proposed build, and its two named risks

**Build.** Rewrite `emit_find_assigned_vars_group` (`generic_fold.py:17031`) to emit a mutual
structural-variant walker group in the `_collect_mutations` style, eliminating `<n>__Lbody` and
`<n>__Lorelse` (and their size postconditions) entirely. Then convert `_collect_mutations` **flat** —
no `no_inline`, no `verify_module`, both refuted.

**RISK (a) — it re-emits an already-landed, already-proven function.** `find_assigned_vars` is
currently VERIFIED. Any rewrite of its emission is a regression risk against a working proof. Mitigating
facts: `find_assigned_vars` is mirror-only (no corpus program contains it), so corpus byte-diff should
stay 0; but the mirror `.mlw` moves and the whole-file re-proof is mandatory, not optional.

**RISK (b) — the faithfulness trap, which is the real danger.** `find_assigned_vars` descends
**selectively**. From the live body (`src/pycsl/module6_whyml/ir_scanner.py:33`):

| stmt tag | what is collected | what is descended |
|---|---|---|
| `Assign`, `AugAssign` | `stmt["target"]` | — |
| `TupleUnpack` | `stmt.get("targets", [])` | — |
| `While` | — | `body` **only** (NOT `orelse`) |
| `If` | — | `body` **and** `orelse` |
| `For` | `stmt.get("target","")` if truthy | `body` **only** |
| `Try` | — | `body`, plus each handler's `body` |
| `Match` | — | each case's `body` |
| *(every stmt)* | walrus targets via `find_named_expr_targets` | (that walk is generic) |

A **naive** generic structural descent — "walk every value in every cell" — would over-collect: it
would descend `While.orelse` and `For.orelse`, which the Python does not. That is a *fidelity* failure
disguised as a proof success: the emitted WhyML would prove, but it would prove a different function
than the one in the mirror. The rewrite must therefore keep per-tag selectivity by binding the descent
through a structural `match` on the parent dict's cells (dispatching on the already-read tag), **not**
by reintroducing a reader function — reintroducing a reader is exactly what breaks the structural-order
chain and brings the size goals back.

**Expected yield.** 1 marker guaranteed (`_collect_mutations`), plausibly 2
(`find_iteration_mutations` shares the shape and was named as the follow-on). Low per-stub ROI; the
2026-08-26 authority amendment pre-authorizes it regardless, and cost/scale is not a stop condition.

---

## 5. Honest limits of this report

- I have **not** run the structural rewrite. Section 3's claim that the structural style *deletes* the
  problematic goals is an inference from (i) the emitter source and (ii) the fact that
  `_collect_mutations`' own structural group proves robustly. It is not yet a measurement. **This is
  the single most important thing for an independent reviewer to attack.**
- The banked `scratchpad/cm_structvar.mlw` (77 KB) is a `_collect_mutations` emission from a **prior
  tree**; its byte-identity to a fresh rebuild is asserted from the worker#22 record, not re-verified
  by me at HEAD.
- The t2/t3 spike numbers in §2 are quoted from `getting-better/wall-lessons.md`, not re-run at HEAD.
- I have not measured whether `find_assigned_vars` still proves Valid *at HEAD* — the campaign moved
  from ~804 to 675 markers since worker#22, so the module population of `ir_scanner.py` has changed and
  the razor edge may have moved in either direction.
- Whether the structural rewrite can keep *both* the walrus (`find_named_expr_targets`) inlined copy
  and the per-tag selectivity inside one mutual-recursion group, without a size measure sneaking back
  in, is unproven.

---

## 6. What would refute this report

Any one of the following, run as an oracle:

1. The structural rewrite is emitted and `ir_scanner.py`'s whole-file proof still has non-Valid goals →
   the reopening is refuted and the wall is a genuine CERTIFIED-BOUNDARY.
2. The structural rewrite cannot preserve per-tag selectivity without a reader (fidelity failure) → the
   build is unsound and must not land.
3. `find_assigned_vars` is measured to **already** be non-Valid at HEAD → the premise of the whole
   chain has expired and the wall must be re-stated from scratch.
4. `_collect_mutations` turns out to be blocked by something orthogonal at HEAD (its live body having
   changed since worker#22) → the payoff is 0 and the build should not be started.
