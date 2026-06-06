# SCC ordering: add contract-reference edges to the call graph

This is a real ordering-completeness bug: the call graph is missing an entire class of edges. The
dependency that forces WhyML declaration order isn't "A's body calls B" — it's "A *references* B," and
a contract reference is exactly as binding as a body reference, because `let f … ensures { rank c … }`
is just as unbound-symbol-broken as a body call would be. So the fix is to make the graph reflect the
true reference relation. The plan below gets there without tripping the byte-diff gate.

## Grounding (verified in the current code — read before planning)

- **The graph is body-only.** `scc.py::sort_functions_by_scc` builds it as
  `call_graph[name] = find_calls_in_ir(func["body"], …)`. Contracts are never scanned. This is the bug.
- **The emitter already keys `rec`/`with` off SCC membership, not body recursion.** In
  `functions.py` the keyword is `'let rec function' if (use_rec or _scc_size > 1) else 'let function'`
  (and the mutual-continuation `with function` / `and` cases key off `_pos_in_scc`/`_scc_size`). So a
  *mutual* group formed through contract edges will emit `let rec … with …` correctly **for free**
  once it's a single SCC — the emitter change is minimal. (Caveat in Phase 2.)
- **There is no contract-reference purity check today, and there doesn't need to be for this fix.** An
  impure (or otherwise non-logic) reference in a contract currently lowers to an *abstract `val`* via
  `_handle_call_expr`, not to the real function — so it carries **no** declaration-order dependency.
  The fix is therefore self-protecting: impure references must simply *not generate edges*. (See the
  "unbundle" note — turning impure contract references into a hard error is a *separate* decision.)

## Phase 0 — Characterize before touching anything

Before adding edges, prove the current state to yourself. Add a *diagnostic-only* pass that walks every
function's `requires`/`ensures`/`assigns`/`variant`/`raises` (and class invariants, behavior blocks,
and — once they exist — quantifier bodies and lemma contracts) collecting referenced logic-symbol
names, and compares the contract-induced order against the current body-only SCC order. Run it across
the whole corpus and log every case where contract order would differ. This quantifies the blast radius
(how many existing files depend on the missing edges vs. get them by luck of source order) and gives
the exact watch-list for the byte-diff gate. No behavior change yet, so it's safe to land first.

**Honest note on sequencing:** Phase 0 already needs the *edge collector* of Phase 1 (you can't compute
"contract order" without it). So the real work — the binder-aware, purity-correct collector — lands
*in* Phase 0; "no behavior change" describes the *output* (a log), not that the hard part is deferred.
Budget accordingly: the collector is the bulk of the effort and essentially all of the risk.

## Phase 1 — Collect contract-reference edges (the crux)

Extend the edge collector so that, for each function `A`, you gather not just body calls but every
**logic symbol** named anywhere in `A`'s contract. Three points decide whether this is correct:

**Reuse Module 4's existing contract walker — do not write a new one.** `Module4_SemanticAnalyzer`
already has `_CSL_CHILDREN_MAP` + `extract_variables`, which enumerate every contract node type and
**already subtract quantifier binders** (`extract_variables(node.body) - {node.var}`). Reusing that
machinery defuses the bound-variable trap by construction and guarantees you don't miss a contract node
kind (the most likely source of an under-collecting bug). Writing a fresh walker re-introduces both
risks.

