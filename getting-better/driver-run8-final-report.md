# Driver run #8: final report (self-tcb-reduction-driver, AUTONOMOUS, 96 h)

- **Window:** 2026-11-17T12:24Z to 2026-11-21T12:24:06Z (`getting-better/.driver-deadline` = 1795263846).
- **Branch:** `ghost-assign-bc6`. COMMIT-ONLY: nothing was pushed (334+ commits since 0057c8b94, all local).
- **Run log:** entries 1053-END in `getting-better/driver-run-log.md`.
- **Plan of record:** `getting-better/driver-run5-plan.md` with the run #6 / #7 lessons, and `getting-better/driver-run8-plan-draft.md` (§6 order; §5b r12 first).

## 0. Read first (soundness / gate status)

- **No VACUOUS result was found anywhere this run.** Every "could not be checked" probe classified at the end (6 on int75, 1 on main) is a probe the tooling builds badly, not a contract that is self-contradictory (log 1257 / 1259).
- **Main carries a TOOLING RED on its own gate (no false proof).** Since L17, route #615 makes a vacuity probe whose why3 run fails a gate FAILURE. Main's per-function probe builder still builds a malformed probe for the one-line PyVal helper `is_pstr` (in the preamble of 23 / 53 mirror files), so a whole-file proof of such a file under main's tooling ends "Verification FAILED (vacuity could not be checked)" even when every goal is Valid (pycsl: 821 / 821). The fix (u62, branch `run8-u62` 83a50f12d) is proven to remove it (pycsl / normalize / Module3_Weaver all SUCCESS incl. vacuity under it, logs 1254 / 1256) but was **not landed**: with it, 1192 previously skipped helpers get probes, and 6 of those probes are themselves rejected by why3 (4 directive-enforcement pairs, `pycsl_lib/enm` and `pycsl_lib/fut`), which turns two slow planes red (log 1252). Run #9 must land u62 together with a fix for those 6 shapes.
- **Proof-map rule gap (supervisor, log 1241):** a proof carries over only if BOTH the emission AND the proof tooling are identical. L17 carried u57's proofs across a tooling change; they were re-proved under the corrected tooling before the end (all green). Run #9 rule: any change to `bin/` or to the probe / prover tooling invalidates carry-over.

## 1. Results

| | start | end |
|---|---|---|
| `\trusted` (canonical grep) | 367 | **366** (L16 -1 `_why3_typecheck`; L17 +1 soundness-forced re-trust `normalize_prover_output`; L18 -1 `_sha256_file`) |
| Proof-axiom ledger | 3 | 3 |
| Landings | — | L15, L16, L17, L18 |
| oom_kill (pycsl-heavy slice) | 0 (reboot) | 15, all in jobs whose results were voided and re-run (§7) |

Net conversions: 2 verified (`_why3_typecheck`, `_sha256_file`), 1 soundness-forced re-trust; the run became a **soundness run**: 10 routes found / repaired (§4), most PRE-EXISTING holes that the per-batch red teams exposed.

## 2. Landings

