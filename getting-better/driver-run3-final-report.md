# Driver run #3 — final report (self-tcb-reduction-driver, AUTONOMOUS, 96 h)

Window: 2026-10-25 .. 2026-10-31T07:56Z (deadline reset to 07:56Z after the 2026-10-27 session deaths).
Branch `ghost-assign-bc6`, commits `7bf752d4e..HEAD` (local only, never pushed). Run log entries 253-3xx
(`getting-better/driver-run-log.md`); driver notes and prune record in the session scratchpad `run3-notes.md`.

## 1. Iterations and landings
- 83 run-log iterations (entries 253-335), ~320 commits.
- Integration landings on main (each through a full driver battery: fidelity, root + pyref + mirror byte-diff with M1
  for every mover, fast planes, all ledgers, new-file expectations, base sample at the previous main), among them:
  c8b0aa205 (#432-#439), c53b5e381 (#411), a7f423866 (#440-#443), 7c2c20aad (#444-#459), 33f7ac681 (#460-#462),
  d6abee90b (#463-#473 + _alpha_rename), dcf424f75 (#475-#480, d1 defects), ad7cdc91d (#474 #481-#487 + slow-plane
  matchers), 2223318e5 (#488 honest frames), ddd542f97 (#489 #490), cd93786d9 (#491-#495).
- Red-team rounds rt31-rt42 (12 rounds); each round CLOSED the previous round's confirmed list completely
  (convergence re-proof with mode flags) and found new surfaces: rt38 142 -> rt39 141 -> rt40 129 -> rt41 237 -> rt42 139.

## 2. Stubs converted and trusted count
- `\trusted`: start 448 grep lines / 420 markers -> end 437 / 409 (net -11).
- 13 conversions (verbatim live body, whole-file proof 0 non-Valid, non-vacuous): pure_ast._const_value_getter,
  _const_value_setter; extract._split_rocq_check_output; canonical._iff_app_to_binop, _expand_nat_to_int,
  _sort_arrow_hypotheses, _dedup_arrow_chain, substitute, _normalize_type_string, _normalize_names, _flatten_foralls,
  _ac_normalize, _alpha_rename (canonical.py now has no trusted stub).
- 2 HONEST RE-TRUSTS (+2): errors.PyCSLError.__init__ (route #226 polarity flip; invariant line >= 0 not
  established) and expr_ghost_spec_ops._handle_mktuple_expr (route #488: its verified `assigns \nothing` was false;
  re-trusted with its true 22-field frame).
- Census (lv5 115 + cv6 294 stubs): every remaining stub has a measured first blocker; no stub is one cheap lever from
  conversion. Binding constraint = the value-model seam (int-erasure ~123 incl. its refusal side, R325 39, in-place
  mutators 40 -- measured 0/16 convert even with the mutator guard off).

## 3. Walls
- int-erasure-seam (r3): BROKEN (narrow), 1 conversion; residuals recorded in its impl.
- in-place receiver mutator: MEASURED, not the binding constraint (w1, 0/16).
- cross-mixin-declaration-stubs (review-and-break, full cycle): report (dc1) -> independent fable review (9 oracle
  runs) -> impl -> Gate S REFUTED on the ghost files (dx1) -> found route #488 (false verified frames, runtime
  witnessed) -> repaired honestly (z1) -> dc2 built B0 (frame honesty through the MRO), B2 (declaration-conformance
  plane, negative-tested) and B1 widening, all gated EXCEPT the statements.py whole-file proof (~5.5 h) -> NOT landed
  (worktree pycsl-dc2 @57dfe7b34). B4 (`#@ declared_in`) designed: -20 markers gross / -2 TCB net.

## 4. Routes
- Opened this run: #402-#495 (94), each driver-reproduced on main before opening (rp34..rp42 scripts).
- Repaired and landed: all of #402-#490 except #429 (user decision) ; #474 closed in two steps (x3 + f2); #488 repaired honestly (+1 trusted).
- Still open: none of the red-team routes #402-#495 (all landed with witnesses); #429 awaits a user decision. rt42's convergence list re-proved on the final main: see the CONVERGENCE line below.
- CONVERGENCE on the final main (cd93786d9, driver re-run 07:02Z): rt42's 139 confirmed probes -> 139/139 REFUSED.
- Slow-tier planes: found RED (artefacts, not defects) and repaired; both slow planes green on main since 2223318e5.

## 5. User-decision items
1. +1 trusted errors.PyCSLError.__init__ (proves with `requires line >= 0`; 92 construction sites in 13 mirror files).
2. #429 Latin-1 upper/lower closure.
3. #414 MemoryError assumption.
4. #461 / m1 / x1 design: the verifier partially EXECUTES the module top level at verification time (and y2's
   alternative to #483/#484 would run the program's import code inside the verifier) -- policy decision.
5. #461 Severity-2 classification; #488 Severity-2 (false frame, no consuming proof).
6. The #UND hashing residual; dict-model conversions as a certified boundary.
7. cross-mixin B4: adopt `#@ declared_in` as a distinct counted class (needs the statements.py proof first).
8. heavy.sh: NORMAL jobs share 2 slots; long single-job batteries starve the queue (consider a 3rd NORMAL slot).

## 6. Leftover worktrees
- /home/fabrice/git/pycsl -- main worktree (branch ghost-assign-bc6), unrelated dirty files untouched (heavy.sh, session.txt,
  .aux / .olean artifacts, removed w7 / w8 gitlinks).
- /home/fabrice/git/pycsl-v-s1base -- the driver's verification base, detached at the final main (cd93786d9); safe to remove.
- /home/fabrice/git/pycsl-dc2 -- KEPT ON PURPOSE: commits 7f21f1d2c..57dfe7b34 (cross-mixin B1 widening + B0 frame-honesty
  declaration arm + B2 declaration-conformance plane + impl record), all gated EXCEPT the statements.py whole-file proof
  (~5.5 h at LOW). Run that proof, then integrate; then B4 (`#@ declared_in`).
- All other executor / integration worktrees of run #3 were pruned once their work landed (record in run3-notes.md).

## 7. Lessons recorded (run3-notes.md)
- Union-merging adjacent code blocks can change loop nesting: check every executor block's neighbours after a union (done for int7-int12).
- Never `git commit -a` in the main worktree; never put backticks in a double-quoted echo; kill processes by PID, never `pkill -f` with a pattern
  that appears in the killing command (it killed the driver's shell twice).
- `rm` only with literal paths / `${VAR:?}` / python shutil (agents hung on approval prompts three times).
- Run the `--slow` planes at least once per landing day (two slow planes went RED unnoticed; both were plane artefacts).
- heavy.sh NORMAL jobs share 2 slots: split gate batteries into <= 30 min jobs; reuse the driver's base emissions instead of re-sweeping.
- Prune an executor's base worktree only after the executor returns (one slip, no loss).
