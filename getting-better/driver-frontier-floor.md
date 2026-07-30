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
