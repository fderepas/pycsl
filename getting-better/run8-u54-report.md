# run8-u54 report: route #615, a killed or crashed why3 run fails the vacuity gate

Executor u54, driver run #8. Branch `run8-u54`, tree `/home/fabrice/git/pycsl-u54`, base `41fc6f781`. This change is a refusal-only repair: it only turns runs that used to pass silently into failures. It changes no emission, adds no `\trusted` and adds no axiom.

## Commits

See the final section ("Commits (all on run8-u54, none pushed)").

## The rule

A why3 run that **died at the process level** has said nothing about a probe. It is now reported as `could not be checked` and **fails the gate** (rc 1). Before this change it was counted as passed. "Died at the process level" means:

- why3 was killed by a signal (`subprocess` returncode < 0, for example -9 from the kernel OOM killer); or
- it returned a shell-style code of 126 or more; or
- it exited non-zero with no JSON goal record on stdout.

A prover that **ran and answered** is not such a failure. That covers Valid, Invalid, Unknown, Timeout, OutOfMemory at why3's `memlimit` and StepLimitExceeded. A clean run whose selected goal set is empty (no normal exit, the #260 path) is not a failure either.

Measured why3 1.8.2 exit codes (`scratchpad/u54/rc/rc.txt`; files in `scratchpad/u54/rc/`):

| Case | rc |
|---|---|
| All Valid | 0 |
| A goal unproved | 2, records present |
| Ill-typed file | 1, diagnostic on stderr, empty stdout |
| `-g` selector matching no goal | 0, empty stdout |
| Prover over its memory limit | 2, records with answer "Out of memory" |
| why3 SIGKILLed mid-run | 137 in the shell (-9 in Python), stdout = the records already **streamed** |

Where the rule is applied (all in `src/pycsl/pycsl.py`):

