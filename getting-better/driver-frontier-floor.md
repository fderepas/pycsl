# Driver frontier — count 874 (2026-07-27/29; trio-fusion wall BROKEN, user-authorized)

The self-tcb-reduction-driver reached its **autonomous floor at 875** this run (883→875, 8 conversions).
Established NOT by assumption but by draining all safe-additive work AND build-attempting/spiking EVERY
remaining in-scope vein. Each remaining path requires user input (review-gated / authorization) or is a
correctness floor. This is the A.3 "frontier at floor" state — the loop should idle (heartbeat alive),
NOT re-probe these characterized walls (that only burns the clock).

## What was converted this run (all independently re-verified: §10c all-7 importers + corpus byte-diff 0 + whole-file proof + vacuity + ledger 3)
- Parser vein (6): `_parse_mixin_type`, `_parse_opt_except`, `_parse_impl_rhs`/`_or_rhs`/`_and_rhs` — banked `str_join_seq`/`\variant`/faithful-monotonicity machinery.
- Additive walker vein (2): `_gso_walk` (recognize_cpwalk sibling guard), `_cp_walk` + `_pb_expr` (bespoke recognizers reusing the certified pyval/pydict catamorphism, multi-feature, byte-inert, NO new cert).

## The frontier at 875 — every remaining path, MEASURED
| Vein / stub class | Status | Why it needs USER INPUT (not autonomous) |
|---|---|---|
| walker-FUSION (`_pb_stmt`/`_cs_stmt`) | **feasible-in-isolation, whole-file WALL** | Fusion emitter BUILT + passes byte-diff 0 / §10c all-7 / vacuity; whole-file proof fails on 1 VC (`_pb_stmt__body'vc` postcond, Timeout 32.6M steps) = **E-matching saturation over recursive `wf_dict`/`wf_ir_binds` in the full-file context**. Local asserts don't help. Needs **MODULAR VERIFICATION** (prove the trio in a separate module / restrict wf_* triggers) → touches the **§10.10 whole-file-proof gate = REVIEW-GATED**. The fusion emitter code is validated + banked for that session. |
| string-keyed set-membership (`handler_catches`, `subclasses_of`, `all_phase1_exceptions`, `classify`) | **build-attempted → front-end κ-gap WALL** | FULL build-attempted (2026-07-27, not just spiked): GATE S refuted. The membership `handler_exc in bases_closure(raised_exc)` needs `bases_closure`'s bare `-> frozenset` return retyped `map string`, which needs a string-κ signal — and ALL THREE fail: no `frozenset[str]` annotation; `.add(b)` has `b` typed "Any" (empirically confirmed: `_build_function_symbol_table(bases_closure)` gives `dict_key_types={}`) through a 4-hop `EXCEPTION_BASES`(module-const `Dict[str,Tuple]`)→`.get()`→`list()`→`.pop()` chain the scope inference doesn't track; no return element type. Recovering κ = a NEW front-end **module-constant→collection-element dataflow-propagation** feature (3-4 sub-features, facade-risk). NOT corpus-perturbing, NOT needs-cert, NOT saturation — but needs that front-end signal build (review-gated for facade-risk). Whole `exception_model` frozenset cluster shares this one boundary. |
| string-op (`.strip`/`.startswith`/`.split`/`.rpartition`) | boundary | Faithful str theory gated on `_is_string_expr(receiver)`, never fires for `List[str]` generic-iteration → emits vacuous. Pure `str→str` leaves use regex (**correctness-floor**); `List[str]` leaves need corpus-perturbing live-emitter builds; IR-string leaves hit the Dict[str,Any] wall. |
| heterogeneous `Dict[str,Any]` V1 / family-B `emit_ir` node-ctors / char-lexer | **needs authorization** | Each needs a NEW WhyML value shape + a co-landing axiom-free `src/formal-semantics/` cert (§10.5 coupling) → touches `src/formal-semantics` = authorize first. ~10 CSL classes have no `emit_ir` counterpart. |
| trusted-val `#@ assigns self.field` frames | boundary (soundness) | Trusted vals emit effect-free (drop the declared frame); some "verified" siblings green only because of it. Faithful fix needs a multi-method campaign (strengthen callee `ensures` + make fields mutable record fields). See `trusted-val-assigns-writes-wall.md`. |
| `str_to_int` / `int(<str>)` oracle, regex | **CORRECTNESS floor** | Faithful lowering needs a 4th cited axiom / a regex theory; the unsound `str_to_int` oracle is forbidden (no-more-int). Cannot be built at ledger 3. Leave-trusted. |

