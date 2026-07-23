# driver-backlog.md — the standing, PRE-AUTHORIZED escalation ladder for autonomous runs

The self-tcb-reduction-driver autonomous loop works THIS list, top-to-bottom, without stopping to
ask. Every item here is user-authorized for autonomous pursuit (including session-scale and
certificate-touching builds). The loop escalates to the next item when the cheaper work above it is
exhausted, and only STOPS at the deadline or when every item below is BROKEN / CERTIFIED-BOUNDARY.

**Authority (set by the user, 2026-07-24): FULL.** Auto-pursue every item, including
certificate-touching builds. The only things still gated per-instance are IRREVERSIBLE / OUTWARD
actions — `git push`, anything destructive/outward-facing — never the build/verify itself.

**Discipline that still applies to every item (non-negotiable):** spike-first + refutation-exit (a
wall that refutes is CERTIFIED-BOUNDARY, recorded, NOT ground on); lesson (p) census-first ("does an
existing certified capability already do this?" — enumerate the value models / recognizers before
scoping a new build); the full three-plane gate battery driver-verified fresh; ledger stays 3;
foreground-only sub-agents (lesson n). A checkpoint (commit + one line to
`getting-better/driver-progress.log`) marks each item transition — a breadcrumb, never a stop.

## Ladder (priority order — work top-down)

1. **Cheap drain (always first, §P).** Any `\trusted` stub a fresh census rates `cheap_win==true`.
   Re-run after every wall breaks (a break may unlock cheap follow-ons).

2. **Recognizer-reach extensions (bounded, low-ROI but real).**
   - set-membership + subject-first-param discriminant for `recognize_type_existence` → unblocks
     `_union_c8_test_references_union_var` (measured: ~1 stub; over-engineering-adjacent, do it only
     if item 1 is dry and nothing richer is ready).

3. **The structure-returning `Any`-walker class (session-scale, the big remaining vein).** The mirror
   is dominated by walkers that RETURN a string/dict/list (`_expr_to_whyml`, `_to_bool`, the
   `_build_method_*_ensures_map` family, the `visit_X` unparse family) rather than a bool. The
   bool-existence recognizer cannot model these. This needs a value-PRODUCING tree-transform model
   (not just existence). Spike whether the certified pyval/pydict/stmt_ir catamorphisms can carry a
   RETURNED value before scoping anything new (lesson p). Highest count-ROI if it opens.

   **CENSUS + SPIKE DONE (2026-07-23, count 971) — CERTIFIED-BOUNDARY for existing/minimal machinery.**
   - STEP-0 census (lesson p): **0 of the 8 clean candidates are reached by any existing recognizer**
     (`recognize_frt`/`sawalk`/`substmap`/`dictfold`/`setfold`). Demonstrated verbatim-porting
     `monomorphize._type_str`: the `Any` param lowers to `int` (default int-hash model), `typeof_op 422`
     reads a HASH CONSTANT (vacuous, lesson l), and the sibling call `_sanitize_type_name node` fails to
     typecheck (int-vs-string). The value-producing recognizers are each **bespoke to ONE live-method
     shape** over pydict/pyval and match none of the candidates.
   - STEP-1 spike: **NOT refuted.** A value-returning `: string` catamorphism over pyval proves
     non-vacuously — `emit_frt_group` already emits `find_return_type (stmts: list pyval) : string` that
     BUILDS a string from the tree (`str_concat_op "(" (str_join_arr ", " (Array.make nn "int")) ")"`,
     tuple arity `nn` read via real spine readers), variant-terminating, axiom-free, and it is un-`\trusted`
     + gated in the mirror. So provability is NOT the wall.
   - The real wall: the 8 candidates sit behind **four distinct un-built value carriers**, none a small
     extension to an existing recognizer:
       * Python **tuple / sexp** ADT (indexed `t[1]`, tag-at-`[0]`): `from_sexp._const_name`,
         `_ind_short_name`, `_binder_name` — reopen with a tuple value carrier.
       * **class-instance variant** ADT (`isinstance(t,Var)` + `t.name`/`node.left`): `emit_why3._pp`,
         `Module2_Parser._csl_to_str` — reopen with @dataclass/class→WhyML-variant model + faithful
         f-string interpolation of runtime strings + `str(int)`.
       * Python **`ast.*` node** hierarchy (`isinstance(x,ast.Subscript)`, `x.value.id`): M5
         `_normalize_literal_annotation`, `_encode_callable_annotation`, `_typeddict_field_type` — reopen
         with an `ast`-node value model (plus self-state mutation / `\trusted`-sibling calls / raise+encode).
       * **pyval-dict flat projection** (`_type_str`) + **runtime-string ops** (`ir_inline._global_call_target`:
         `partition(".")`, `"." in f`, `recv in globals_set`, `g_class[recv]`) — `_type_str` is the ONLY
         candidate on an existing carrier (pyval) but is a LONE stub (no cluster) needing a bespoke
         ~flat-projection recognizer; not worth a per-method build (§10.7 VALUE-not-count, lesson p).
   - Cluster measurement: 113 `str`- + 25 `Optional[str]`-returning `\trusted` stubs exist, but the
     population is **heterogeneous non-fold** (I/O `_find_coqc`, regex `_strip_rocq_comments`, self-state
     `errors.message`, string manip) — no single small recognizer unlocks a cluster. A worthwhile build
     is a per-carrier value model (biggest = the `ast.*` M5 family), gated by its own measure-before-build
     carrier census + authorization — NOT a bespoke per-stub recognizer. Fell through to item 4.

