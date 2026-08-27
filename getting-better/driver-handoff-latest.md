# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-27, RELAUNCH #3 worker)

## State, verified from the surface at the end of this window

- Directive count **619** (`grep -rcF '#@ \trusted' src/self-annotate/src --include=*.py`,
  summed). Window delta **626 -> 619**, SEVEN conversions plus TWO count-neutral faithfulness
  repairs. Confirm it yourself before quoting it.
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

## What this window did (continued past the first handoff draft — read all of it)

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

ALSO LANDED after that: **the rest of the L2 cluster REFUTED** with the wall measured exactly
(a TYPE-UNIFICATION wall, not the dispatch expansion — see the backlog); `_py_op_to_str`
CONVERTED via a new type-keyed dispatch-table capability; the `field_names` erasure fixed
(the last removable `KNOWN_ERASURES` entry); the `check-emitted-vacuity` `v_`-rename blind
spot repaired; and a **NEW INTEGRITY GATE**, `bin/check-untrusted-emitted.py`.

## The single most important thing this window learned

**L3-tc ✓ IS NOT A CONVERSION CRITERION.** Removing a `#@ \trusted` marker verifies nothing
by itself: the AUTO-TRUST SAFETY VALVE silently re-abstracts a body the emitter cannot lower
into an opaque `val`, and the file still type-checks AND still proves. Measured: **17
candidate stubs passed L3-tc after un-trusting and NOT ONE was emitted as a definition** — 6
dropped entirely, 11 re-abstracted. All 17 would have been vacuous conversions. This both
explains and VINDICATES the earlier windows' "no cheap conversion remains": an L3-tc-only
probe over-reports massively. **Any candidate probe you run MUST also check that the function
is emitted as a `let` / `let rec` / `with` member.** `bin/check-untrusted-emitted.py` is that
check; its baseline is **716 un-trusted · 699 definitions · 0 re-abstracted · 0 absent**, so
the booked conversions are clean. Re-run it after any batch.

Second: **when a gate over an EMITTED artifact reports a defect, FIRST ask whether the
emitter RENAMED the thing.** Four for four this window — `with`-members read as non-definitions,
blank lines before a `def` hiding a `\trusted` marker, the `v_` param rename, and recognizer
cluster renaming (`_conc_*` -> `conc__*`). Every one manufactured a defect that did not exist,
and I published one of them before catching it.

## Pick up here

1. **The `pyast_expr` ADT unification** — now the top lever, and its size is MEASURED (see
   `driver-backlog.md` §"L2 REST-OF-CLUSTER"). `_py_expr_to_ir` / `_py_stmts_to_ir` /
   `_csl_to_ir` are blocked BEFORE the dispatch expansion by a type-unification wall: the
   dispatcher is `emit_ir -> emit_ir` but its 23 handlers take 21 DISTINCT RECORD types (14
   more on the statement side), and there is no projection from `emit_ir` to `name`, so the
   expanded chain is UNWRITABLE, not merely unprovable. The certified `pyast_stmt` ADT does
   NOT help — grep confirms ZERO handlers take it. This is COST/SCALE, not a floor, and a
   funded window is the budget for it. Its prerequisite (the deferred-goal fix for
   mutually-recursive union-using SCCs) LANDED this window. Do NOT attempt the dispatch
   expansion first.
2. The cheap-candidate frontier is CLOSED, and now for a measured reason rather than an
   assertion: 17 of 62 small stubs pass L3-tc and NONE is emitted as a definition. Do not
   re-run an L3-tc-only census.
3. `proof2why3/parser.py` still has four module-level `\trusted` functions. `lex` and
   `normalize_surface` are string-scanner facades already STRUCK as a CERTIFIED-BOUNDARY —
   do NOT re-litigate them. `parse_type_expr` needs mutable-object construction, try/except
   over two exception types, and `str(exc)`; it is not cheap.
4. The named COST/SCALE residue from the §A.3 re-classification, which is NOT a floor and
   which a funded window is exactly the budget for: the larger multi-variant certificate
   bundle (Act/Complete/Disjoint/ForExpand + value-model), and the review-gated
   giant/dispatcher decompositions (`run_ir_semantic_checks`, `_csl_to_ir` getattr-dispatch).
   "Review-gated" means run Gate R yourself — it does NOT mean ask the user.
5. The vacuity/erasure surface is now CLEAN and should stay that way:
   `check-emitted-vacuity.py --emit` is GREEN (0 input-blind, 0 new, 6 known and each
   individually justified). The remaining 6 are error-message-only erasures (faithful) plus
   two documented modeling gaps (`_handle_mktuple_expr`/`lr`, `_emit_new_ghost_ref`/`target`
   — the wall-lessons (h) param-collection-mutation family).
6. Named but not built: the **κ-inference gap** behind the `field_names` shape-gate — Module
   5 cannot see through an `Optional[str]` union-local carrier projection to conclude
   "string key". Closing it retires that shape-gate and likely others.

## Gates you now have that earlier windows did not

- `bin/check-untrusted-emitted.py` — is every un-trusted mirror function ACTUALLY EMITTED as
  a definition? Baseline 716/699/0/0, GREEN. Run it after any batch of conversions.
- `bin/check-emitted-vacuity.py --emit` — now free of the `v_` param-rename blind spot (which
  had BOTH hidden real erasures in check (1) and manufactured two false INPUT-BLIND findings
  in check (2)). GREEN.

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