| landing | merge | contents | gates |
|---|---|---|---|
| L15 | 899b6869d | route #611 r12 (an unverifiable bytecode cache refuses; `_co_code_adaptive` compared) + batch B refusals (R1 / R2 / R4) | v66 A/C/D/E + --slow 85/85; mirror-inert; read-only review cr63 |
| L16 | 96b4070a1 | batch A: typed tuple-return exception + `_why3_typecheck` VERIFIED | v70 85/85; statements 30524/30524, stmt_control_flow 16326/16326, pycsl 820/820; rt64 clean |
| L17 | f62c7af65 | soundness pack: #613 rounds 1-3, #612, #615, #616, #429 (+ the forced re-trust) | v72 85/85; reviews rt66 / rt69 / rt71 / rt72 |
| L18 | b9c025081 | batch C (`_sha256_file` on an abstract `py_path` model), R614 (#614 / #617 fail-closed), #429 narrowing-2 import closure (u59), #613 dependency search order (u60) | v73 A/C/D/E + F2 --slow 85/85; pycsl 821/821 incl. vacuity (corrected tooling, identical emission); rt73 / rt74 no introduced finding |

## 3. Conversions and re-trusts

- `_why3_typecheck` (pycsl.py) — L16.
- `_sha256_file` (pycsl.py) — L18, after three red-team repair rounds on its `Path(<str>)` model (string-typed model conflated Path with str: rt65, rt67, rt70 -> type separation lvZ2, rt73 clean).
- **Soundness-forced re-trust (+1, not progress):** `proof2why3/normalize.py::normalize_prover_output` (L17, route #429): its verified `str.replace` with 3-byte UTF-8 patterns had been proved over a Latin-1 string model.

## 4. Routes

| route | what | class | status |
|---|---|---|---|
| #611 r12 | forged / unverifiable `__pycache__` pyc | PRE-EXISTING | L15 |
| #612 | `Callable` parameter assumed pure | PRE-EXISTING | L17 |
| #613 | transitive / implicit stdlib and third-party shadowing, startup hooks, computed names, cwd root, namespace portions, dependency search order (USER DECISION: top priority, recursive) | PRE-EXISTING (+ introduced gaps of the withdrawn `--as-package-module`, never landed) | L17 + L18; **OPEN: V1D, v1f, V2D (u61, run #9), O1 over-refusal** |
| #614 | Path conflated with str (batch C's model) | INTRODUCED by batch C | L18 (type separation) |
| #615 | dead why3 run counted as a verdict; main-phase truncation | PRE-EXISTING | L17 |
| #616 | call-site probe rewriter counted parens in string literals (13 probes never ran; all now run, none vacuous) | PRE-EXISTING | L17 |
| #617 | `#31` Path-to-string erasure reached comparisons via aliases / imported callees | PRE-EXISTING | L18 (R614 fail-closed) |
| #429 | non-Latin-1 str literals modelled as UTF-8 bytes (`len("😀") == 4` proved) (USER DECISION) | PRE-EXISTING | L17 + L18 |
| #618 | `<Path> / <str>` and `os.path.join` share one op | PRE-EXISTING | **OPEN** |
| (u62) | per-function probe builder malformed for one-line `let` (is_pstr) — 23 / 2349 probes rejected at base; silently "not vacuous" before #615 | PRE-EXISTING tooling | **OPEN on main** (fix on `run8-u62`) |

## 5. Red team / review rounds

rt63 (stopped before probing by a safety classifier; replaced by the read-only review cr63, supervisor 13:25Z), rt64 (batch A: clean), rt65 / rt67 / rt70 / rt73 (batch C), rt66 / rt69 / rt72 / rt74 (#613), rt68 (batch D: exposed #429), rt71 (#429), cr63. A driver-written brief for the #613 executor was also stopped by a classifier; the supervisor wrote it (logs 1090 / 1094). Every INTRODUCED finding was repaired before its batch landed; nothing landed with an open introduced finding.

## 6. Decisions

**Supervisor defaults for the plan-draft §5 open items (FLAGGED for the user):** (1) red team per batch BEFORE landing — applied throughout; (2) batch A GO, expressions / statements proofs never overlapping — applied; (3) #497, #414, PyCSLError line>=0, #461/#488, `\diverges` untouched (#429 was later decided by the USER); (4) the str-subscript IndexError gap NOT made a corpus-wide obligation.

**User decisions this run:** #613 top priority, recursive (2026-11-18 ~08:10Z); #429 refusal-only fix (2026-11-19 ~16:25Z).

**User-visible decisions to confirm:**
- `--verification-image ROOT` for the mirror gates only ("no CPython-run claim", never inferred, token-guarded env hand-off) — log 1140.
- `--as-package-module` WITHDRAWN (four introduced gaps) — log 1186.
- Stale timestamp pyc ignored as CPython does (TOCTOU class) — log 1071.
- Declared over-refusals: 2160 (#614), 10251 (batch C: expected PASS, now a type error), 3600 (unchanged), local `test/` / `test.py` / `pip.py` / any site-package-named helper beside a program (#613 G6 / O1: no sound narrowing exists on this host, log 1226).
- A why3-rejected call-site probe body is a gate failure (#616).
- Batch D (negative slice bound model) DEFERRED: no `\trusted` gain and its expressions.py vacuity phase could not complete under the 6 GiB per-job cap.

## 7. Proof budget, tooling coverage, incidents

- heavy.sh stayed at 2 proof slots; every heavy job went through it; expressions and statements whole-file proofs never ran together.
- oom_kill 0 -> 15: the driver's expressions.py proofs (snapD / snapD2, vacuity probes at 3-4.5 GB) and one executor batch; all affected results voided. This exposed route #615.
- **Tooling under which each mirror file's LAST whole-file proof ran (supervisor, log 1248):**
  - pycsl.py, proof2why3/normalize.py, frontend/Module3_Weaver.py: int75 tooling (u62's corrected probe builder; NOT landed) — SUCCESS incl. vacuity.
  - module6_whyml/statements.py, module6_whyml/stmt_control_flow.py: snapA (b65e75bfc), pre-#615 / #616 tooling.
  - types.py, proof_axiom_allowlist.py: lvY's branch (not landed), pre-#615.
  - every other mirror file: last proved in run #7 or earlier, pre-#615 / #616 tooling.
  - => every mirror file except the first three must be re-proved in run #9 under the landed (and then the u62) tooling.
- **Newly probed helpers, UNCHECKED until run #9 re-proves their files** (u62 census, +1192 probes in total): pycsl +107, frontend/__init__ +107, ir_resolve +107, Module5_IREmitter +104, expressions +83, statements +73, stmt_control_flow +68, and the rest (pycsl's are now checked: 227 probes, none vacuous).
- Incidents: the 2-slot queue was the bottleneck (jobs waited up to 15 h); several red teams relied on emission-level evidence; executor branches committed `progress.txt` (untracked before every landing); the driver's own proveq.sh first ran a mirror file without `--verification-image` (log 1236).

## 8. Open items for run #9

1. Land u62 (probe builder) together with a fix for the 6 probe shapes it still builds badly (4 directive pairs, enm `_auto_counter`, fut `annotations`); then re-prove every mirror file (proof-map rule).
2. #613 V2D (u61 rule on `run8-u61`, needs a corpus-loadable witness shape), V1D and v1f (OPEN pre-existing holes).
3. #618 (Path `/` vs os.path.join); full (T) type separation incl. #31-erased parameters (lvZ's spike: 24 corpus / 9 mirror movers).
4. Batch D (negative slice bound): needs an expressions.py proof whose vacuity phase fits the memory cap.
5. Plan-draft §6 items not reached: type_of_batch, receiver-reading str methods, _to_cache_payload, parse_format, _synthesize_block, bases_closure, subprocess.run cwd= / timeout=.
6. #613 residuals: TOCTOU, writable install dir, runtime environment, program-chosen dynamic imports, O1.

## 9. End state

- `ghost-assign-bc6` at L18 (b9c025081) plus the final log / report commits; `\trusted` 366; ledger 3; nothing pushed.
- Kept branches (commit-only): run8-u50 ... run8-u62, run8-lvW / lvX / lvY / lvZ / lvZ-spikeT / lvZ2 / lvZ2-r614, run8-int67 ... run8-int75.
- Evidence archived under `scratchpad/run8/evidence/` (executor scratch tarballs, re-proof logs) and `scratchpad/rt63` ... `scratchpad/rt74`.
- Cleanup at the deadline: see the RUN #8 END log entry.
