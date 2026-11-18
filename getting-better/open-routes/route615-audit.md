# Route #615 audit: whole-file mirror proofs with OOM kills in their own scope

Executor u54, driver run #8, 2026-11-18. Task 2 of `scratchpad/run8/brief-u54.md`.

This audit only reads records. No proof was re-run for it, as the brief requires. The vacuity re-runs it calls for are listed at the end for the driver to schedule.

## Why this matters

Before the #615 repair, a vacuity probe whose why3 process was killed returned "not vacuous" without saying so. This applies to the per-function `ensures false` probe in `src/pycsl/pycsl.py::_run_vacuity_gate._probe_one`. A killed why3 surfaces no JSON record for the injected goal, and "no record" was read by the #260 arm as "no normal exit", which means not vacuous.

The call-site probe (#267) printed `could not be checked (no probe goal surfaced ...)` and then carried on. It did not fail the gate either.

The driver's acceptance rule from run #5 / #6 compared the set of `could not be checked` lines with a clean run's set. That rule can catch killed **call-site** probes, which is how int48 stmt_control_flow was voided (log 585). It **cannot** catch a killed **per-function** probe, because that probe printed nothing at all.

## Sources and how far back they go

- `journalctl --list-boots` keeps **10 boots**, from **2026-08-10 13:52Z** (boot -9) to now (boot 0, started 2026-11-17 12:14:35Z). The pre-reboot boots are all retained: -1 is 2026-11-13 08:48Z to 2026-11-17 12:09Z, and -2 is 2026-10-31 13:26Z to 2026-11-13 08:47Z.
- Kernel log: `journalctl -k -b <n>` for n = -9..0. Every `Killed process` line was paired with the `oom-kill:` line before it, which gives the `task_memcg` (the scope). There are 98 kills in all, in `witnesses-r615/route615-journal-kills.tsv`.
- User journal: `journalctl --user -b <n>` gives each scope's `Started run-p<PID>-*.scope - [systemd-run] <cmd>` line and its `Consumed ... wall clock` line, in `witnesses-r615/route615-journal-scopes.txt`. The user journal has no entries for boots -9 to -4, so the 2026-09 tmux-scope kills have no recoverable command line.
- Run logs: `scratchpad/run{5,6,7,8}/*-proofs.txt` (the `oom a->b` field exists only from run #8 on; every run #8 row reads `oom 0->0`), the per-file proof logs in `scratchpad/run5`, `run6` and `run8`, and `getting-better/driver-run-log.md`.

## Kills inside heavy.sh proof scopes

80 of the 98 kills are inside `pycsl-heavy.slice` scopes. They fall in five scopes, and each scope is one whole-file mirror proof. The command lines below come from the user journal.

| # | Scope | Proof (tree, commit) | Window (start - end, UTC) | Kills in scope | What was killed | Outcome then | Load-bearing today? |
|---|---|---|---|---|---|---|---|
| A | `run-p1312788-i22265030` | `module6_whyml/stmt_control_flow.py` on **int39** (`/home/fabrice/git/pycsl-int39`, branch `run5-int39`, tip `a1c0cbf50`) | 2026-11-06 00:59:18 - 07:14:40 | **1** (05:39:03, why3 pid 2116324, 1.06 GB, memcg) | **Undetermined.** The main goals finished between log 528 (04:56Z, "running") and log 529 (05:56Z, "16353 goals so far"). The vacuity pass was seen at 06:55Z (log 532). A kill in the vacuity phase would have been silent if it hit a per-function probe. | **ACCEPTED** as clean (log 533: 16353/16353 SUCCESS incl. vacuity). It was later used as the "clean" reference set for stmt_control_flow (logs 585, 599). Log 583 mentions "one isolated kill at 2026-11-06T05:39Z" but does not attribute it to this proof. | No. stmt_control_flow was re-proved on int50 (log 599, after the kill window), int55f, int61y, and on run #8 snapA @ `b65e75bfc` (16326/16326, `oom 0->0`). **Caveat:** int39's `could not be checked` set ({_handle_if_stmt, _handle_return_stmt}) was used as the clean baseline. That set is unaffected, because a killed call-site probe would have **added** an entry and a killed per-function probe adds none. |
| B | `run-p760921-i25913590` | `module6_whyml/statements.py` on **int48** (`pycsl-int48`, branch `run5-int48`, tip `b105e8d87`) | 2026-11-07 01:47:58 - 11:09:07 | **47** (03:08:25 - 05:32, why3, 0.8-3.2 GB each, memcg at the 9.66 GB slice cap) | **1 kill in the main-goal phase** (03:08:25, 3.17 GB; log 588 says the main goals finished 03:29Z). **46 kills in the vacuity phase** (03:39-05:32). | **ACCEPTED** (log 593: 23799/23799, SUCCESS incl. vacuity). The reason given was that the `could not be checked` set equalled the clean 2026-10-31 run's. **That rule was blind to killed per-function probes**, so with up to 46 vacuity-phase kills this acceptance rested on the fail-open path. The proof map of landing L1 (log 597) used this proof for statements. | Not for the current main. statements was re-proved on int55s2 (log 703, `oom_kill 75` unchanged during the run), int56s, int61x, and run #8 snapA @ `b65e75bfc` (30524/30524, `oom 0->0`). It **was** load-bearing for run #5's landing L1 (main <- int50). That landed state's statements vacuity claim was never genuinely re-checked on that emission. It has since been superseded. |
| C | `run-p708007-i25872190` | `module6_whyml/stmt_control_flow.py` on **int48** | 2026-11-07 01:19:51 - 06:29:27 | **22** (03:39 - 05:16) | Vacuity phase: 4 extra call-site `could not be checked` lines appeared (log 585). Any per-function kills were silent. | **NOT accepted** (log 585). Re-run on int50 and accepted (log 599). | No. |
| D | `run-p2592390-i31946341` | `module6_whyml/statements.py` on **int55** (`pycsl-int55`, branch `run6-int55`, at `2779fa844` when started) | 2026-11-09 11:49:47 - 17:04:31 | **5** (13:07:11 x2, 16:42:36 x2, 16:53:18) | Vacuity phase (log 680: "vacuity-phase why3 children"; main goals 30430/30430 by 14:33Z). | **VOID** (log 686, `scratchpad/run6/int55s-VOID-statements.log`). Re-run int55s2 accepted (log 703). | No. |
| E | `run-p3133659-i3136011` | `module6_whyml/expressions.py` on **snapD** (`pycsl-snapD` @ `3b2cec32c`) | 2026-11-18 12:16:31 - 14:17:10 | **5** (14:12:02, 14:13:40 x2, 14:16:07 x2; 1.7-4.4 GB) | Vacuity phase (log 1112: live children were `-g /tmp/.pycsl_vac_*.mlw:<line>`; the main goals 51087/51087 were printed before). | **STOPPED** by the driver (log 1113, `scratchpad/run8/snapD-expr-run1-killed.log`). Re-run snapD2 at PRIO with PYTHON_CPU_COUNT=2. | Pending. snapD2 is the proof that will carry expressions.py. It must show `oom_kill` unchanged over its window. With #615 landed, any killed probe also turns the run red. |

### Kills outside heavy.sh scopes (no recoverable proof)

| Date (UTC) | Process | Scope | Note |
|---|---|---|---|
| 2026-09-08 20:44:12 | why3 pid 1836944, 0.87 GB, **global** OOM | `tmux-spawn-a4f0e5e7-...` | A pre-heavy.sh session run. The user journal for boot -9 is empty, so the command line cannot be recovered. A global OOM also killed the user `systemd` / `sd-pam` (session death). |
| 2026-09-26 21:46:26 | why3 pid 4091604, 0.87 GB, **global** OOM | `tmux-spawn-f67068b4-...` | Same pattern (boot -7). The command cannot be recovered. |
| 2026-10-27 01:14 / 08:10, 2026-11-01 22:09, 2026-11-18 09:26 | python3 / python, 7.2-12 GB, global OOM | tmux scopes | The whole interpreter was killed. A pycsl run killed this way prints no verdict, so this is not fail-open. 2026-11-01 is the known CPython-probe OOM (RULES.md #3). |

These two why3 kills cannot be tied to a recorded proof. Any proof accepted from a session run on 2026-09-08 or 2026-09-26 that overlaps those times is unverifiable from the journal. Every whole-file mirror proof since then has been re-run, so none of them is load-bearing today.

## Second finding: the main-goal phase has a related fail-open

A whole-file proof's main goals come from ONE full-file `why3 prove -P Z3 --json` run (`_dispatch_provers`, first attempt). If that run is killed after it has streamed some records, and every streamed record is Valid, then `_dispatch_provers` early-exits with `rc 0` and fewer goals. `_check_goal_conservation` compares against that same truncated first run, so it does not catch the loss. The only defence today is a reviewer comparing `total` with an earlier run's goal count.

Row B's 03:08:25 kill falls in the main-goal window. Its 23799/23799 total cannot be checked against a same-emission clean run, because no other statements proof of the int48 emission exists. The #615 repair also closes this in the proof driver: a signal-killed why3 run now fails `_dispatch_provers`. See `getting-better/run8-u54-report.md` for whether that change was made and how it was witnessed.

## Re-runs for the driver to schedule

None is needed for the current main. Every proof above is superseded by a later proof of the same file that was clean on `oom_kill`, except row E, which is in progress.

1. **E (snapD2 expressions.py)**: accept only if `oom_kill` is unchanged across its window. Once #615 is landed, also check that the log has no `could not be checked: ... route #615` lines.
2. **Historical (optional):** if run #5's landing L1 must be re-certified as it was, re-run the statements.py vacuity phase on the int48 emission (row B). The current main does not depend on it.
3. Going forward, the acceptance rule "same `could not be checked` set as a clean run" stays useful for intrinsic call-site rejections. After #615, a killed probe is a hard FAIL, not an extra line, so a run with any kill in its scope is red by construction when the kill hit a probe.
