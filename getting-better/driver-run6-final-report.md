# Driver run #6 — final report (self-tcb-reduction-driver, AUTONOMOUS, 96 h)

Window: 2026-11-08T17:56Z .. 2026-11-12T17:56Z (`getting-better/.driver-deadline` = 1794506189). Branch
`ghost-assign-bc6`. Run-log entries 644-~800 (`getting-better/driver-run-log.md`). Plan of record:
`getting-better/driver-run5-plan.md` (capability batches, cheap gates per conversion, batched whole-file mirror
proofs, integration tree + battery before landing, reduced red-team cadence, one repair executor at a time); its §5
slot layout superseded by the 2-slot heavy queue. COMMIT-ONLY: nothing was pushed.

## 1. Iterations and landings
- **Census first.** cv11 (`getting-better/run6-capability-census.md`, b0d6ec044): 377 governing markers (405 grep
  lines, 28 prose); 192 prior chains replayed (184 same terminal); no rewrite/retype-only near miss; ranking over
  COMPLETE chains: R1 per-receiver narrowing (6), exception-payload model (4), `\diverges` (user decision, 1), frame
  widening (1), none-default map param (1). Lever (i): `src/pycsl_lib` stdlib models are NOT usable for the
  external-world stubs (route #326 refuses them under `--import-path`; aliased in they are closed-world toys).
  lvP Part 1 (`getting-better/run6-lvP-recensus.md`) re-walked the 54 chains naming the run #6 capabilities.
- **Capability / batch executors (conversions in brackets).**
  - lvL — R1: route #567's ast narrowing decided PER RECEIVER (resolution via #579's table) [4; 2 more re-trusted
    under the model-dead-branch rule, then converted by u37].
  - lvM — exception-payload model (user exceptions carry their first constructor argument) [3; `PyCSLError.__init__`
    stays `\trusted` because of the open `requires line >= 0` decision].
  - lvN — cap-none-default-map-param (`pycsl_none_map`) + `_rebound_collections` declared and 15 frames widened
    truthfully [2 `\trusted -> declared_in` swaps].
  - lvO — law-free re.Match model + constant-pair loop unroll [1].
  - lvP — List[Tuple]/Tuple returns as pure seqs of native tuples + typed pass-body trusted tuple stubs [4].