4. **The closure / nested-`def` walker family (dropped-closure blocker).** `_check`-style wrappers
   solved; the `found=[False]` / nested-`def` lambda-lift family (`_body_has_raise`,
   `_body_has_diverging_construct`, `_lemma_*`) still drops the closure at emission. Needs the
   emitter to recognize a nested-def existence walker whole. Spike-gate.

   **CENSUS + SPIKE DONE (2026-07-23, count 942) — CERTIFIED-BOUNDARY for existing/bounded machinery.**
   - STEP-0 census (lesson p): ported the LIVE closure body of `_body_has_raise` VERBATIM into the
     mirror (`found=[False]; def walk(node): ... for v in node.values(): walk(v)`), `--no-proof
     --keep-mlw`. **The closure is DROPPED at emission** and lowers input-blind/VACUOUS:
     `let _body_has_raise (body: int) : int = let found = Array.make 1 0 in let _ = walk body in ();
     found[0]` — `body` erased to `int` (default int-hash, no `list` value model), the nested `walk`
     lifted to a free/erased symbol, `found` a constant array. **No existing recognizer fires on the
     nested-def `found=[False]` closure.** Blocker = nested-`def` lambda-lift drops the walk AND the
     mutable-closure idiom erases the subject to int. (The already-converted sibling `_body_has_return`
     right below emits the certified `stmt_ir` catamorphism — it was flat-rewritten live+mirror to the
     `recognize_stmt_has` shape; that is the ONLY working precedent for this family.)
   - STEP-1 spike (recognize the nested-def walker as a WHOLE) = a nested-`def` + mutable-closure
     lowering SUBSYSTEM = **session-scale**. The bypass (flat-rewrite to `recognize_stmt_has`, the
     `_body_has_return` precedent) reaches AT MOST `_body_has_raise` and even that is CERTIFICATE-COUPLED:
     the certified `stmt_ir` ADT (WhyML preamble + Lean `StmtIR.lean` + Rocq `Phase2d_StmtIR.v`, w/
     round-trip completeness + tag-distinctness theorems) has **no `SRaise` constructor** — "Raise" is
     not in `_STMT_LEAF_TAG_CTOR`/`_STMT_COMPOUND` and cannot be, so the typed catamorphism can't return
     `SRaise -> true`. The other 9 of 10 are each SEPARATELY blocked, so SRaise unlocks 1, not the cluster:
       * `_body_has_diverging_construct` — detects `type=="Call"` in EXPRESSION positions; the stmt_ir
         catamorphism deliberately does NOT descend into `emit_ir` expr children, so the typed route
         structurally cannot see it; plus a compound multi-tag+`type` discriminant. Needs generic-expr descent.
       * `_lemma_returns_value` — needs the `SReturn` `iropt_ir` PAYLOAD guard (value present & non-`None`);
         the catamorphism arm `SReturn _ -> true` discards the payload. Not expressible as-is.
       * `_returns_string_seq` / `_func_returns_string_seq` — self-state `_seq_value_types` map read +
         string-element value model.
       * `_is_linear_expr` — an AND-fold (universal) expression whitelist over `emit_ir`, not an
         existence-OR walk; different algebra.
       * `_has_set_op_on_map` — self-state map-locals + `_rhs_yields_map`/`_test_contains_map` sibling
         calls + compound discriminants.
       * `_should_auto_trust_tuple_return` — self-state `array_vars` + `IRScanner` + nested tuple-slot walk.
   - VALUE verdict (lesson 7 / §10.5): even the certificate-coupled `SRaise` build (WhyML preamble +
     both certs + round-trip/distinctness re-proof + the `emit_ir`→`stmt_ir` marshalling) unlocks exactly
     1 of 10; it does NOT open the cluster. Not worth a both-prover ADT extension for a lone marker.
     **Reopening capabilities (record for a future ladder edit):**
     (R1) a nested-`def`+mutable-closure (`found=[False]`) existence-walker RECOGNIZER that lifts
     `def f(root): found=[False]; def walk(x): if <cond>: found[0]=True; <descend>; walk(root);
     return found[0]` WHOLE onto the certified `emit_bool_existence_group` (pyval) / `emit_stmt_has_group`
     (stmt_ir) target — the pyval route is the natural carrier because its `__d` already generically
     descends ALL dict values (incl. expr children); (R2) `SRaise` added to the certified stmt_ir ADT
     (axiom-free co-landing cert) for the "Raise" tag; (R3) generic-EXPRESSION-position Call detection +
     compound multi-tag/`type` discriminant → `_body_has_diverging_construct`; (R4) an `SReturn`
     iropt-payload predicate → `_lemma_returns_value`; (R5) self-state map/dict value-model threading
     (`_seq_value_types`, map-locals) → the auto_trust/functions self-state members.
     Fell through to item 5.

