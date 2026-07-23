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
         `_ind_short_name`, `_binder_name` — **CERTIFIED-BOUNDARY (2026-07-24, sexp-carrier-impl.md
         §OUTCOME).** Both spikes re-verified axiom-free by the driver (SexpCert.v coqc 8.20.1 "Closed
         under the global context" ×3; sexp.mlw z3 pos Valid / evil Timeout / nth1 Valid), so
         PROVABILITY is not the wall. The RECOGNIZER walls: the verbatim bodies use heterogeneous
         positional index `t[i]` consumed as BOTH string (`return inner[1]`, `out.append(iid[1])`) and
         sub-sexp (`_walk_modpath(mp[1])`) at the same syntactic form (BLOCKER 1 — needs consuming-
         context-directed `atom_of` coercion the emitter's emit_ir-node-only subscript lowering lacks),
         the helpers build a `List[str]` result via `.append`/`.extend`/`reversed`+for-over-slist that
         the `last_atom` oracle sidesteps (BLOCKER 2), plus string-tag dispatch/`len>=3` guards
         (BLOCKER 3). REOPEN needs a bespoke sexp recognizer = 3 new features for net −3 (session-scale,
         §10.3 generic-Any class). Cert + value oracle banked in getting-better/sexp-carrier-oracles/.
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

**AST-NODE CARRIER SIZED (2026-07-23, count 942):** 47 `\trusted` stubs dispatch on `isinstance(_,ast.*)`
   (24 in Module5_IREmitter, 14 in Module3_Weaver). BUT the top users are HEAVY transforms —
   `_build_function_symbol_table` (30 ast-dispatches → 3-tuple of dicts), `_build_function_ir`,
   `visit_Module`, `_synthesize_*` — i.e. the emitter's core AST→IR construction. A faithful `ast`-node
   value model for these is re-implementing the emitter in WhyML, the campaign's DEEPEST wall (§10.3
   int-AST / generic-Any), NOT a bounded carrier. So the biggest cluster is the least tractable. The
   TRACTABLE carriers remain the small ones (tuple/sexp: 3 from_sexp stubs; class-variant: 2). Deprioritize
   the ast-node model until a small carrier proves the certificate+emitter pattern is repeatable in-window.

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

   **BUILT (2026-07-23, count 942 unchanged — spec-plane integrity, count-neutral by design).**
   NOT its own subsystem: a genexp arg to `all`/`any` inside a `#@` clause desugars to the ALREADY-
   CERTIFIED bounded quantifier. `all(P for x in dom)` builds exactly the CSLNode `\forall x in dom; P`
   builds (via `_mk_in`, quantification.md P3); `any(...)` builds `\exists x in dom; P`. So the IR,
   lowering, AND 3-axiom certificate are ENTIRELY reused — no new value model, no new lowering path.
   - Grammar: ONE branch in `_ContractParser._parse_atom_name` (`src/pycsl/frontend/Module2_Parser.py`) —
     when `name in ("all","any")` and a `for` follows the first expr, parse `for VAR in DOMAIN`, close
     `)`, emit `Forall`/`Exists` via `_mk_in`. A non-genexp `all(arr)`/`any(arr)` keeps the CallExpr path.
   - SPIKE (STEP 1) PASSED: `#@ assert all(x >= 0 for x in a)` now (a) PARSES, (b) lowers to a real
     `forall x. (exists m. 0<=m<len(a) /\ a[m]=x) -> x>=0` — grep 0 `all_1`/`any_1` oracle in the emitted
     .mlw, (c) proves a POSITIVE fixture and the EVIL TWIN (`all(x>=5 ...)` under `a[i]>=0`) does NOT
     prove (lesson l). The genexp `.mlw` is BYTE-IDENTICAL to the hand-written `\forall x in a; P`.
   - Fixtures (git add -f): `0938_spec_genexp_all_any.py` (positive `all`+`any` asserts, PROVE) +
     `0939_spec_genexp_evil_twin.py` (`# pycsl-expected: FAIL`, MUST NOT prove). Also fixed the
     PRE-EXISTING red `0937` (R2b's evil twin lacked the `# pycsl-expected: FAIL` marker → spurious FAIL;
     comment-only, emission byte-identical) — opportunistic gate hardening (item 8).
   - GATES (all fresh, driver-verified): corpus byte-diff 0 over 784 existing files (base 784 / mine 786
     = +2 new fixtures, 0 existing differ, detached-HEAD worktree); mirror-check 52/52; L3-tc 52/52;
     ALL 52 mirror `.mlw` emission BYTE-IDENTICAL to HEAD ⇒ self-annotation proof suite provably
     unaffected (identical WhyML ⇒ identical proof); sync drift 5 == HEAD; ledger 3 (no cert/allowlist/
     formal-semantics touched); count 942 unchanged (correct — spec-plane repair does not lower the
     count). Fell through to item 6.

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
   - **STATUS 2026-07-23 — fidelity-drift repair, 5 DIVERGED → 4 (1 verified re-port, 4 STILL-BLOCKED).**
     The §10.4 fidelity gate was RED with 5 un-`\trusted` mirror methods proving stale bodies. Per-drift
     verbatim re-port + full gate:
     - `_handle_return_stmt` (stmt_control_flow) — **RE-PORTED & VERIFIED** (commit, drift 5→4). Added the
       `_pyval_seq_locals` return branch, the `emit_ir`/`_union_` raise branches, the tail bool→int block.
       `--fun` SUCCESS (13 goals all Valid, ~3m46s); L3-tc whole-file ✓; emitted body faithful (dispatches
       on real `func_ret` tags, references `val_ir`/`py_val`, no `any_1`); vacuity no-NEW-erasure/0-input-blind;
       mirror-check 52/52; count-neutral 942; mirror-only (byte-diff 0 by construction).
     - `_pattern_has_constructor` — **STILL-BLOCKED (vacuous).** Verbatim `any(genexp)` lowers to
       `any_1 (Array.make 1 0)` (wall-lesson l facade). The new `recognize_type_existence`/`recognize_bool_existence`
       do NOT cover this shape (recursion over a named list FIELD `alternatives` via a `self._method` call,
       dispatch on a non-`type` tag `pattern`). Missing cap: a recognizer for `any(self._pred(a) for a in
       node.get("<field>",[]))` recursive-existence-over-list-field. Committed body stays the (lesson-j)
       while-loop rewrite — flag for re-trust vs recognizer build.
     - `_union_arm_whyml_type` — **STILL-BLOCKED, but RE-DIAGNOSED 2026-07-24 (narrower than thought).**
       The prior "missing cap: nested string-field projection" was WRONG. With the field annotated
       `_record_types: Dict[str,Dict[str,str]]` AND the intermediate local annotated `_rt: Dict[str,str]`
       (both mirror-only, sync-gate drops local annotations), BOTH projections lower FAITHFULLY —
       `_rt := (match Map.get self._record_types tag with Some v_ -> v_ | None -> const None end)` (real
       outer map get) and `match Map.get !_rt "whyml_name" with Some v_ -> v_ | None -> "" end` (real inner
       STRING projection, NO int-hash, NO opaque `subscript_get`/`_rt_get_str`). The residual blocker is
       DIFFERENT and smaller: the verbatim body binds `_rt = getattr(...).get(tag)` in the early-return→
       if-else ELSE branch, so the emitter HOISTS it as `let _rt = ref 0 in` (int default, statements.py
       `_emit_body_code` `pfx="0"`), and `_rt := <map string (option string)>` fails L3-tc "expected int".
       The map/dict typed-local classifiers (`find_array_and_dict_vars`, `_rhs_yields_map`) are RHS-pattern-
       driven and don't recognize `.get(tag)`, and there is NO symbol-table-driven map-local classifier
       (unlike `string_vars`/`_union_locals` which DO read `_current_symbol_table`). Since all `_rt` uses are
       inside the else branch, a let-bind there would typecheck. **Missing cap = a byte-inert emitter
       recognizer: classify a local whose symtab type is a nested string-map as a typed local (let-bound at
       first assign / pre-declared `ref (const None)`), the map analogue of the existing `ref ""` string and
       `ref (IrOther "")` emit_ir pre-decls.** That is a src/pycsl edit (out of this mirror-only task's scope),
       but bounded and count-moving — a candidate menu-B build. The driver's spike (`d[tag]["whyml_name"]`,
       direct double-subscript on a plain local) genuinely lowers, but does NOT exercise the verbatim body's
       hoisted guard-local `_rt` — which is the real wall.
     - `_handle_var_expr` (expressions) — **STILL-BLOCKED (genuinely heterogeneous, confirmed 2026-07-24).**
       Needs helper `_union_local_read_projection`, whose verbatim body reads nested
       `_variant_types[st]["constructors"][cn]["arity"/"payload"]`. Unlike `_union_arm_whyml_type`, this read
       is genuinely HETEROGENEOUS and NOT annotatable to a faithful map: it iterates `constructors.items()`
       in a find-loop with mutable accumulators (`some_ctor`, `some_pay`), compares `c.get("arity") == 1`
       (INT), and indexes `c.get("payload") or []` then `_pay[0]` (LIST → str). No single carrier
       (`Dict[str,Dict[str,str]]` fails on `arity`/`payload`; a pyval carrier can't do the `.items()` find-loop
       + list-index in VALUE position). This is squarely the generic-`Any` recognizer wall (§10.3 / lesson q):
       multiple recognizer features (dict-items find-loop, heterogeneous constructor record, list-payload
       projection), all emitter-side. Adding the helper `\trusted` would be a +1 regression.
     - `_handle_for_stmt` — **STILL-BLOCKED (missing subsystem).** Verbatim body needs ~12 helpers absent from
       the mirror (`_string_char_iter`, `_classbody_psl_recv`, `_pyast_walk_recv`, `_keyword_iter_recv`,
       `_tparam_iter_recv`, `_mktuple_elts_recv_ir`, `_tparam_bases_recv`, `_add_abstract_op`) + 5 new self-state
       fields + a widened frame; the string-char-iter / pyast-stmt / keyword / tparam ADT-reflection is the V1/V2
       census wall. Supplying stubs would raise the count (forbidden).
     Net: fidelity gate greener (5→4), count-neutral 942, tree clean, no axiom. The 4 residuals are the V1
     `Dict[str,Any]`/genexp-list-field value-model wall (census-known), not a bounded transcription backlog.

## Exhaustion = STOP (the ONLY early-stop condition now)
The loop stops before the deadline ONLY when items 1–8 are each BROKEN or CERTIFIED-BOUNDARY for the
current tree — a genuinely empty ladder. "Bounded work ran out" is NOT a stop condition; escalate to
the next session-scale item instead. When you DO record a CERTIFIED-BOUNDARY, note what NEW capability
would reopen it, so a future run (or a future ladder edit) can pick it back up.