**The edge predicate must be *identical* to the emitter's "emits as a logic symbol" decision — make it
one shared function.** An edge `A → B` belongs only when `B` lowers to a real WhyML
`let function`/`predicate`/`lemma` that needs prior declaration. The right predicate is **not** "is `B`
pure" — it is the emitter's actual gate, `can_emit_as_logic = func_pure and not local_refs and not
is_method` (functions.py). A reference whose target lowers to an *abstract `val`* (impure, a method, or
having local refs) needs **no edge** and must not get one. Because the ordering decision (this graph),
the `rec`/`with` decision, and the emission decision all must agree on "is `B` a logic symbol," extract
that classification into a single shared function and have all three call it — otherwise they drift and
you get spurious cycles (over-add) or a lingering unbound-symbol bug (under-add). The `\`-operator
family, built-ins, and datatype constructors are never user logic symbols → never edges.

**`assigns` contributes essentially nothing.** Its targets are mutable locations (`x`, `self.f`, an
array region), not logic-function references. Include it for completeness, but ensure the collector
treats an `assigns` *target* as a frame location, never as a symbol dependency.

## Phase 2 — Merge edges and re-run SCC

Feed the union of body edges and contract edges into the existing Tarjan/SCC machinery — don't write a
second ordering pass, just enrich the graph the existing one consumes. This is deliberate: contract
references can legitimately create **new cycles** (a lemma's `ensures` mentions `f`, and `f`'s body
calls the lemma — a genuine mutual-recursion group the body-only graph couldn't see). The SCC pass
already groups cycles into `let rec … with …`, so mutual groups formed *through contracts* get correct
grouping for free — and, per Grounding, the emitter's keyword already keys off `_scc_size > 1`, so this
needs little to no emitter change.

Two things to verify explicitly:

- **Contract-only mutual groups are all-logic, so the group is well-typed.** A contract can only
  reference logic symbols (Phase 1's predicate), and logic symbols emit as `let [rec] function`. So a
  cycle closed purely by contract edges is a group of logic functions → `let rec function … with
  function …`, which is valid. (You cannot get an invalid mixed `let` / `let function` group, *because*
  the predicate excludes non-logic targets — which is also why getting that predicate right is the
  crux.)
- **The single-node self-cycle edge case.** A function whose *own contract* references itself is an SCC
  of size 1 with a self-loop; `_scc_size > 1` is false and `use_rec` is body-based, so it would mis-emit
  `let` instead of `let rec`. This is likely a non-existent case in practice, but make the single-node
  `rec` decision read the self-loop in the enriched graph (or the shared SCC signal), not body-only
  `is_recursive`, so it can't silently mismatch.

## Phase 3 — The byte-diff gate (the actual risk control)

This is where "byte-diff-risky" gets neutralized, so make it the gating mechanism rather than a fear.
Adding edges can only ever *constrain* the topological order further; it never removes constraints. So
for any existing file whose order already satisfied its contract dependencies, the new edges are
redundant and the emitted WhyML is **byte-identical**. Run the full corpus through the enriched ordering
and diff against the committed golden `.mlw`. Partition the results: byte-identical files (the large
majority, per Phase 0) prove no regression; changed files are exactly the ones previously correct by
luck (or latently broken).

**Make the "what may change" invariant a checkable assertion, not an eyeball check.** A *currently
compiling* file cannot contain a contract-only cycle — no linear order would satisfy it, so it wouldn't
have compiled. Therefore, for any previously-compiling file, the fix can only **reorder** declarations,
never **re-group** them (SCC membership is unchanged). Encode that: the Phase-0 diagnostic / Phase-3 gate
should *assert* "no SCC-membership change for any byte-changed file that previously compiled." A pure
reordering passing that assertion is expected and fine; an SCC-membership change on a
previously-compiling file is a collector bug (almost certainly over-adding edges), caught mechanically
rather than by reading each diff.

**Keep the tie-break out of this diff — it's a separate variable.** The current order is whatever Tarjan
produces over the source-ordered function list; it is *not* provably source-order for independent nodes.
Introducing explicit source-order tie-breaking can reorder files *by itself*, independent of any new
edge — which would conflate "edges moved it" with "tie-break moved it." So either (a) match the current
tie-break exactly (minimize churn, isolate the edge effect), or (b) land a source-order tie-break as its
**own** byte-diff-gated change *before* this one. Do not bundle the two; the gate is only meaningful if
it isolates one variable at a time.

## Unbundle: rejecting impure contract references is a *separate* decision

The instinct to also "reject a contract reference to a non-pure function" is reasonable but is **not
part of this fix and must not be bundled into it**. Today PyCSL *tolerates* such a reference by lowering
it to an abstract `val` (no edge, no order dependency — see Grounding), so the ordering fix is sound
without it. Turning it into a hard error is a behavior change with its own blast radius (files relying
on the abstract-`val` behavior would newly fail) and deserves its own Phase-0-style measurement and its
own gate. Keep the distinction crisp: the ordering fix only ever *adds edges for logic symbols*; it
never starts tolerating — or newly rejecting — impure contract calls.

## Phase 4 — Lock it with the P2 probe and a regression twin

Land the P2 quantified-fact wrapper that currently fails — the pure `ensures \forall x: Nat; to_int(x)
>= 0` wrapper with no body calls — as a PASS driver; it's the precise case the fix exists for. Add an
ordering twin too: a file where the contract dependency is the *only* thing forcing order, with the
referencing function placed *before* its referent in source, and confirm it still compiles. That twin
proves the edge (not source-order luck) is doing the work, and stops a future refactor from silently
regressing to body-only edges.

## Sequencing and why this order

Phase 0 first, because it converts "byte-diff-risky" from a vague fear into a known, enumerated set of
affected files — you cannot gate safely on a diff you haven't measured (and it forces you to build the
careful collector up front). Phases 1–2 are the actual fix and are small *given* a binder-aware,
purity-exact collector that reuses Module 4's walker and a shared logic-symbol predicate. Phase 3 is the
safety proof, with the SCC-membership assertion making it mechanical and the tie-break explicitly kept
out. Phase 4 makes it permanent. Doing Phase 0 before quantification P2 even starts de-risks the
critical-path item up front, and the smoothing it gives P3/P4 (whose contracts reference *more* logic
helpers, not fewer) comes along for free.

The single most important discipline running through all of it: **one shared "is this a logic symbol"
classifier**, consumed by the edge collector, the `rec`/`with` decision, and the emission decision
alike. The bug exists because the graph and the emitter currently use different notions of "depends on";
the fix is durable only if they are made to use the same one.
