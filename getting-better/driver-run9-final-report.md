# Driver run #9: final report (self-tcb-reduction-driver, AUTONOMOUS, 96 h)

- **Window:** 2026-11-21T21:25:23Z to 2026-11-25T21:25:23Z (`.driver-deadline` = 1795641923).
- **Branch:** `ghost-assign-bc6`. COMMIT-ONLY: nothing was pushed.
- **Run log:** entries 1269 to the "RUN #9 END" entry in `getting-better/driver-run-log.md`.
- **Interruptions:**
  - API weekly rate limit, ~07:25Z-11:24Z on 2026-11-23 (logs 1325 / 1326).
  - User PAUSE, 20:31Z-22:10Z on 2026-11-23 (logs 1346-1349).
  - Two /tmp user-quota incidents, 21:35Z and 22:27Z on 2026-11-23 (logs 1349-1352). Every affected result was voided and re-run. All driver and executor jobs then moved to a TMPDIR on the repo volume.
- **oom_kill:** 15 at the start and 15 at the end. No job was OOM-killed during the run.

## 0. Read first (soundness)

- **No VACUOUS verdict anywhere.** That covers every mirror whole-file proof (§6), every red-team round and every gate.
- **Priority 1 is done (L19).** Main no longer fails its own non-vacuity gate on the `is_pstr` probe. u62 + u63 fixed the 7 badly built probe shapes (parameterless lets, `let constant`). The type-only census found 0 rejected over 5430 emissions / 16771 probes.
- **Introduced false proofs: all caught before landing, all repaired.**
  - u66's s1 / s8, repaired by u69 (L21).
  - u74's F1 (float record field), repaired by u76.
  - u76's b1, a hidden FLOAT-FINITE reliance, repaired by u77: the soundness report now declares it.
  - u77's K1, a latent defect that failed closed, repaired by u78.
