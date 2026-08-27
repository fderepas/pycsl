# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-27, RELAUNCH #3 worker)

## State, verified from the surface at the end of this window

- Directive count **620** (`grep -rcF '#@ \trusted' src/self-annotate/src --include=*.py`,
  summed). Window delta **626 -> 620**, six conversions plus one count-neutral faithfulness
  repair. Confirm it yourself before quoting it.
- Ledger **3**, untouched all window. No new axiom, no new abstract val.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`,
  `src/formal-semantics/rocq/.lia.cache` + `Phase2j_*` build artifacts, untracked
  `prompt.txt`/`style.css`/`scratchpad/`). None of it is mine; leave it alone.
- `getting-better/.driver-deadline` is intact. Do not touch it.

## Three instrument facts that will silently corrupt your gates. Read before running anything.

1. **`why3` is NOT on the default PATH.** It is at `/home/fabrice/.opam/framac-coq8/bin/why3`.
   Without it `pycsl.py` prints `[!] ERROR: 'why3' command not found` **and exits 0** — a
   false green. Start every gate with
   `export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH`. (Lesson (aa).)
2. **The canonical mirror import path is `--import-path src/pycsl`**, NOT
   `src/self-annotate/src`. `bin/run-self-annotation-suite.sh:27` is the authority, and it
   matters: `frontend/Module5_IREmitter.py` L3-tc FAILS under the mirror path and PASSES
   under the canonical one. (Lesson (cc).)
3. **The prover pin is still stale and still halves every gate.** `pycsl.py:1318` names
   `Alt-Ergo,2.6.2,`; 2.6.3 is installed. Pass `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'`
   EXPLICITLY on every proof you rely on. Do NOT edit the pin — it stays on the
   flagged-for-USER list. Also: `check-emitted-vacuity.py` is a false green without `--emit`.

Plus one argument that has gone stale: **"gated on @mutable_state, therefore corpus
byte-inert" is NO LONGER TRUE** — corpus programs 0925/0926/0927/0928 all declare it. Run
the byte-diff sweep; do not argue your way out of it. (Lesson (bb).)

## What this window did

**L13 IS CLOSED.** The `proof2why3._Parser` cursor nest — the top lever since relaunch #23 —
is FULLY CONVERTED: eleven members, zero `\trusted` methods in the class, and all five
ASSUMED monotonicity clauses RETIRED (each became a proved postcondition when its stub was
converted). Parser-mirror proof goals went 216 -> 438, every step driver-measured, corpus
byte-diff 0 over 813/813 at every step.

Also BROKEN: ladder item 2, the **`0`-reads-as-`None`** faithfulness bug in
`Module5_IREmitter::_collect_class_constants`. Count-neutral by design (a repair to an
already-converted body, same shape as the L14 frame repair): one opaque `val … : int` left
the model and one facade guard became the real None test.

Eleven capabilities were built and four LATENT EMITTER DEFECTS fixed. **Read
`driver-backlog.md` §L13-CLOSED before scoping anything** — several of the capabilities are
general (list-term/list-string ctor slots, term ctor discriminant + unique-arm payload
projection, union-returning-call guard/projection, the `_union_*` param-registry repair, and
the deferred-goal fix for mutually recursive union-using SCCs), and lesson (p) says census
them before building.

## Pick up here

1. **Re-census the value-model frontier with the eleven new capabilities in hand.** This is
   the highest-value next move and it is cheap: several previously-refuted targets were
   blocked on exactly what now exists. Census FIRST, do not build.
2. `proof2why3/parser.py` still has four module-level `\trusted` functions. `lex` and
   `normalize_surface` are string-scanner facades already STRUCK as a CERTIFIED-BOUNDARY —
   do NOT re-litigate them. `parse_type_expr` is a thin driver and may be cheap.
3. The named COST/SCALE residue from the §A.3 re-classification, which is NOT a floor and
   which a funded window is exactly the budget for: the larger multi-variant certificate
   bundle (Act/Complete/Disjoint/ForExpand + value-model), and the review-gated
   giant/dispatcher decompositions (`run_ir_semantic_checks`, `_csl_to_ir` getattr-dispatch).
   "Review-gated" means run Gate R yourself — it does NOT mean ask the user.
4. Worth a window of its own, found in passing and NOT chased:
   `check-emitted-vacuity.py --emit` reports a NEW erasure in
   `Module3_Weaver::_const_int`, two INPUT-BLIND methods in `functions.mlw`, and six stale
   KNOWN_ERASURES entries.

## Method notes this window paid for

- **Emit-and-diff BEFORE you prove** (lesson r) — the mirror emission diff scoped every
  re-proof set this window to 1 or 2 files out of 52.
- **A timeout is not a scale wall until the shape blows up in ISOLATION** (lesson ee). ~40
  goals timed out at 280-370M steps, looking exactly like the documented `list.List`
  explosion; two controlled probes showed the real cause was two missing loop annotations.
- **Host a new helper in a live function whose mirror counterpart is `\trusted`** (lesson dd).
  Otherwise §10.4 forces a verbatim re-port and the unported helper becomes an int-typed
  auto-trusted val that breaks L3-tc.
- **`isinstance_op 0 0` in an emitted body is a facade detector** (lesson ff).
- The **§10.4 re-port obligation is live and it caught a real omission again** — my mirror
  `parse_atom` had dropped an f-string from a `raise`. The fidelity plane is not a formality.

Standing discipline unchanged: demand-first bundling (capability-first is REFUTED); close a
blocker set by ITERATED measurement until L3-tc PASSES; spike-first with a refutation exit;
census-first; the three L-planes driver-verified FRESH; ledger stays 3; a gate you have not
confirmed non-vacuous is not a gate.