5. **R2c — contract-grammar genexp** (`#@ assert all(x >= 0 for x in a)` does not parse). Repairs the
   spec plane of the any/all fold. Independent of R2d/R2e. Grammar work in `Module2_Parser.py`; may
   be its own subsystem — SPLIT and record if so.

6. **R2e — string/capture folds** (element-type parameterization + string-predicate lowering +
   closure-capture threading + `startswith`). 4 coordinated capabilities; clears
   `_handle_fieldassign_stmt` + `_union_arm_tag` (~2 sites) + 11 banked. Session-scale.

7. **The 3 session-scale vacuity residuals** (`_emit_new_ghost_ref`, `_handle_mktuple_expr`,
   `_collect_class_constants`) — each erases a param that flows only into a `\trusted` sibling; needs
   the sibling converted + a value-model feature (e.g. set-param-by-reference). Also the live-tool
   `Set[str].add(param)→()` faithfulness bug (lesson h family) — a real all-users fix worth doing
   under item 7.

8. **Soundness/gate hardening (do opportunistically, never a reason to stop).** The self-state vacuity
   gate's LOWER-BOUND partials; a `check-self-annotate-sync.sh` audit; the 5 flagged judgment-call
   lessons (i,k,g,j',m) carve-outs. Small, bounded, always-available filler between walls.

## Exhaustion = STOP (the ONLY early-stop condition now)
The loop stops before the deadline ONLY when items 1–8 are each BROKEN or CERTIFIED-BOUNDARY for the
current tree — a genuinely empty ladder. "Bounded work ran out" is NOT a stop condition; escalate to
the next session-scale item instead. When you DO record a CERTIFIED-BOUNDARY, note what NEW capability
would reopen it, so a future run (or a future ladder edit) can pick it back up.