- **Pre-existing false proofs closed this run:** routes #619, #620, #621, #622, #623, #624, #625, #626, #627, #628, #629, #630, #631, #632, #633, #634 (record / list parameter), #635 (listed modules) and #636.
- **Pre-existing false proofs still OPEN:** see §8.
  - #642: rt86's 11 program-file bypasses.
  - #643: rt87's a1 / d1b / s1 / g9, the `assigns` frame on a partial record, a dict, a set or a module global.
  - #637-#641 (rt85).
  - v1f and V1D (#613), #618, and rt82 W1 / W2.

## 1. Results

| | start of run #9 | end of run #9 |
|---|---|---|
| `\trusted` in the mirror | 366 | 365 at L23; **364** once L24 lands (§2) |
| proof-axiom ledger | 3 | 3 (no new axiom) |
| landings | L18 | L19-L23 (+ L24 / L25: see §2) |
| non-vacuity gate on main | FAILED (`is_pstr` probe) | green |

- **Conversions:**
  - `SertopSession.type_of_batch` became VERIFIED (u67, L21).
  - `audit_proof_reverify._to_cache_payload` became VERIFIED (u74, plus the u76 repair; in L24).
- **No soundness-forced re-trust** this run.

## 2. Landings

Every landing passed its own battery: A new-corpus witnesses, C byte-diff (root and pyref, both counts asserted), D mirror sweep, E fidelity and F, the 85 `--slow` planes.

| landing | merge | content | battery |
|---|---|---|---|
| L19 | c115e0a5a | probe builder (u62 + u63): priority 1 | v75: C 0 MOVED, D 0 diff, F 85 / 85 |
| L20 | de6ea9e96 | u65 #619 / #620 / #623 + u68 R327 re-witness | v77: F 85 / 85 |
| L21 | d2f5bfd4c | V2D import-resolver batch (u64 / u66 / u69 / u71: #621 / #622 / #626 / #627) + u67 (type_of_batch VERIFIED, 366 -> 365) + bespoke-model-drift plane fix | v79: D 1 mover proved 64 / 64; F 85 / 85 |
| L22 | 3a7b323c7 | u70 + u72: one identity per definition (#624 / #625 / #628 / #629 / #630) | v80: C 0 / 0 / 0, D 0 diff, F 85 / 85 |
| L23 | af47df99f | u73 + u75: import-resolver escapes (#631 / #632 / #633 / #635 / #636) | v81b: C 3 declared GONE, D 0 diff, F 85 / 85 |
| L24 | (see end state) | u74 + u76 + u77 (int85 115c761cb): `_to_cache_payload` VERIFIED (365 -> 364), F1 repair, #634 `PYCSL-FUNCTION-FRAME`, honest FLOAT-FINITE report, c15 narrowing | v85: A 42 / 42, C 5 declared GONE, D 2 movers proved (88 / 88, 111 / 111) |
| L25 | (see end state) | u78 (int86 cfbb04668): K1 / f19 refusal-only repair | v86: C 5 declared GONE (the same as v85), D == int85 |

## 3. Red teams (one round per batch, run BEFORE landing)

| round | batch | introduced false proof | resolution |
|---|---|---|---|
| rt75 | probe builder | none | 2 pre-existing gate escapes -> #619 / #620 (closed in L20) |
| rt76 / rt78 / rt79 / rt81 | V2D | rt81: s1 / s8 (u66) | repaired by u69 before L21 |
| rt77 | u65 | none (F3, a gate-honesty finding) | repaired by u68 |
| rt80 / rt85 | u70 / u72 | none | O1-O4 declared; #637-#641 opened (pre-existing) |
| rt82 | u67 | none | W1 / W2 open (pre-existing) |
| rt83 / rt86 | u73 / u75 | none | o3 / m1 / m4 declared; #642 opened (11 pre-existing bypasses) |
| rt84 | u74 | F1 | repaired by u76 |
| rt87 | u74 + u76 | b1: a FLOAT-FINITE reliance missing from `--soundness-report` | repaired by u77; c15 over-refusal repaired; #643 opened (pre-existing) |
| rt88 | u77 | none; K1 latent, failed closed | repaired by u78 (refusal-only; its C leg shows 0 new GONE) |

## 4. Decisions taken by the driver

These are all fail-safe; each one only refuses more.

- **Declared over-refusals:**
  - rt85 O1-O4;
  - rt86 o3 / m1 / m4;
  - corpus 6026 (`os.path` in a set);
  - the `f = b.f` assign re-export (qe72, 10451; log 1409);
  - 0337, a fixture whose `assigns \nothing` was false;
  - 9063, which was expected to FAIL and is now refused;
  - w19c.
- **Data-only bin/ changes:** census rows do not void proofs (strace audit, log 1291).
- **Batches were folded to fit the deadline:** L23 went first (u73 + u75), then L24 (u74 + u76 + u77), then L25 (u78).

## 5. User-visible items, waiting on the user

- `--import-path ""` (z1), and an `--import-path` directory that does not exist (z5). Both are refused; they stay declared.
- The over-refusals in §4.
- **Side effect of #634:** an imported user-`\trusted` function whose real body writes a parameter outside its declared frame is now refused in the importer.
- **Model assumption:** reading a float record field now lists FLOAT-FINITE in `--soundness-report`. `--strict-float-finite` refuses such programs (u77).

## 6. Mirror proof map (per file, PROOF-MAP rule: same emission AND same tooling)

- **Probe tooling for the whole run after L19:** vac 4f0d913f4e, why3.conf 7f7c546820, provers 2ba89a01.
- **50 files** were whole-file proved, vacuity included, in campaign c20 on int77. int77's mirror emission is identical to main through L23, checked by every battery's D leg. One exception: proof2why3/sertop moved in L21 and was re-proved on int80 (64 / 64).
- **`stmt_control_flow.py`:** the main phase is proved (16326 / 16326). Vacuity shards 1-7 did not run.
- **Not re-proved under run #9 tooling: `statements.py` and `expressions.py`.** Their jobs are in `scratchpad/run9/c20-jobs.HOLD.txt`.
- **`audit_proof_reverify.py` and `audit_proof.py`** moved in L24. Both are whole-file proved on int85: 88 / 88 and 111 / 111, rc 0. int86's emission of both is byte-identical, so the proofs carry to L25.
- **Per-file logs:**
  - `scratchpad/run9/c20-results.txt`;
  - `scratchpad/run9/p85-proofs.txt`;
  - the int80 sertop log (log 1361).

## 7. Process notes

- **heavy.sh** stayed at 2 proof slots and was not edited. All jobs went through it.
- **PRIO** let up to 4 heavy jobs run at once late in the run. oom_kill stayed at 15.
- **Quota incidents:** fixed with a TMPDIR on the repo volume. Results containing EDQUOT were voided and re-run.
- **progress.txt:** it stayed untracked in the main worktree. Executor branches never brought it in.

## 8. Open items (soundness queue)

1. **#642** (rt86): program-file gaps in rule M and #635. These are comprehension first-iterator scope, a function metaclass, wildcard-shadowed builtins, annotation evaluators, and `xml.sax` / `site` / `_pyrepl`. Fix direction: apply #483's stdlib allow-list to the program file.
2. **#643** (rt87): four more #634 variants. Each has a fix direction in `scratchpad/run9/rt87-FINDINGS.txt`.
   - a1: a partial record frame; only the root of the frame target is checked.
   - d1b / s1: a dict or set parameter.
   - g9: a module-global write under `assigns \nothing`.
3. **#637-#641** (rt85): wrong-body bindings across modules.
4. **v1f, V1D (#613), #618**, and rt82 W1 / W2.
5. **Mirror proofs** of `statements.py`, `expressions.py` and the `stmt_control_flow.py` vacuity shards under the current tooling.
6. **Debt:** 515 pre-existing expected-FAIL witnesses have no census row (u76).

## 9. Run #10 inputs

- **The run #10 brief is `getting-better/run10-brief.md`** (commit 9f83c3b0c). The supervisor wrote it on the user's request. It puts `\trusted` reduction first, and says that L24 = run9-u77 lands first if run #9 does not land it. This driver appended dated lines to its "Open inputs" list before the deadline.
- **Inputs:**
  - the §8 queue;
  - the §5 user decisions;
  - the c20 held jobs (`scratchpad/run9/c20-jobs.HOLD.txt`);
  - the rules in `scratchpad/run9/RULES.md` (1-38).
