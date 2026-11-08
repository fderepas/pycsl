# Driver run #5 — final report (self-tcb-reduction-driver, AUTONOMOUS, 96 h)

Window: 2026-11-04T15:18Z .. 2026-11-08T15:18Z (deadline file `getting-better/.driver-deadline` = 1794151101).
Branch `ghost-assign-bc6`. Run-log entries 456-~626 (`getting-better/driver-run-log.md`); plan of record
`getting-better/driver-run5-plan.md` (392d09bc2). Commit-only until 2026-11-06 ~14:00Z; from then on push after each
commit (user policy, log 551): fast-forward only, `ghost-assign-bc6` only, never forced, no push was rejected.

## 1. Iterations and landings
- ~170 run-log entries, ~254 commits since the run's start (40cf96df0).
- **Censuses first (plan §2).**
  - cv8: the first blocker of all 387 stubs (`run5-capability-census.md`).
  - cv9: a deep multi-link census of 166 non-hot stubs, merged with the levers' chains (`run5-chain-census.md`).
  - cv10: a deep census of the 133 hot-home stubs (`run5-hot-chain-census.md`).
  - Finding: nearly every stub has a second and third wall behind the first. The value model is on 124 of 245 merged chains, and no small capability completes more than 1-3 stubs.
- **Lever / batch executors (conversions in brackets).**
  - lvA, proof2why3 `re` models [2].
  - lvB, in-place mutator havoc lowering [0]: gated but not landed, held on `run5-lvB`.
  - lvC, R325 call models [2].
  - lvD, the str seam [3].
  - lvE, #327 hygiene [0]: stopped early, every chain walls at link 2.
  - lvF, the unit-return and non-int while-Return defects [2].
  - lvG, the vm-irnode impl §1-§3 [1].
  - lvH, the mutator bundle [0]: stopped early.
  - lvI, cv10 candidates [4].
  - lvJ, empty-dict and Optional[str] typing [1].
  - lvK, partial TC-OK under the honesty rule [2].
  - Fix executors: lvD2 (writes-survival ratchet), lvD3 (#572), lvG2 (#566 / #567 exemption removal), u33 (two ledger slow planes).
- **Repair-backlog executors, one at a time (plan §4).**
  - u25: #556, #558, #560.
  - u26: #561, #562.
  - u27: #546 residual.
  - u28: #565.
  - u29: #465 early refusal, calcsize retype, and the #568 finding.
  - u30: #568.
  - u31: #569, #570, #571, #573.
  - u32: #574.
  - u34: #581 / #575 (landed).
- **Wall cycle (skill §4) for cap-vm-unerase-irnode.**
  - Report: 1da0da1d3.
  - Independent fable review: ac1d388bf. Gate R passed, with oracle artifacts; it found two live soundness defects, which became #566 and #567.
  - Implementation plan: fe51f1f4c, with a make-or-break spike and refutation exits (Gate P).
  - lvG: spike S1 passed with a REFINE note; §1 repaired #566 / #567; §2 gave 1 conversion; the §3 spike stopped.
  - Verdict: COST/SCALE wall, not a certified boundary.
- **Red team.**
  - rt54, one round after batches A + B: 27 confirmed in 5 families. The repairs became #569-#573; F4 (#572) had been introduced by this run (lvD's C2) and was repaired by lvD3.
  - rt55, report-only, in the wrap-up: 209 confirmed in 8 families, all default model, all pre-existing (the driver reproduced them on main before L1). They were opened as #575-#582.
- **Landings on main.**

  | Tree | Contents | Battery |
  |---|---|---|
  | int32 | #556 #558 #560 | v39 |
  | int33 | lvA | v40 |
  | int34 | #561 #562 | v41 |
  | int35 | #546 residual | v42 |
  | int36 | lvC | v43 |
  | **L1 = int51** (ec880a780) | lvD, lvF, lvG, lvI, lvJ, lvK, #565-#574, lvD2 / lvD3 / lvG2 / u29 / u33 fixes | v46 + v47 |

  - L2 = int52 (3861d04ca): #575 #581 (u34), v48 green (85/85).
- **Every landing** went through:
  - the driver battery: new corpus files vs their headers, route witnesses x hoare / typed / store, corpus root + pyref byte-diff vs main (only declared movers, M1 re-run), mirror sweep vs main, fidelity, and the --slow planes at 85/85;
  - a DRIVER whole-file proof of every mirror mover on a tree whose emission of that file is byte-identical to the landed tip's (the proof map, logs 597 / 600 / 608).

## 2. Stubs converted and trusted count
- **`\trusted` grep count: 415 -> 405.** That is 17 conversions minus 7 honest re-trusts (net -10). The <= 400 target was missed by 5; the 7 re-trusts are the user's decision on the #566 / #567 mirror exemption. Proof-axiom ledger: 3 throughout. No new axiom, and no new `\trusted` except the 7 re-trusts.
- **Conversions:** verbatim live body (equivalent live rewrites where noted), whole-file proof 0 non-Valid, non-vacuous mutation test, and an honesty statement. Commits in parentheses.
  - lvA: proof2why3/normalize `normalize_prover_output`, `normalize_whyml_axiom`.
  - lvC: core_ir_semantic `_typeddict_check_subscript`, `_namedtuple_check_subscript`.
  - lvD: crosscheck `CrossCheckResult.diagnostic`, pycsl `_make_temp_mlw_path`, pure_ast `_Unparser.visit_MatchStar`.
  - lvF: expr_ghost_spec_ops `_handle_mktuple_expr`, Module2_Parser `_ContractParser.parse`.
  - lvG: Module2_Parser `_ContractParser._parse_expr_list`.
  - lvI: expressions `_e`; the statements `_resolve_dotted_signature` -> `#@ declared_in` swap, which counts as a conversion per the user's 2026-11-06 decision; statements `_handle_augassign_stmt`; pure_ast `Comment.__init__`.
  - lvJ: expressions `_emit_contract_logic_symbol`.
  - lvK: Module3_Weaver `_validate_function_contracts`, pure_ast `_Tok.__repr__`.
- **Re-trusts, all logged:**
  - lvG2: stmt_control_flow `_handle_match_stmt` (#566); Module5 `_const_int_value`, `_collect_final_registry`, `_collect_typevar_registry`, `_m5_get_type_name_legacy`, `_union_arm_tag` (#567).
  - u32: Module5 `_collect_type_params` (#574).
  - None could be rewritten equivalently. Three bodies were stubbed so the trusted-termination ratchet holds.

## 3. Proof hours
- About 66.6 h of single-slot driver whole-file mirror proof time over 27 runs.
- Longest runs: expressions 11 h 18 min; statements 9 h 21 min; stmt_control_flow 5 h 33 min, 6 h 15 min, 5 h 9 min (one run rejected as OOM-suspect) and 4 h 26 min; pure_ast 3 h 34 min, 2 h 46 min and 3 h 34 min; Module5 3 h 34 min and 1 h 42 min; core_ir_semantic 1 h 44 min; functions 1 h 33 min; plus many shorter runs.
- Batching (plan §3): expressions and statements were each proved once for all of lvF, lvJ, lvI, lvD2, lvD3, u31, lvG2 and lvK.
- Executors ran their own small-home proofs in addition.

## 4. Walls
- **vm-irnode (cap-vm-unerase-irnode, 42 stubs):** full cycle; COST/SCALE. Reopening: R1 the CSLIn retype plus the non-IR narrowing view; R2 typed TypedDict views (FunctionView); R3 List[ExprIR] wiring; no new sum or cert.
- **In-place mutators (40 stubs):** the lvB lowering is sound (spike) but completes 0 stubs. Reopening: a whole-module self-field alias analysis (13 + 5 stubs), an exact pop() with an IndexError VC, the set() model.
- **#327 ident collision (13 stubs):** not the binding blocker. Every chain walls at link 2: collection aliasing / in-place mutation 6, identity tests 3, other 4.
- **The str seam:** nine distinct causes; each capability built unlocked 1 stub.
- **Honesty walls** (input-blind results): `_parse_inductive_rules` (tuple-element model), `ReverifyReport.summary`, `_coerce_dotted_args` (hval wall), `_sig_val_from_let`.
- **Refused for termination:** `_expand_anon_binders`, `normalize_surface`, `bases_closure` would convert only with `#@ \diverges` (decision 3 below).

## 5. Routes
- **Opened this run:** #565-#582 (18).
- **Repaired and landed (18 incl. the #546 residual):** #546 residual, #556, #558, #560, #561, #562, #565, #566, #567, #568, #569, #570, #571, #572, #573, #574, #575, #581. All refuse-by-default, each with witnesses in all three models, corpus FAIL + control files, census / advice / annotations §7 entries and route docs.
- **Still open for run #6:** #576 #577 #578 #579 #580 #582 (rt55, pre-existing); the documented residuals of #556-#581 (annotations §7); the #568 out-of-file-receiver residual; #497 (user decision).
- **Integration-only defects the driver caught.** Each would have landed a red plane on main:
  - writes-survival TRAP 1402 > 1399 from lvD's C2 (fixed by lvD2);
  - stale / misplaced frame-honesty ledger rows after a re-trust and a conversion (u33);
  - getattr-erasure growth from three conversions plus u30's fixtures, attributed by git blame and registered (u33);
  - the termination ratchet after the #574 re-trust (u32 stub);
  - three append-only ledger merge conflicts, unioned by hand.

## 6. Infrastructure incidents
- **heavy.sh changes:**
  - a third proof slot (plan §5);
  - a HEAVY_QUICK class for wrapper scripts;
  - NORMAL may borrow slot 2;
  - a HEAVY_PRIO class for driver gates (supervisor note).
- **OOM:** about 70 why3 runs were OOM-killed inside the pycsl-heavy slice, 2026-11-07 03:08-05:55Z, with four concurrent heavy streams. The supervisor dropped heavy.sh to 2 slots at 05:10Z (heavy.sh.v3slot kept). The driver audited every proof in the window (logs 583-599):
  - one stmt_control_flow result was rejected and re-run (4 extra 'could not be checked' vacuity probes);
  - the rest were accepted on evidence (valid == total, 0 non-Valid, 'could not be checked' sets equal to clean runs).
  No session death.
- **Hour labels:** logs ~520-586 ran ~8 h ahead of real time; corrected in log 587.
- **Plane-runner truncation:** `run-soundness-planes.sh` shows only `tail -3` of a red plane's output, which hid most of two failures (u33).

## 7. Decisions for the user
1. **#497:** `\abstract` with an executable body. Still open.
2. **`PyCSLError.__init__`:** `requires line >= 0`. Still open.
3. **`#@ \diverges` conversions:** `_expand_anon_binders`, `normalize_surface` and `bases_closure` convert only by declaring possible non-termination, which would also drop termination from verified callers.
4. **The DO-NOT-CONVERT class:** about 48 stubs whose only observable is the filesystem, subprocess, json, hashlib, argparse, stdout or eval (cv9 proposal).
5. **#429 Latin-1, #414 MemoryError, #461 top-level execution:** still open.
6. **Severities of #461 / #488:** still open.
7. **The dict-model boundary / #UND:** still open.
8. **Two weak attributions of getattr-erasure rows (u33):**
   - lvI's `_handle_augassign_stmt` guards: 4 of 6 reads are justified only as part of a verbatim port.
   - lvG's `_compute_return_type` gate: re-ported verbatim, no per-read honesty note.
9. **Settled this run:** declared_in counting (a `\trusted` -> `#@ declared_in` swap counts as a conversion) and the #566 / #567 mirror exemption (rejected; 7 honest re-trusts).

## 8. Leftover worktrees and branches
- **Worktrees:** none besides the main worktree (every executor / integration / base worktree removed after landing).
- **Branches kept, unmerged:**
  - `run5-lvB`: the gated mutator lowering, held.
  - `run5-int*`: all merged into main.
  - executor branches: all merged.
- **Main worktree:** the unrelated dirty files are untouched (prompt, scratchpad/heavy/heavy.sh as installed by the supervisor, and others).

## 9. Lessons (run #5)
- **First blockers are a poor guide.** Census whole chains before choosing a capability. Four levers in a row found a second wall one link behind the first.
- **Executors must run the ledger slow planes.** getattr-erasure, trusted-frame-honesty and assigns-writes-survival should be run individually before reporting, not only the fast planes; each one bit this run.
- **Do not trust a truncated red plane.** Read a red plane's full output, never the runner's `tail -3`.
- **Heavy streams and memory:** four concurrent heavy streams exceed the 9.66 GB slice. A proof run through an OOM window is accepted only on evidence: compare its 'could not be checked' set with a clean run.
- **Re-trusts and conversions both touch ledgers.** Each moves frame-honesty, termination and getattr ledgers (lesson d5 again).
- **Hour bookkeeping:** derive run hours from `.driver-started`, never from memory.

## 10. Final-main convergence (log 624)
On main 8eb4669d6 (default model), each run #5 route's exemplar: repaired routes #565-#575 and #581 all refused by
their named codes or NOT PROVED; the six open rt55 routes (#576-#580, #582) still prove, as recorded.
