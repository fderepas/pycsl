# Driver frontier floor — count 875 (2026-07-27, 96h autonomous run)

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
| string-keyed set-membership (`handler_catches`, `subclasses_of`, `all_phase1_exceptions`, `classify`) | **multi-piece capability wall** | Nearest (`handler_catches`) needs a build crossing the **Module5 front-end** (frozenset-element-type κ inference — no signal today) **+ emitter** (frozenset-return retype `map int`→`map string`; new module-function-call `x in f(...)` membership case). NOT corpus-perturbing (0 corpus files — byte-inert), NOT needs-cert (set.Fset trusted, ledger 3), NOT saturation (dies at L3-tc). Authorizable multi-piece cross-boundary build. |
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