1. **Per-function probe** (`_run_vacuity_gate._probe_one`, the `ensures { [@expl:vacprobe] false }` probe). The run counts as failed under any of the process-level conditions above. It also counts as failed if the injected goal's record has answer `HighFailure`, which is why3's answer when the prover child itself crashed or was killed. A failure of **any** configured prover makes the probe "could not be checked", because best-of-N lost an instrument and the dead prover might have proved `false`.
2. **Call-site probe** (#267). A signal or 126+ exit, or a non-zero exit with no JSON **and an empty stderr**, now fails the gate. The old warning `could not be checked (no probe goal surfaced ...)` is kept, unchanged and still non-failing, for a why3 that **ran and rejected the rewritten body**. That means a non-zero exit, a diagnostic on stderr and no signal (rc 1, as measured above). This is deliberate, because those rejections are **intrinsic** and already present in landed proofs: statements {_array_coerce_arg, _first_assign_kind, _wrap_body_with_return_catch}, stmt_control_flow {_handle_if_stmt, _handle_return_stmt}, pure_ast 3, expressions 5. Making them fail would turn every big mirror proof red. That is a separate decision, and I flag it here rather than take it.
3. **Gate verdict** (`_run_proofs._gate_vacuity_then_succeed`). Unchecked entries are printed under their own header, `NON-VACUITY GATE FAILED: ... COULD NOT BE CHECKED ... (route #615)`. The run then ends with `Verification FAILED (vacuity could not be checked)`, exit 1, and with `--diagnostics-json` the code `PYCSL-VACUITY-UNCHECKED`. If vacuous functions are also present, they are reported as before.
4. **Main-goal phase** (`_dispatch_provers`, a related finding made during this work). why3 **streams** its `--json` records, as measured: a run killed after 4 s left exactly its first record on stdout. So a full-file run killed after an all-Valid prefix used to **early-exit with rc 0 and fewer goals**. `_check_goal_conservation` compares against that same truncated run, so it could not see the loss. Now a signal or 126+ exit returns that rc, and the run is `Verification FAILED`.

**Mirror twins.** `_run_vacuity_gate`, the nested `_probe_one`, `_dispatch_provers`, `_run_proofs` and the nested `_gate_vacuity_then_succeed` are all `\trusted` in `src/self-annotate/src/pycsl.py`. The mirror file is not touched, so the mirror emission is unchanged and no §10.4 re-port is owed. An earlier draft also edited the `--check-vacuity` help text. I reverted it: `_parse_args` is **verified** in the mirror (not `\trusted`), so editing it would have owed a pycsl.py mirror re-port and re-proof. No helper function was extracted (rule 9).

## Witness mechanism

Everything is in `getting-better/open-routes/witnesses-r615/`. No corpus file is involved, because the mechanism needs a wrapper. Nothing is forged: the wrapper never writes a verdict.

- `bin/why3`: a why3 wrapper put first on PATH. pycsl calls `why3` through PATH. The wrapper passes every call to the real why3, except that, depending on `R615_MODE`:
  - `kill-pf`: **SIGKILLs itself**, a real signal death, when the `.mlw` is a per-function probe (it contains `[@expl:vacprobe]`).
  - `kill-cs`: does the same for a call-site probe (`[@expl:vacpost`).
  - `exit137-pf`: exits 137 with no output.
  - `ulimit-pf`: runs the real why3 under `ulimit -v 60000` for a per-function probe.
  - `kill-main`: for the main proof file, runs the real why3, relays exactly what it has streamed by the time its first goal record appears, then SIGKILLs it and itself.
- `run-r615.sh <tree> <outdir>`: runs the full pycsl proof (vacuity gate on, the default) of corpus 2823 (#267 control: a `\trusted` callee on one branch, so both probes run) and 0351 (`sorted` val) under each mode, plus `w615_main_kill_ctl.py` under `off` / `kill-main`. It prints `mode, file, rc, verdict, count`.
- `w615_main_kill_ctl.py`: `a_succ` (easy, emitted first) and `z_cube_sum` (Fermat n = 3: true, but Z3 times out on it). Its honest verdict is FAIL.

## Base vs head

Base is `/home/fabrice/git/pycsl-u54-base` @ `41fc6f781`. Head is the snapshot `/home/fabrice/git/pycsl-u54-s1` @ `706e19e29`, whose src is identical to the final commit's.

| Mode | File | BASE | HEAD |
|---|---|---|---|
| off | 2823 / 0351 | rc 0 SUCCESS | rc 0 SUCCESS |
| kill-pf | 2823 / 0351 | **rc 0 SUCCESS, 0 "could not be checked"** (fail-open) | rc 1 `Verification FAILED (vacuity could not be checked)` |
| exit137-pf | 2823 / 0351 | **rc 0 SUCCESS** | rc 1 FAILED (vacuity could not be checked) |
| kill-cs | 2823 / 0351 | **rc 0 SUCCESS** + 1 warning line | rc 1 FAILED (vacuity could not be checked) |
| ulimit-pf | 2823 / 0351 | rc 0 SUCCESS | rc 0 SUCCESS (see below) |
| off | w615main | rc 1 FAILED (Timeout) | rc 1 FAILED |
| kill-main | w615main | MAIN_BASE | MAIN_HEAD |

`ulimit-pf` is the same at base and head by design. Under the 60 MB cap the why3 process survives, and its **prover** child reports `Out of memory` inside a normal record (rc 2), just like a timeout. That is a prover that ran and hit a budget, not a dead run. If the driver wants OutOfMemory answers on the injected goal to fail too, it is a one-line change in the `_hf615` filter. I did not make it because of the risk of making landed probes fail without a measurement.

Logs:

- `scratchpad/u54/wit-base.tsv` and `wit-base/` (job1).
- `scratchpad/u54/h1/witbase.tsv` and `h1/wit.tsv`, with `h1/witbase/` and `h1/wit/` (job2).
- `scratchpad/u54/m-base.tsv` and `m-head.tsv`, with `m-base/` and `m-head/` (job3, the corrected main witness). All are under `/home/fabrice/git/pycsl-u54/`.

A head log line, from `h1/wit/kill-pf-2823.log`:

```
[-] vacuity probe for 'g' could not be checked: the why3 run itself FAILED (prover Alt-Ergo,2.6.3,, exit code -9, signal 9, 0 goal record(s) on stdout).
[-] NON-VACUITY GATE FAILED: the vacuity probe of the following function(s) COULD NOT BE CHECKED ...
    g [could not be checked: the vacuity probe's why3 run FAILED (prover Alt-Ergo,2.6.3,, exit code -9) — route #615]
[-] Verification FAILED (vacuity could not be checked). Check the solver output.
```

## Audit (Task 2)

The full audit is in `getting-better/open-routes/route615-audit.md`. Its evidence is in `witnesses-r615/route615-journal-kills.tsv` (98 kernel kills) and `route615-journal-scopes.txt`.

The journal keeps 10 boots, back to **2026-08-10**, and the pre-reboot boots -1 and -2 are retained. 80 kills fall inside 5 heavy.sh scopes, each a whole-file mirror proof:

| Proof (tree) | Date | Kills in scope | Hit | Then | Load-bearing now |
|---|---|---|---|---|---|
| stmt_control_flow (int39, `a1c0cbf50`) | 11-06 | 1 (05:39) | undetermined (main ended 04:56-05:56Z) | ACCEPTED, used as the "clean" reference | no (re-proved int50, int55f, int61y, snapA) |
| statements (int48, `b105e8d87`) | 11-07 | 47 (1 in main phase, 46 vacuity) | vacuity probes, and one main-phase why3 | **ACCEPTED (log 593) by a rule blind to killed per-function probes** | not for main today (re-proved int55s2, int56s, int61x, snapA); it **was** load-bearing for run #5 landing L1 |
| stmt_control_flow (int48) | 11-07 | 22 | vacuity | not accepted (log 585) | no |
| statements (int55, `2779fa844`) | 11-09 | 5 | vacuity | VOID (log 686) | no |
| expressions (snapD, `3b2cec32c`) | 11-18 | 5 | vacuity | STOPPED (log 1113) | pending: snapD2 |

There are also two global-OOM `why3` kills in tmux scopes (2026-09-08, 2026-09-26) whose command lines cannot be recovered, and 4 whole-interpreter python kills, which are not fail-open. No re-run is needed for the current main. For snapD2, accept it only if `oom_kill` is unchanged over its window.

**Observed while working:** the slice `oom_kill` was **15** when my job1 started (19:45Z). It was 5 at log 1114. The 10 new kills came from other jobs. My jobs were 15 -> 15 throughout.

## Gates

HEAD snapshot `pycsl-u54-s1` @ `706e19e29` against BASE `pycsl-u54-base` @ `41fc6f781`, swept by me (base8 not used: my base is not 0057c8b94). Everything went through heavy.sh, one job at a time, with cwd = tree root. Status files: `scratchpad/u54/job1.status` and `scratchpad/u54/h1/status.txt`.

| Gate | Result | Log |
|---|---|---|
| Corpus byte-diff root | 3281 / 3281, **0 MOVED, 0 GONE, 0 APPEARED**, rc 0 | `h1/C-root.txt` |
| pyref | 2185 / 2185, **0 / 0 / 0**, rc 0 | `h1/C-pyref.txt` |
| Mirror sweep | 53 / 53, **0 diff lines** | `h1/D.txt` |
| Fidelity | check-self-annotate-sync rc 0, self-annotate-mirror-check rc 0, doc-coherency rc 0 | `h1/E-*.log` |
| Fast planes (teed) | rc 0, **62 / 62 green** (fast + conversion tier); --slow not run, per the brief | `h1/P-planes.log` |
| check-vacuous-drivers | rc 0 | `h1/I-check-vacuous-drivers.log` |
| check-emitted-vacuity --emit | rc 0 (see note) | `h1/I-check-emitted-vacuity.log` |
| frontend-only-conformance | rc 0 (38 / 38) | `h1/I-frontend-only-conformance.log` |
| core-only-conformance | rc 0, 38 OK / 0 MISMATCH | `h1/I-core-only-conformance.log` |
| count-trusted-directives | rc 0: markers 339, grep-substring **367 (unchanged)** | `h1/I-count-trusted-directives.log` |
| Ledger | `src/pycsl/proof_axiom_allowlist.py` has no diff vs base: **3** | |

Note on check-emitted-vacuity: it reports "2 known erasure(s) NO LONGER erased: remove from KNOWN_ERASURES". The mirror emission is byte-identical to base, so this is pre-existing and not caused by #615.

## Commits (all on run8-u54, none pushed)

COMMITS