- **Repair executors (one at a time on the backlog, plus mandatory ones).** u36 (#579 #580 #582), u37 (#583 + the 2
  re-conversions), u38 (#584 #585), u39 (#589 #590 #591), u40 (#592, introduced by run #6 — mandatory).
- **Red team.**
  - rt56 (scope = run #6's capabilities and routes): 1068 probes, 966 CPython-breaching; its proofs were starved by
    the batch proofs and completed by the driver. 15 confirmed false proofs in 6 families: 14 PRE-EXISTING (#589-#591,
    #593-#595, proved on the pre-run-#6 base 822621340) and 1 INTRODUCED by run #6 (#592, lvN's none_map; L3 type
    error on the base) — repaired by u40 (mandatory) and landed in L6.
  - rt57 (wrap-up, report-only; scope = the last batch's changes): 636 probes, 626 CPython-breaching, 82 confirmed
    (default model only) in 3 families, all PRE-EXISTING: #596 (44, unarmed child reads after an IR class test),
    #597 (30, R590 misses function-local rebinding), #598 (8, exception-constructor keyword args).
- **Landings on `ghost-assign-bc6`.**

  | Landing | Tree | Contents | Battery |
  |---|---|---|---|
  | L4 dc3a7763f | int54 | u36 (#579 #580 #582), cv11 census | v51 85/85 |
  | L5 57ca7b58c | int55 | lvM + lvN + lvL + u37 (#583) + lvO | v52 85/85 + 22 mirror movers proved (proof map) |
  | L6 f02f79c32 | int57 (int56 + u39 + u40) | u38 (#584 #585) + lvP + u39 (#589-#591) + u40 (#592) + 2 driver fixes | v53 + v54 (F 84/85 -> fixed, fast 62/62) + 9 mirror movers proved |
  | L7 ca5516027 | int58 | u41 (#593 #595, mirror-inert refusals) | v55 85/85 |

## 2. Stubs converted and trusted count
- **`\trusted` grep count: 405 -> 393 (L5) -> 389 (L6, final).** 16 conversions, 0 net re-trusts (2 temporary
  re-trusts by lvL were converted back by u37). Proof-axiom ledger 3 throughout; no new axiom, no new `\trusted`.
- **Conversions** (verbatim live body or a behaviour-identical live respelling of the trusted twin; whole-file proof
  0 non-Valid on an emission-identical tree; mutation test; NEW this run: leaf-reachability check):
  - Module5_IREmitter: `_const_int_value`, `_collect_type_params`, `_collect_typevar_registry`,
    `_m5_get_type_name_legacy` (lvL); `_collect_final_registry`, `_union_arm_tag` (u37, after #583).
  - Module2_Parser: `_ContractParser._err` (lvM); `_grab_reviewer_id`, `_parse_inductive_rules`, `_parse_inductive`,
    `_parse_variant_def` (lvP).
  - pure_ast: `_Parser.error`, `_Parser.unsupported` (lvM).
  - statements: `_expr_to_whyml`, `_track_collection_metadata` declared_in swaps (lvN).
  - Module1_Ingestor: `_match_block_hdr` (lvO).
- Goal "< 405" met; stretch "<= 390" met at 389.

## 3. Proof hours
- Driver whole-file mirror proofs: 35 proof runs, ~76.8 h of proveq wall time (including queue waits), plus the
  driver's battery planes (v51-v55, ~3 h of --slow planes each) and executors' own small-home proofs.
- Longest: statements 12.5 h (int55s2, 2 vacuity workers) and 9.9 h (int56, 3 workers); expressions 12.2 h (int55x)
  and 10.6 h (int56); stmt_control_flow 10.3 h (incl. queue); pure_ast 3.1-3.5 h; Module5 2.7-3.3 h.
- Batching (plan §3): expressions / statements / pure_ast / Module5 were each proved once per landing (L5: 22 mirror
  movers; L6: 9 movers), with the proof map deciding which earlier proofs carried over.
- Voided / superseded: one statements run (OOM), one stmt_control_flow start (OOM window), one expressions run
  (superseded by u37 + lvO merged mid-proof).

## 4. Walls / near misses still open
- cv11: no rewrite-only near misses remain; the residual chains are dominated by the value-model seam
  (vm-unerase-irnode / list / dict on 56 / 26 / 25 chains), external-world models (fs 30, subprocess 20),
  method-recursion termination (28), context managers (19), self-field alias analysis (18).
- lvP re-census: `_parse_contract` (py_label record vs emit_ir), `_index_proofs_dir` / `parse_type_expr`
  (cap-exception-object-read), re.Match beyond lvO's gate (`_re` alias, `m.start()`, `lastgroup`, Any subject).
- lvO: `_rewrite_annotation_str` (Any subject, tuple-key dict), `parse_format` (route #369 kwarg, .extend, ...).
- `PyCSLError.__init__` (route #226 invariant goal needs the open `requires line >= 0` decision).
- `_expand_anon_binders` (needs the open `#@ \diverges` decision).

## 5. Routes
- **Opened this run:** #583-#598 (16).
- **Repaired and landed (12):** #579 #580 #582 (L4), #583 (L5), #584 #585 #589 #590 #591 #592 (L6), #593 #595 (L7).
  All refuse-by-default or faithful lowerings, witnesses in default / typed / store, corpus FAIL + control files,
  census / advice / annotations §7 entries, route docs.
- **Open for run #7:** #586 #587 #588 (u38 findings: shared node / string projectors, `_to_bool` truthiness), #594
  (AnnAssign `.value is None` decided), #596 (unarmed child reads -> placeholder; 44 probes), #597 (R590 local
  rebinding; 30), #598 (exception-ctor kwargs; 8), route #583's F3; the documented residuals of #579-#595
  (annotations §7). All pre-existing. No route introduced by run #6 is left open.

## 6. Infrastructure incidents
- **OOM:** 5 memcg kills (oom_kill 70 -> 75) in one statements whole-file proof's vacuity phase (pycsl ran
  cpu_count//2 = 6 why3 probes, ~1 GB each, at the 6 GiB per-job cap). Result voided and re-run alone; fix =
  `PYTHON_CPU_COUNT=4` (2 workers) and later `=6` (3 workers) — no code / heavy.sh / cap change. No kill after.
- **LOW starvation:** a LOW statements proof never got slot 2 in 70 min; long driver proofs moved to PRIO.
- **Watcher bug:** waitev.sh globbed its watch list once, so the int55 expressions result sat unseen ~6 h; fixed
  (log 745).
- **Executor oracle edit:** lvM changed the `--fun` tooling; verified non-weakening against a known-bad control and
  landed conversions (log 659).

## 7. Decisions for the user
1. #497 (`\abstract` with an executable body) — still open.
2. `PyCSLError.__init__` `requires line >= 0` — still open (blocks that conversion).
3. `#@ \diverges` conversions (`_expand_anon_binders`, `normalize_surface`, `bases_closure`) — still open.
4. #429 Latin-1, #414 MemoryError, #461 top-level execution, severities of #461 / #488 — still open.
5. The dict-model boundary / #UND — still open (new evidence: `Optional[Dict]` parameters are modelled as maps, so a
   callee's `isinstance(d, dict)` is decided true; #592 refuses the only route by which `None` reached such a body).
6. Driver-approved this run (not user decisions, recorded for review): truthful widening of 15 frames (lvN); a
   verified contract strengthened from its body (`expect_name`, lvP); two NEVER_RETURNS registrations in
   check-corpus-contract-truth for lvP's deliberately pass-body trusted witnesses (9517 / 9519).

## 8. Leftover worktrees and branches
- **Worktrees:** none besides the main worktree (every executor / integration / red-team / base worktree removed
  after its outcome was logged).
- **Branches kept, unmerged:** `run5-lvB` (held mutator lowering, from run #5) and `run6-cv11` (census branch; its doc
  was cherry-picked as e8f7d025f). All other run6-* branches are merged into `ghost-assign-bc6`.
- **Main worktree:** the unrelated dirty / untracked files present at run start were left untouched.
- **Nothing pushed** (commit-only, as instructed).

## 9. Lessons (run #6; carve-outs in the driver skill)
- A conversion must pass a LEAF-REACHABILITY check (model-dead, CPython-live blocks found a real false proof, #583).
- Vacuity-phase workers are the memory peak: cap them with PYTHON_CPU_COUNT.
- LOW is starved when NORMAL/PRIO borrow slot 2; long driver proofs run PRIO.
- A proof counts for the tip only if its file's emission is byte-identical at its start tree and the tip (proof map).
- A capability that turns an ill-typed (fail-closed) lowering into a well-typed one can EXPOSE a latent model gap
  (#592): red-team the boundary the old type error was guarding.
- Red-team proofs starve behind batch proofs: the driver must reserve proof time for them.

## 10. End state
- `ghost-assign-bc6` at the L7 landing + log / report commits; `\trusted` 389 (from 405), proof-axiom ledger 3.
- Last full battery on the landed tree: v55 85/85 (--slow), corpus root 3109 / pyref 2185 byte-inert vs L6, mirror
  53/53 byte-identical to the L6 tip whose 9 movers were proved whole-file.
- Slice oom_kill 75 since 2026-11-09T16:53Z (5 kills, all in one voided statements run).
- Run-log entries 644-81x; ~245 commits since 822621340; none pushed.
