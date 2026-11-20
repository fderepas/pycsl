# Driver run #8: final report (self-tcb-reduction-driver, AUTONOMOUS, 96 h)

- **Window:** 2026-11-17T12:24Z to 2026-11-21T12:24:06Z (`getting-better/.driver-deadline` = 1795263846).
- **Branch:** `ghost-assign-bc6`. COMMIT-ONLY: nothing was pushed.
- **Run log:** entries 1053 onward in `getting-better/driver-run-log.md`.
- **Plan of record:** `getting-better/driver-run5-plan.md` with the run #6 / #7 lessons, and `getting-better/driver-run8-plan-draft.md` (order of §6, §5b r12 first).

## 1. Results

| | start | end |
|---|---|---|
| `\trusted` (canonical grep) | 367 | **L18_TRUSTED** (see §2; 366 at L16; 367 at L17 = 366 + one soundness-forced re-trust) |
| Proof-axiom ledger | 3 | 3 |
| Landings | — | L15, L16, L17 LANDING_L18 |
| oom_kill (pycsl-heavy slice) | 0 (reboot) | 15 — all inside two driver proofs and one executor batch whose results were voided and re-run (§7) |

Run #8 turned into a **soundness run**. The conversion batches (A, C, D) produced a single landed conversion until the end (batch A); every world-model or value-model change was red-teamed before landing, and the red teams kept finding false proofs — mostly PRE-EXISTING ones the new rounds exposed — which, by the user's and supervisor's decisions, took priority.

## 2. Landings

| landing | merge | contents | gates |
|---|---|---|---|
| L15 | 899b6869d | S1: route #611 r12 (a bytecode cache that is not provably the compilation of its source refuses; `_co_code_adaptive` compared) + batch B refusals (R1 PYVAL-SLICE, R2 LAUNDER-OWN-RESULT-CLAUSE, R4 STR-RFIND-RECEIVER-DROPPED) | v66 A/C/D/E + --slow 85/85; mirror-inert; independent read-only review cr63 |
| L16 | 96b4070a1 | batch A: typed tuple-return exception `Return_tup_<codomain>` + `_why3_typecheck` VERIFIED (\trusted 367 -> 366) | v70 85/85; statements 30524/30524 + stmt_control_flow 16326/16326 (snapA) + pycsl 820/820; red team rt64 clean |
| L17 | f62c7af65 | soundness pack: routes #613 (transitive / blanket stdlib and third-party shadowing; startup hooks; computed stdlib names; cwd root; namespace portions; `--verification-image` for the mirror; `--as-package-module` withdrawn), #612 (Callable parameters), #615 (dead why3 run = failure; main-phase truncation), #616 (call-site probe rewriter; rejection = failure), #429 (non-Latin-1 str literals; narrowing 2) | v72 85/85; mirror movers byte-identical to proved emissions; reviews rt66 / rt69 / rt71 / rt72 |
| L18 | L18_MERGE | L18_CONTENTS | L18_GATES |

## 3. Conversions