## Authorizable next campaigns (ranked; each needs a user go-ahead)
1. **Modular-proof for the trio-fusion** — the emitter is built + validated; the only gap is escaping whole-file E-matching saturation via modular verification. Touches §10.10 (review-gated). Unblocks `_pb_stmt`→`_cs_stmt` chain. HIGHEST-value, LOWEST-new-code (emitter done).
2. **String-keyed-set model** — Module5 frozenset-κ inference + emitter frozenset-return + module-call `in`-membership. Byte-inert, no cert. Unblocks the exception_model/import_classifier cluster.
3. **New value-shape + cert builds** (Dict[str,Any] V1 / family-B node ADTs / char-lexer) — each a §10.5 co-landing cert build.
4. **`str_to_int` doctrine call** — the one no-more-int correctness decision (needs the user's ruling).

Ledger held at 3 throughout; drift 2 (pre-existing `_handle_var_expr`/`_handle_for_stmt`); zero live-parser
behavioral changes; nothing pushed.

## UPDATE 2026-07-29 — trio-fusion wall BROKEN (user authorized campaign 1), count 875→874
`_pb_stmt` CONVERTED via the reconstructed trio-fusion + a SOUND extraction-helper fix (commit 2fbff96c).
The two prior diagnoses were BOTH refuted by measurement: (a) it is NOT a modular-verification necessity;
(b) it is NOT wf_dict/wf_ir_binds E-matching (removing wf_ir_binds left the failing goal's step count
unchanged ~92.9k) — the real cause was generic full-module context size on the extraction-helper size VC.
Sound fix: shared recursive `_pb_stmt__dget : pydict -> option pyval` with a `pv_size` postcondition
(Z3 0.05s) + a non-recursive list-extractor wrapper. No axiom, no weakened goal, corpus byte-diff 0.
Whole-file proof: 449 Valid, 0 unproven. NEXT FOLLOW-ON: `_cs_stmt` (same fusion pattern with
_cs_body/_cs_descend) — but it cross-calls the still-trusted `_cs_clause` (a set-consumer over
`_ir_free_vars`), so it may need `_cs_clause`/`_ir_free_vars` handled first.

## UPDATE 2026-07-31 (cont.) — _cs_stmt chain BROKEN (user authorized), count 874→871
The `_cs_stmt` follow-on landed as a 3-conversion chain, all with EXISTING machinery (no new cert,
ledger 3): `_ir_free_vars` (set-union fold → the existing `map string bool` set model; commit 24b663e0),
`_cs_clause` (set-consumer: _contains_result guard + StrSet.mem double-membership + raise), and `_cs_stmt`
(the `{_cs_stmt,_cs_body,_cs_descend}` trio-fusion reusing the proven emit_pb_trio_group recipe;
commit 009f4384). `_cs_clause` erases `ctx` (error-message-only) — added to check-emitted-vacuity.py
KNOWN_ERASURES as FAITHFUL-by-semantics (WhyML matches exceptions by type, not message). Whole-file proof
SUCCESS, byte-diff 0, §10c all-7 ✓, vacuity 0. Both walker trios (_pb + _cs) now proven — the
structured-dispatcher wall is fully cleared. Run total this session: 883→871 (12 conversions).

## UPDATE 2026-08-01 — heterogeneous-func campaign DRAINED to autonomous floor at 855
User-authorized "trio-fusion modular proof" (2026-07-31) snowballed into breaking the heterogeneous
Dict[str,Any] "V1 wall" (in-scope via a pydict->sdict bridge, NO cert — a cert-need spike proved the
primitive with existing certified shapes) and draining most of the core_ir_semantic orchestrator
cluster. Session total: 883 -> 855 = **28 conversions**, 3 walls broken (_pb trio, _cs trio,
heterogeneous-func V1), 1 vacuous facade REMOVED (the lambda-lifted int-erased closure `walk`).
Ledger held at 3 throughout; every increment whole-file-proof + §10c all-7 + corpus-byte-diff-0 verified.
KEY REUSABLE MACHINERY BANKED (all in generic_fold.py, no cert): pydict->sdict bridge; the trio-fusion
emitter (emit_pb_trio_group, {size,phase} variant + shared pv_size extractor); recognizers for
body-walk / clause-fold / field-guard-raise / guard-cascade / no_exception(literal-set) /
closure-existence bool-fold / lemma string-search + map-string-bool SET-PARAM / check_lemma / warn-fold
(warnings.warn = unmodelled no-op side-channel). Converted callers: _check_contract_exprs, _checkpoints,
_ghost_string_ops, _subscript_assignments, _contract_scope, _span, _mutable_defaults, _assigns_regions,
_no_exception, _check_diverges, _check_lemma, _check_union_gt1 (+ predicates _ir_free_vars, _cs_clause,
_body_has_diverging_construct, _lemma_returns_value, _lemma_calls_trusted, _body_has_raise, _sa_immutable_walk).

## AUTONOMOUS FLOOR at 855 — remaining tail is feature/authorization-gated (measured per-stub)
- `_check_happy` (NEXT-CHEAPEST, authorize deliberately) — needs a fused set-collect (_hp_collect_written over ir["functions"]) + guard-cascade+warn over happy["properties"] = a multi-shape build.
- `_check_acts` — local `defined` DICT-accumulator + `referenced` set built in-body (new pattern).
- `_check_class_invariants` — ir `type_decls` fold + set-builder + sorted(genexp); no ir-typedecl-fold recognizer.
- `_check_mutex_invariants` / `_check_callable_params` — string-PARSING (.split/.partition/.isidentifier) = string-op wall.
- `_check_final*` / `_check_concurrency*` / `_check_typeddict_access*` / `_check_namedtuple_access*` / `_check_union_narrowing*` / `_check_noreturn_successors*` — mutually-trusted HELPER CLUSTERS (need whole cluster + un-converted collectors: _collect_call_targets/_hp_collect_written/_final_walk_body/_collect_noreturn_names).
- `_check_noreturn` — needs a pyval->stmt_list bridge = CERT (formal-semantics, authorization).
- `run_ir_semantic_checks` — top orchestrator; converts only once ~all callees do.

## UPDATE 2026-08-01 (72h run) — non-cert frontier EXHAUSTED at 841
72h user-authorized run: 855->841 = 14 conversions (session total 883->841 = 42), ledger 3 throughout,
all whole-file-proof + §10c all-7 + byte-diff-0 verified. THIS RUN converted (reusing/extending the
banked machinery, NO cert): the collector leaves (_collect_call_targets, _collect_noreturn_names,
_stmt_is_noreturn_call), the stateful noreturn walk (_noreturn_walk_stmts + _check_noreturn_successors),
_check_happy, _check_acts (local map-accumulator), the FINAL cluster (_final_check_stmt + _check_final +
re-based _final_walk_body int->pyval = a soundness fix), and the CONCURRENCY cluster (5 stubs: held->list
string threaded, shared->map string(option string), lock_order->option(list string), VC-free
conc__smap_set val). A driver-verifier CATCH: an agent's non-faithful _check_noreturn port (drift 3,
cert-gated) was rejected by the fidelity gate + reverted before commit.
EXHAUSTED at 841 (measured per-stub). Remaining trusted stubs by blocker class (ALL need authorization):
- core_ir_semantic (20): string-parse (_check_mutex_invariants/_check_callable_params/_check_fresh_globals);
  Wall-2 heterogeneous .items()/.values() iterator (typeddict/namedtuple/union walkers); _check_class_invariants
  (review-gated list-returning _ir_free_vars 2nd walker); _check_noreturn (CERT pyval->stmt_list);
  run_ir_semantic_checks (caller-position collection bridges + new dict-of-(int,set,set)-tuple value shape).
- other mirror files (821): ir_inline/ir_resolve (.values() heterogeneous walk + string-keyed-set κ-gap);
  pure_ast/ConcurrencyChecker/Module5/monomorphize/import_classifier (opaque CPython ast objects);
  Module6 emitters/Weaver/Module2_Parser/proof2why3 (string-construction/parse wall); exception_model
  (dict-of-tuples value shape + string-set + sorted); pycsl.py/audit_proof/sertop (legit IO/subprocess trusted).
NEXT (authorize first): Wall-2 iterator model / string-keyed-set κ-inference / a cert (SRaise / pyval->stmt_list)
/ new value-shapes / a review-gated list-returning _ir_free_vars. None autonomous-reachable under ledger-3 + no-formal-semantics.
