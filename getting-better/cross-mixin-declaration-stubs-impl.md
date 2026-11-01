# cross-mixin-declaration-stubs-impl.md — implementation plan (driver run #3, 2026-10-30)

Inputs: `cross-mixin-declaration-stubs.md` (dc1, report) and `cross-mixin-declaration-stubs-response.md` (independent fable
review, Gate R satisfied: oracle runs O1-O9 cited, incl. Why3 clone-refinement spikes O6/O7 and the import refutation O4).
Both agree: modelling choice, not a fundamental wall; order R0 -> R1 -> R2a -> R3 -> (R2b) -> R4; R7 (relabel as
`\abstract` / bare `requires_method`) is trust laundering and is FORBIDDEN; no marker drops before a checking plane exists.

## 1. FIRST ACTION — Gate S (make-or-break spike, refutation exit)

Widen the 12 + 1 under-stated declaration frames (and the `_seq_operand` window's `raises`) to the definition's text
(R1) in the executor's tree and run, through heavy.sh, the WHOLE-FILE proofs of the affected mirror files
(`stmt_control_flow.py`, `statements.py`, `expr_ghost_spec_ops.py`, `expr_ghost_collections.py`, `expressions.py` --
HEAVY_LOW=1; emit-diff first per lesson (r): only files whose emission changes need the proof).
- PASS: every changed file proves 0 non-Valid (the four verified control-flow callers' VCs cannot change truth value, O9).
- REFUTE: a changed file no longer proves -> STOP, record which VC depended on the narrow frame (that would be a REAL
  false proof today: escalate it as an open route), no build.
- A solver-budget artefact (Timeout / OOM) is re-run, never a verdict.

## 2. Build (only after Gate S PASS), one commit per increment, brief rule-5 battery on the final HEAD

B0 (R0): `bin/check-trusted-frame-honesty.py` resolves a declaration to its definition through the live MRO (the
   resolution `_self_write_fixpoint` already uses for call edges) and includes the `requires_method` windows; it must
   report the 12 + 1 deltas RED on the base tree (show it) and green after B1. Ratchet, never a loosened gate.
B1 (R1): the frame / raises widening of Gate S, committed.
B2 (R2a): a pure-AST plane `bin/check-declaration-conformance.py` (wired into `bin/run-soundness-planes.sh`, ratchet
   style): for EVERY declaration (`\trusted` stub with no live def in its class, or `requires_method` window) resolve the
   definition and check (a) projected frame inclusion decl ⊇ def (projection onto the declaring file's record fields),
   (b) raises ⊇, (c) requires / ensures TEXT-equal (a non-trivial pre/post is reported as needing R2b and fails the
   plane), (d) signature refinement (report the `ExprIR` vs `Dict` type-layer mapping explicitly). Row 16
   (`_handle_return_stmt`, a base/override pair) goes through the existing #277/#278 override path, not this plane.
   Negative-test the plane: a scratch copy with one frame narrowed back must turn it RED.
B3 (R3): delete the 6 unapplied declarations in `statements.py` ONLY if the plane and the sync / mirror checks accept it;
   report them as "removed by absence", not as capability.
B4 (R4, conditional on B2 green + ratcheted): introduce `#@ declared_in <file>::<Class.m>` in place of `#@ \trusted` for
   declarations the B2 plane checks; `bin/count-trusted-directives.py` reports it as a DISTINCT class next to the
   `\trusted` count; `check-trusted-reasons.tsv` rows move accordingly; the 14 trusted definitions stay counted. Announce
   as "-N markers, -3 TCB" (net). Every doc surface the new directive touches (doc-coherency: annotations.md,
   README, the three reference docs, a skill) is updated. If the directive cannot be made to emit EXACTLY the same
   WhyML as the trusted declaration (emit-diff 0 on the mirror), stop B4 and report.

R2b (generated Why3 clone-refinement conformance units) is OUT of scope for this run (about a week); record it as the
next step. R6 (one composite record) stays research.

## 3. Gate battery (brief rule 5, every rc teed in full)

fidelity; root + pyref byte-diff vs a base worktree at the starting commit (the emitter is not touched, so expect 0/0/0);
mirror emit sweep (MOVED = exactly the files B1 / B3 / B4 change; each OWED whole-file proof is run); planes 61 (+ the
new plane); all ledgers; `\trusted` and `count-trusted-directives` before / after.

## 4. Costed scope (honest)

Gate S + B0 + B1: ~half a day of wall time dominated by the `statements.py` whole-file proof (~2 h 20 m at low priority).
B2: one to two days of careful work in the reviewer's estimate -- this run attempts it inside the executor's box; if the
box ends first, B0 + B1 land alone (soundness hygiene, \trusted unchanged) and B2-B4 are the recorded next step.
Expected verdict: BROKEN (narrow): -24 (or -18 after B3) markers gross, -3 TCB net, ONLY with B2 green; otherwise
CERTIFIED-BOUNDARY for B4 with B0 + B1 landed.

## 5. Gate S result (executor dx1, 2026-10-30) — REFUTED for the opaque-`self` rows; NO BUILD

Tree `a9e1f2e13`. R1 applied in the executor tree with dc1's `sync_decl_frames.py` (each declaration's `#@ assigns`
replaced by / given its definition's line verbatim) for the 12 STRONGER rows 1, 2, 3, 7, 9, 10, 11, 12, 13, 20, 23, 24.
Emit (`--no-proof --keep-mlw`, through heavy.sh) base vs candidate of the five files:

| file | candidate | `.mlw` diff vs base | verdict |
|---|---|---|---|
| `expr_ghost_collections.py` (row 1) | **L3-tc ✗** | — | **REFUTED**: `let ghostcollectionopsmixin___handle_append_expr ... writes { }` applies `self__e_2`, which now `writes { _pyobj_state }` -> Why3 "this expression depends on variable _pyobj_state, which is left out in the specification" |
| `expr_ghost_spec_ops.py` (rows 2, 3) | **PIPELINE ERROR [ir-semantic]** | — | **REFUTED**: `'ghostspecopsmixin___handle_mktuple_expr' calls 'self._e', which WRITES ..., inside a comprehension ... PyCSL lowers OPAQUELY` |
| `stmt_control_flow.py` (rows 20, 23, 24) | L3-tc ✓ | 10 lines (`self__match_pattern_cond_3` gains a receiver + 12-field `writes`; `self__expr_to_whyml_2` +3 fields; 2 dependent `writes`; 1 call site) | whole-file proof (HEAVY_LOW, candidate): rc=0, **14817 Valid / 0 non-Valid**, `Verification SUCCESS` (13546 s incl. the non-vacuity gate; 2 vacuity call-site probes `could not be checked` for `_handle_if_stmt` / `_handle_return_stmt`, a warning, not compared to a base run) -> **PASS** |
| `statements.py` (rows 7, 9-13) | L3-tc ✓ | 3 lines, all a `writes` added to an UNAPPLIED bodyless `val` (`statementemissionmixin___e`, `___expr_to_whyml_string_ctx`, `___track_collection_metadata`; each symbol occurs once in the `.mlw`) | whole-file proof NOT run: the ~2 h 20 m+ LOW-slot proof could not finish inside the box after the 3 h 46 m `stmt_control_flow` run. The emission change touches no applied symbol, so no VC is expected to change — an expectation, NOT a proof |
| `expressions.py` | L3-tc ✓ | 0 lines | unchanged |

**What depended on the narrow frame (rows 1-3).** Not a VC: the *frame* of 30 VERIFIED handlers. In both ghost files
`self` is opaque (`type ghost*mixin = int`); every `_handle_*` handler that calls `self._e` / `self._expr_to_whyml_string_ctx`
is verified with `#@ assigns \nothing` (21 in `expr_ghost_collections.py`, 9 in `expr_ghost_spec_ops.py`). Their emitted
`writes { }` type-checks ONLY because the declaration `assigns \nothing` makes the avatar frameless. With the definition's
frame the avatar writes the coarse `_pyobj_state` and Why3 rejects the callers' empty `writes`. So today the mirror
certifies 30 `assigns \nothing` frames that rest on an understated `\trusted` declaration.

**Runtime witness (live code, not the over-approximated definition frame).** `/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/dx1/witness/frame_witness.py` (programs `w1`-`w8`, `x1`-`x6` beside it)
wraps every live `GhostCollectionOpsMixin` / `GhostSpecOpsMixin` `_handle_*` method, fingerprints `vars(self)` before and
after each call, and runs the live pipeline (`--no-proof`) on a small program. With
`#@ ensures \has_key(\result, abs(a[0])) ==> \has_key(\result, abs(a[0]))` (also `max(a)`, `sum(a)`), the live
`_handle_has_key_expr` WRITES `self._abstract_ops`; with `int(s)` it writes `self._uses_const_reflect_cache`. The mirror's
verified `_handle_has_key_expr` claims `assigns \nothing`. (The witness programs themselves fail L3-tc —
`unbound ... 'abs_conv'` — which is a separate, uninvestigated observation: an abstract op registered while a ghost
handler emits a spec operand does not reach the module. The write itself is what the witness shows.)
Controls: on corpus 0295 / 0312 / 0785 / 0786 the wrapped handlers run and write nothing (hits=0).

**Model-visibility.** The handlers are dispatched by name (`Module6_WhyMLTranspiler.py` dispatch table), not through an
avatar, so no other mirror proof is known to consume these 30 frames: a FALSE PROVED CONTRACT CLAUSE, not (yet) a false
proof of a consumed fact. Escalated as an open route (below).

**Repair cost, spiked (scratch copies, `--no-proof`).** (i) `expr_ghost_collections.py`: also widening the 21 callers'
`assigns \nothing` to the definition's frame -> L3-tc ✓ (23 `writes { _pyobj_state }`) and the scratch copy's whole-file proof is rc=0, **166 Valid / 0 non-Valid**,
`Verification SUCCESS` (199 s, non-vacuity gate included); honest, but it WEAKENS 21
verified contracts to their true frame and owes a whole-file proof. (ii) `expr_ghost_spec_ops.py`: widening the callers
does not help — `_handle_mktuple_expr` (`", ".join([self._e(e, lr) for e in node.elts])`, verbatim live) is refused
by the opaque-comprehension write rule; it needs either a re-trust (+1 marker) or a comprehension lowering that applies
the call per element.

**Correction to the report (§5.1) / review (§5.3).** On this tree the `requires_method _seq_operand` window is NOT
understated: the mirror definition `statements.py:_seq_operand` is VERIFIED (not `\trusted`), declares 21 fields, all
inside the window's 22, and has NO `raises` clause. There is nothing to widen. (Also: the Weaver's window accepts only
`requires` / `ensures` / `assigns`; a `raises` line closes the window and becomes the enclosing method's own clause.)

**Open route (escalated), replaces B1 for rows 1-3:** "ghost-handler false frames": 30 verified `_handle_*` methods in
the two opaque-`self` ghost files prove `assigns \nothing` only via the understated `_e` / `_expr_to_whyml_string_ctx`
declarations; the live `_handle_has_key_expr` writes `self._abstract_ops` (witness). Fix = R1 for rows 1-3 TOGETHER with
honest caller frames (collections: spiked L3-tc ✓) and a decision for `_handle_mktuple_expr` (re-trust, or a modelled
comprehension). Then B0-B4 as planned.

**Gate S verdict: REFUTED** (refutation exit taken; B0-B4 NOT built, no mirror file changed, `\trusted` 436 lines /
408 markers unchanged). Of the four files whose emission R1 changes: `expr_ghost_collections.py` and
`expr_ghost_spec_ops.py` no longer type-check / pass semantics (the narrow `_e` / `_expr_to_whyml_string_ctx` frames are
load-bearing for 30 verified frames, runtime-witnessed false for `_handle_has_key_expr`); `stmt_control_flow.py` PASSES
(rows 20, 23, 24: the four verified control-flow callers are unaffected, as O9 predicted); `statements.py` not proved.
Candidate patches: `/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/dx1/gateS_full_R1.patch`
(all 12 rows) and `.../dx1/gateS_R1_nonghost.patch` (rows 7, 9-13, 20, 23, 24 only). A coordinator MAY re-scope B1 to the
non-ghost rows (Gate-S-green for `stmt_control_flow.py`; `statements.py` proof owed); that is a plan change, not taken here.
Next step after the ghost route: R0/B0 as planned, then R2a, with R2b (generated Why3 clone-refinement units) recorded as
the step after.

## 6. Execution record (executor dc2, driver run #3, 2026-10-30/31) — B1 + B0 + B2 landed, proofs OWED; B4 NOT built

Base `8fdfce794` (z1 had already repaired the 3 ghost rows, route #488). Order run: B1, B0, B2, gate battery.

**B1 (R1) — and why it is NOT the verbatim sync of §5.** The verbatim definition frames (dx1's
`gateS_R1_nonghost.patch`, re-derived on this tree: identical) raise `check-assigns-writes-survival` TRAP
1399 -> 1484 (+85): a declaration's `writes` is its frame INTERSECTED WITH THE DECLARING CLASS'S RECORD,
so the definition's fields that record does not carry emit nothing and read as a guarantee (the TRAP).
Paying that the z1 way (declare the fields) was tried for the one field that matters across units
(`_rebound_collections`, see below) and REFUTED by `check-assigns-underdeclaration` (RED: the newly
mentionable field is written by the live closures of `_handle_seq_assign` (verified),
`_handle_tuple_unpack_stmt`, `_stmts_to_whyml`, whose frames omit it — declaring it turns three
fail-closed omissions into model-visible holes); reverted. Landed instead: each of the 9 understated
declarations widened MONOTONICALLY (nothing removed from any clause) by every definition field the
declaring class's record carries, the whole definition frame where the record carries none. EMISSION:
`statements.mlw` and `stmt_control_flow.mlw` are byte-identical to the verbatim-sync candidate (dx1's);
`Module6_WhyMLTranspiler.mlw` differs from it in one unapplied composite val. TRAP 1399, HOLE 0.
RESIDUAL (named in B2's ledger): `_track_collection_metadata` is MRO-selected in the mirror composite
(`Module6_WhyMLTranspiler` lists StatementEmissionMixin before TypeInferenceMixin, so its composite val is
minted from this declaration onto the union record, which carries `_rebound_collections`); the declaration
omits that one field there (the val is unapplied; base was frameless). Repair = the 3 frames above + the
field, or a TRAP-ratchet decision by the driver.

| MOVED mirror (sweep vs base) | emission vs base | proof |
|---|---|---|
| `module6_whyml/stmt_control_flow.py` | 10 lines (`_match_pattern_cond` avatar gains receiver + 12-field `writes`, `_expr_to_whyml` +3) | `.mlw` BYTE-IDENTICAL to dx1's candidate (`scratchpad/dx1/cand_mlw/stmt_control_flow.mlw`), whose whole-file proof is rc=0, 14817 Valid / 0 non-Valid, `Verification SUCCESS` (13546 s, `scratchpad/dx1/proof_cand_stmt_control_flow.log`) — transferred, not re-run |
| `module6_whyml/statements.py` | 3 lines: a `writes` on the UNAPPLIED vals `_e` / `_expr_to_whyml_string_ctx` / `_track_collection_metadata` (each symbol occurs once) | L3-tc ✓; whole-file proof **OWED**. (A whole-file run of the withdrawn field variant reached 25211 Valid / 0 non-Valid in the VC stage and was killed in the non-vacuity stage at 5 h 38 m; it is NOT evidence for this emission.) |
| `Module6_WhyMLTranspiler.py` | `writes` on 4 unapplied vals (3 imported, 1 composite) | L3-tc ✓; whole-file proof at HEAD `d2675cb4a` (HEAVY_LOW): rc=0, **1764 Valid / 0 non-Valid**, `Verification SUCCESS` (1688 s, non-vacuity included; `scratchpad/dc2/proof_final_transpiler.log`) |

**B0 (R0)** `bin/check-trusted-frame-honesty.py`: a DECLARATION arm (population and live-MRO resolution in the
new shared `bin/lib_declarations.py`: 24 `\trusted` stubs + 2 `requires_method` windows, every one resolving
to exactly one definition), and the `\nothing` arms resolve a declaration through the MRO too. Negative test
= the base tree: OWN 9 (5 MODEL-VISIBLE) RED, trusted `\nothing` total 3 > 1 and model-visible 2 > 0 RED.
HEAD: OWN model-visible 0 (hard), OWN 7 (all unmodelled in the declaring file; ratchet 7), INHERITED 13
(ratchet 13: the DEFINITIONS' own frames omit live writes `_r188_stub_names` / `_r55_subsumed_name` /
`r417_obls` / `r434_ok` / `ir` — a residual of the trusted definitions), GREEN.

**B2 (R2a)** `bin/check-declaration-conformance.py`, pure AST, fast plane #57 (MIN_PLANES 56 -> 57): frame ⊇
definition projected onto every record the declaration reaches (declaring class + mirror composites whose
unit MRO-selects it; import visibility resolved as pycsl does, relative to the importing file), no frameless
declaration of a writing definition, raises ⊇, pre/post trivial (else R2b, RED), signature refinement with
every accepted type-layer mapping printed (`ExprIR ~ Dict`, `set ~ Set[str]`, ERASED `int` parameters of the
definition). Base tree: 11 FAIL (7 unnamed) RED. HEAD: 21/26 conform; 5 NAMED residuals with their EXACT
recorded violation (`KNOWN_NONCONFORMING` / `KNOWN_FAILURES`, FAIL_RATCHET 5; a ledgered declaration that
fails differently, or conforms again, is RED): window `_field_type_of` (`-> str` over `Optional[str]`),
`_resolve_dotted_signature` (tuple result over an unannotated definition), statements `_expr_to_whyml`
(`subst: int` over `Optional[Dict[str, str]]`), `_track_collection_metadata` (the composite residual above),
row 16 `_handle_return_stmt` (`ExprIR` over `ReturnStmt`; base/override — routes #277/#278 do NOT reach it: no
`refines` goal is emitted, the base is imported from the un-annotated live tree). Negative tests on scratch
copies (`scratchpad/dc2/neg/b2_neg.sh`): control GREEN; frame narrowed to `\nothing`; one in-record field
dropped; a second field dropped from the ledgered MRO-selected declaration; a `raises` the definition gains;
a non-trivial `ensures` (R2b); a result type changed; a ledgered residual repaired without un-ledgering it
— all 7 RED.

**B4 (R4) NOT BUILT.** B2 certifies 20 `\trusted` declaration stubs (conforming, other-mixin), so
`#@ declared_in` could carry at most 20 markers (gross -20; net TCB -2: only the two `_coerce_to_int`
declarations have a VERIFIED definition; row 16 is excluded). Not started because (i) B1's statements.py proof is OWED;
(ii) it is a language change the pycsl-audit-pycsl-language discipline wires through parser, five doc
surfaces and the reference corpus, and this executor had no corpus ID block (brief rule 4); (iii) every plane
keyed on the `\trusted` marker must learn the new class or silently lose population:
`count-trusted-directives` / `trusted_markers`, `check-trusted-reasons` (20 rows), `check-untrusted-emitted`
(a `declared_in` stub is emitted as a `val`), `check-self-annotate-mirror-sync`, `check-trusted-frame-honesty`'s
trusted `\nothing` arm, `check-directive-enforcement` (a user-facing `declared_in` is enforced only by this
repo plane, not by pycsl — it must be refused outside the mirror or counted as trusted by pycsl's own TCB
report, else it is `\trusted` under another name). Design for the next executor: parse
`declared_in <file>::<Class.m>` in `Module2_Parser._parse_contract` (not mirrored) to the SAME `Trusted` node
(emission identical by construction; verify mirror emit-diff 0), teach the walks above, and make B2 require
the named target to equal the live-MRO resolution.

**Next steps:** the OWED whole-file proof of statements.py (~5 h+ at LOW incl. non-vacuity); the
`_rebound_collections` repair (3 frames + field); R2b (generated Why3 clone-refinement units — no declaration
has a non-trivial pre/post today); then B4.

**Gate battery (HEAD `d2675cb4a`, every rc 0):** fidelity sync (938 functions) / mirror-check (53) / doc-coherency;
corpus byte-diff root 2696/2696 0 MOVED / 0 GONE / 0 APPEARED and pyref 2186/2186 0/0/0 (candidate swept at
`12ca6cf63`, src/pycsl identical; baseline = `scratchpad/v18/ca`, the emission of `909ecae97`, whose src/pycsl and
corpus are identical to `8fdfce794`); mirror sweep 53/53, MOVED exactly statements / stmt_control_flow /
Module6_WhyMLTranspiler (the base mirror emission equals v18's proved one byte for byte); soundness planes 62/62
(fast incl. the new plane + the conversion tier); slow planes check-assigns-writes-survival (TRAP 1399, HOLE 0)
and check-emitted-function-coverage OK; check-trusted-frame-honesty --emit-dir OK; check-assigns-underdeclaration
--transitive OK (TRAP 3, HOLE 0); check-trusted-reasons 409 <-> 409; count-trusted-directives markers 409 / grep 437;
check-assumed-facts OK. `\trusted` 437 lines / 409 markers before and after (gross 0, net 0).

## 7. Execution record (executor dl4, driver run #4, 2026-10-31/11-01) — B4 BUILT

Base `4b626bc4b` (int13 = main `e7d7cdd47` + dc2's B0/B1/B2). Commits: `edaf10b77` (directive, refusal,
corpus, docs), `92fadf94b` (20 conversions + planes taught + ledgers).

**Directive.** `#@ declared_in <relpath>.py::<Class>.<method>` parses in `Module2_Parser._parse_contract`
(inline: its mirror twin is `\trusted`, lesson a4) to the SAME `Trusted` node as `\trusted`, with
`reviewer = "declared_in:<target>"` (no reviewer reaches the WhyML), so emission is identical by
construction AND pycsl's own TCB accounting still counts it as trusted. `_run_pipeline` REFUSES it in any
file outside `src/self-annotate/src/` (choke-point rule). Malformed target = parse refusal; `# @declared_in`
= ingestor near-miss refusal. pycsl.py's text-level `\trusted` block scans (#444 / #449 / #226 / #468 /
#489) read `declared_in` as `\trusted`. Corpus: 7827 FAIL (refused; without the refusal `f` would prove a
false `\result == 1`), 7828 PASS (control, `\trusted reviewer:`), 7829 FAIL (malformed), 7830 FAIL
(near-miss, all contracts true), 7831 PASS (control) — each matches its expectation. Refusal-witness census
gained rows for 7827/7829/7830. Five doc surfaces + pycsl-annotate / self-tcb-reduction skills.

**Conversion.** Exactly B2's 20 conforming other-mixin `\trusted` declaration stubs (row 16 and the 5
ledgered residuals untouched). Mirror emit sweep vs int13: 53/53, **0 MOVED / 0 GONE / 0 APPEARED** — no
proof owed. `\trusted`: 409 -> **389** markers, grep 437 -> **417**; `declared_in` **20** (own column).
**GROSS -20 markers; NET TCB -2** (only the two `_coerce_to_int` declarations name a VERIFIED definition;
the other 18 move the trust onto 13 trusted definitions that stay counted). Whether `declared_in` is a
headline class is a USER decision: the `\trusted` grep keeps its meaning, both numbers are printed.

**B2 (g).** The named target must EQUAL the live-MRO resolution; exactly one line; no `\trusted` beside it;
not on a ledgered or base-override declaration; every `declared_in` in the mirror must govern a census
declaration. Negative tests (`dl4/neg/b2_neg.sh`, scratch copies) 10/10: control GREEN; wrong class; wrong
file; on a twinned (non-declaration) method; in-record frame field dropped; frame `\nothing`; with
`\trusted`; on ledgered row 16; annotating nothing; definition gains a `raises` — all RED.

**Planes taught, with (u6) perturbation** (B = base plane on base tree, T = taught on HEAD, U = BASE plane
on HEAD): count-trusted (U silently drops the 20; T adds the column), trusted-reasons (20 unclassified rows
moved OUT, MAX_UNCLASSIFIED 257 -> 237; U keeps 257 and never mentions them), untrusted-emitted (U: 20
SILENTLY RE-ABSTRACTED, rc=1; T = B), mirror-sync `methods` (U: sibling-concrete-fidelity 20 NEW
DIVERGENCES rc=1; T = B), frame-honesty (U moves 20 from the trusted param population 402 -> 382 into the
converted one; T = B), raises-honesty (U 67 -> 64), claim-strength (U trusted 391 -> 371), blast-radius
(U 388 -> 368), directive-enforcement (new pair, MIN_COVERED 52 -> 53). Taught for consistency, no
measured sensitivity (U = T = B): termination, underdeclaration, bespoke-discard, yield-erasure,
computed-rhs (perturbation timed out; base only). Inspected and deliberately NOT taught (same-qualname
pairing never sees a declaration; untaught is stricter on a misplaced marker): self-annotate-mirror-check.sh,
check-mirror-signature-drift. Others in bin/ read IR / emission (identical by construction) or are tools.

**Battery (HEAD `92fadf94b`).** fidelity sync / mirror-check / doc-coherency rc 0; corpus byte-diff root
0 MOVED / 0 GONE / 1 APPEARED (`1723_route212_verify_imports_control`: environmental — the int13 baseline
was swept without why3 on PATH; the base tree with why3 emits it byte-identically) and pyref 2186/2186
0/0/0; mirror 53/53 0/0/0; fast planes 62/62; slow 22/23 (check-swallowed-exceptions RED, identical on the
base tree: 4 `_run_pipeline` firings, pre-existing per log 339); count-trusted / trusted-reasons (+self-test)
/ assumed-facts OK; proof_axiom_allowlist unchanged.