- `_why3_typecheck` (pycsl.py) — L16 (batch A, sp5's GO).
- `_sha256_file` (pycsl.py) — batch C; landed only if L18 landed (L18_SHA).
- **Soundness-forced re-trust (+1, not progress):** `proof2why3/normalize.py::normalize_prover_output` (L17). Its verified `str.replace` with 3-byte UTF-8 patterns had been proved over a Latin-1 string model (route #429).

## 4. Routes found and repaired this run

| route | what | found by | class | status |
|---|---|---|---|---|
| #611 r12 | forged / unverifiable `__pycache__` pyc beside a source pycsl reads | run #7 rt62 residual; u50 | PRE-EXISTING (10125-10127 proved at base) | L15 |
| #612 | `Callable` parameter assumed pure (two calls equal) | lvX (side finding) | PRE-EXISTING | L17 |
| #613 | transitive / implicit stdlib and third-party shadowing; cwd root; dependency search order | USER DECISION (priority), u52 / u55 / u58 / u60, reviews rt66 / rt69 / rt72 / rt74 | PRE-EXISTING (plus INTRODUCED gaps of the withdrawn `--as-package-module` mode, never landed) | L17 (+ u60 A1 in L18) |
| #614 | Path value conflated with its string (batch C's model) | rt65, rt67, rt70 | INTRODUCED by batch C | repaired by type separation (lvZ2) — L18 |
| #615 | vacuity probe whose prover died counted "not vacuous"; main-phase truncation accepted | driver (oom kills in snapD) | PRE-EXISTING | L17 |
| #616 | call-site probe rewriter counted parens inside string literals; 13 landed probes never ran | u54 / supervisor | PRE-EXISTING (all 13 now run: none vacuous) | L17 |
| #617 | Path-annotated values erased to string (#31) reached comparisons via aliases / imported callees | rt67 / rt70 | PRE-EXISTING | R614 fail-closed (L18) |
| #429 | non-Latin-1 str literals modelled as UTF-8 bytes (`len("😀") == 4` proved) | rt68 | PRE-EXISTING; USER DECISION to refuse | L17 (+ u59 narrowing-2 closure in L18) |
| #618 | `<Path> / <str>` and `os.path.join` lowered to the same `path_join_op` | rt73 | PRE-EXISTING | OPEN (run #9) |

## 5. Red team / review rounds

rt63 (stopped before probing: safety classifier; replaced by the read-only review cr63 per supervisor), rt64 (batch A: clean), rt65 / rt67 / rt70 / rt73 (batch C: three repair rounds; rt73 clean), rt66 / rt69 / rt72 / rt74 (#613), rt68 (batch D: exposed #429), rt71 (#429: narrowing-2 hole, pre-existing), cr63 (r12 review). A brief for a #613 executor was also stopped by a classifier (log 1090); the supervisor wrote it instead (log 1094).

## 6. Decisions

**Supervisor defaults for the plan-draft §5 open items (FLAGGED for the user):** (1) red team per batch BEFORE landing (applied throughout); (2) batch A GO with the expressions / statements proofs never overlapping (applied); (3) #497, #414, PyCSLError line>=0, #461/#488, `\diverges` untouched (#429 was later decided by the USER, 2026-11-19 ~16:25Z); (4) the str-subscript IndexError gap NOT made a corpus-wide obligation.

**User decisions relayed this run:** route #613 is top priority and must be recursive (2026-11-18 ~08:10Z); #429 refusal-only fix now (2026-11-19 ~16:25Z).

**User-visible driver / supervisor decisions to confirm:**
- `--verification-image ROOT` (mirror gates only; "no CPython-run claim"; never inferred; token-guarded env hand-off) — log 1140.
- `--as-package-module` withdrawn (its four introduced gaps) — log 1186.
- Stale timestamp pyc: ignored as CPython does (TOCTOU class) — log 1071.
- 2160 declared over-refusal (#614); 10251 declared over-refusal (batch C, expected PASS now a type error); 3600 still a declared over-refusal; a local `test/` / `test.py` / `pip.py` / site-package-named helper beside a program is refused (#613 G6 / O1, no sound narrowing on this host).
- The rc-1 "why3 rejected the probe" warning (13 landed probes) became a gate failure once all probes ran (#616).
- Batch D (negative slice bound model) DEFERRED: its expressions.py vacuity phase could not complete under the 6 GiB per-job cap; it adds no `\trusted` gain.

## 7. Proof budget and incidents

- heavy.sh stayed at 2 proof slots; every heavy job went through it; expressions / statements whole-file proofs never overlapped.
- oom_kill 0 -> 15: 5 + 2 kills in the driver's expressions.py proofs (snapD / snapD2, vacuity probes at 3-4.5 GB each, results voided and stopped), the rest in one executor batch (voided). This exposed route #615.
- The 2-slot queue was the run's bottleneck: executors and red teams waited up to 15 h for a slot; several red teams had to rely on emission-level evidence.
- Housekeeping: executor branches committed `progress.txt`; every integration tree untracked it before landing.

## 8. Open items for run #9

- Route #618 (Path `/` vs os.path.join).
- Full (T): a distinct WhyML type for every Path value, including #31-erased parameters (lvZ's spike measured 24 corpus / 9 mirror movers).
- Batch D: model the negative slice bound once an expressions.py proof with a checked vacuity phase fits (lower memory per probe).
- Re-run vacuity phases for the 5 functions whose call-site probes now type-check but were not run alone (u56).
- The plan-draft §6 items not reached: type_of_batch (needs preamble Optional field typing), receiver-reading str methods, _to_cache_payload, parse_format, _synthesize_block, bases_closure, subprocess.run cwd= / timeout=.
- The #613 residuals (TOCTOU, writable install dir, runtime env, program-chosen dynamic imports, O1 over-refusal).

## 9. End state

END_STATE
