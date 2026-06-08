# more-proc — parallelizing the reference-test sweep

**Date:** 2026-06-08
**Goal:** cut `bin/run-reference-tests.sh` wall-clock by running independent tests **concurrently**,
without changing which tests pass/fail.
**Status:** plan (no code yet).

---

## 1. Why this is worth doing, and why it's safe

`bin/run-reference-tests.sh` is a **serial** `for py_file in …` loop (line 127): one blocking
`python3 src/pycsl/pycsl.py … "$py_file"` per test. Each invocation is dominated by
`why3 prove -a split_vc -P alt-ergo -P z3 --timelimit 30` — i.e. **prover-bound, up to 30 s per
goal**. With ~600 tests that is the whole runtime; the box has **14 cores** and typically sits near
**~2 load**, so ~12 cores are idle while the sweep crawls one test at a time.

The tests are **embarrassingly parallel**:
- each is its own `pycsl.py` **process** (no shared interpreter state);
- each reads **only** `src/pycsl/**` (read-only during a sweep) and its own `NNNN.py`;
- each writes **only** its own `NNNN.mlw` and `NNNN.proofs/…` (names are test-unique → **no
  output-file collisions**);
- there is **no cross-test ordering dependency** (the summary is order-independent).

So correctness does not depend on running them one at a time. The serial loop is purely a throughput
choice.

## 2. The one real risk: prover-timeout flakiness — and the gate that catches it

`--timelimit 30` bounds prover time per goal. **If that limit is CPU-time, parallelism is safe**
(CPU seconds consumed are unchanged by contention). **If it is wall-clock**, then over-subscribing
cores can starve a prover and turn a goal that needs ~25 s into a >30 s timeout → a **false `[FAIL]`**.
A faster sweep that introduces false failures is worse than useless (ER doctrine: never trade
correctness for speed).

**Therefore the acceptance gate for this work is:** *the parallel run must produce the exact same
PASS/XFAIL/FAIL set as the serial run* on the full corpus. Until that's demonstrated at a chosen
`--jobs`, the parallel mode is not "done." Mitigations if flakiness appears: lower `--jobs`, or raise
`--timelimit`, or pin one prover. (Likely CPU-time-based given Why3 defaults — but **measure, don't
assume**.)

**Update — this risk materialized, and is now mitigated.** A full parallel sweep at the half-cores
default (`--jobs 7`) produced two spurious `[FAIL]`s (`0342`, `0352`, both Rocq-heavy) — *not* from
over-subscribing our own jobs, but because a **second agent was also sweeping at half-cores** →
combined load ≈ all 14 cores → prover starvation. Both passed when run alone. The half-cores budget
assumes the *other* half is free; with two concurrent sweeps it isn't.

**Mitigation shipped — a serial confirmation pass.** After the parallel run, every `[FAIL]`/`[SKIP]`
is re-run **one at a time** (no intra-sweep contention); any that now passes is reported
`[FLAKY→PASS]` and dropped from the failure set, leaving only `[CONFIRMED FAIL]`s. So a load-induced
timeout can never masquerade as a regression — validated: the `0342`/`0352` flakes were recovered and
the sweep reported a clean `601/601`. (Auto-skipped in `--jobs 1`; disable with `PYCSL_NO_RECONFIRM=1`.)
The acceptance gate above is thus met *by construction* even under concurrent-agent load: the confirmed
failure set is what must match serial.

## 3. Approaches (recommend A now, C later)

| | Approach | Pros | Cons |
|---|---|---|---|
| **A** | `xargs -P K` over the file list, each running a worker shell function | minimal change, no new deps, keeps the bash script | bash result-aggregation is fiddly (subshell counters don't propagate → use result files) |
| **B** | GNU `parallel --jobs K` | nice progress/ordering, `--joblog` | adds a dependency not guaranteed present |
| **C** | a Python driver (`multiprocessing.Pool` / `concurrent.futures`) replacing the loop | structured results, per-test wall timeout, progress bar, JSON summary, reusable in CI | a rewrite of the runner |

**Plan: ship A first** (quick, low-risk, immediately useful), keep the serial path as `--jobs 1`;
**then optionally C** as the durable runner if we want richer reporting.

## 4. Design — Approach A (`xargs -P`)

### 4.1 Keep serial (run once, before fan-out)
The pre-gates stay exactly where they are and run **once**:
- `stdlib-coverage.py --check all`
- `doc-coherency.py --check`
- `.venv` activation.

### 4.2 Worker (one test → one result line)
Factor the per-file body (lines 143–164) into a function/subscript `run_one <py_file>` that:
1. extracts `# pycsl-flags:` and `# pycsl-expected: FAIL` (unchanged logic);
2. runs `pycsl.py $extra_flags "$py_file"`;
3. classifies `PASS` / `XFAIL` / `FAIL` / `SKIP` (the exact existing rules);
4. writes **one line** `STATUS<TAB>NNNN` to a per-test file `"$RESULTS_DIR/NNNN"` (atomic: one
   writer per file, no shared append races).

### 4.3 Fan-out
```sh
build file list (respecting --start-at/--stop-at, both suites/subdirs as today)
RESULTS_DIR=$(mktemp -d)
printf '%s\n' "${py_files[@]}" \
  | xargs -P "$JOBS" -I{} bash -c 'run_one "$@"' _ {}
```
(`run_one` exported via `export -f`, or re-exec the script in a `--worker` mode to avoid `export -f`
portability issues — the `--worker <file>` sub-mode is the cleaner, more portable form.)

### 4.4 Aggregate (deterministic, order-independent)
After `xargs` returns, read `$RESULTS_DIR/*`, **sort by test number**, print the per-test lines in
order (so the log reads identically to the serial run), tally `passed/failed`, print the failed list,
`exit 1` if any `FAIL`/`SKIP`. Completion order never affects the summary.

### 4.5 Concurrency constraint: **use exactly half the machine's cores**

**Hard constraint (this revision):** the sweep uses **`JOBS = total_cores / 2`** (integer division,
floored at 1). Half the box is a deliberate courtesy budget — it leaves the other half for the second
agent / interactive work, and it also happens to suit the per-test sizing (each test's `why3` runs
**two provers**, `alt-ergo` + `z3`, so `cores/2` keeps total prover processes ≈ cores).

The core count MUST be obtained with **this exact, cross-platform script** (works on an Ubuntu desktop
*and* a Mac — `nproc` alone is Linux-only), embedded verbatim in `run-reference-tests.sh`:

```bash
#!/usr/bin/env bash
# Print the number of processors (logical CPUs) on Ubuntu/Linux or macOS.
set -euo pipefail

get_cpu_count() {
    case "$(uname -s)" in
        Linux)
            # nproc respects cgroup/affinity limits; fall back if absent
            if command -v nproc >/dev/null 2>&1; then
                nproc
            else
                getconf _NPROCESSORS_ONLN 2>/dev/null || \
                grep -c '^processor' /proc/cpuinfo
            fi
            ;;
        Darwin)
            # logical CPUs (includes Hyper-Threading); use hw.physicalcpu for physical cores
            sysctl -n hw.logicalcpu 2>/dev/null || \
            sysctl -n hw.ncpu
            ;;
        *)
            # last-ditch POSIX fallback
            getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1
            ;;
    esac
}

get_cpu_count
```

Wiring:
```sh
CORES=$(get_cpu_count)
JOBS=$(( CORES / 2 ))
[ "$JOBS" -lt 1 ] && JOBS=1          # floor at 1 (single- or dual-core machines)
JOBS="${PYCSL_JOBS:-${JOBS}}"        # explicit override still allowed
[ -n "${JOBS_FLAG:-}" ] && JOBS="$JOBS_FLAG"   # --jobs K beats the env/default
```
- `--jobs K` / `PYCSL_JOBS` may **override** the half-cores default (e.g. for measurement or to dial
  back under contention), but absent an override the rule is exactly `total_cores / 2`.
- `--jobs 1` reproduces today's exact serial behavior (escape hatch / debugging).
- On the current 14-core box this yields **`JOBS = 7`**.

## 5. Validation plan (the gate)

1. Pick a representative range (e.g. `--start-at 200 --stop-at 350`, which includes the slow
   Rocq-required `0220`-class tests).
2. Run `--jobs 1` → record the sorted PASS/XFAIL/FAIL set + wall time (T1).
3. Run at the **half-cores default** (`JOBS = get_cpu_count()/2`; = `7` on the 14-core box) → record
   the set + wall time (Tk).
4. **Gate:** the two result sets are **identical**. If not, a prover starved → lower K or raise
   `--timelimit`; re-test until identical.
5. Report speedup (T1/Tk). The default stays the constraint `total_cores/2`; only narrow it (or raise
   `--timelimit`) if step 4's gate fails at that level.
6. Only then make parallel the default; document in the script header + `pycsl-how-to-develop`.

## 6. Sizing & interaction notes
- **Two-agent contention (today's actual slowness):** when the stdlib agent is also sweeping, the box
  is already busy — the **half-cores constraint** (`get_cpu_count()/2`) is exactly what keeps the two
  agents from oversubscribing: each takes half. Consider a load-aware cap (skip if `loadavg` already
  high) as a later nicety.
- **Memory:** each `why3`+prover uses memory; at K≈7 this is minor, but watch RSS on large `.mlw`.
- **Don't double-parallelize:** Why3 itself can schedule goals; we parallelize at the **test** level
  and leave each `why3` as-is. Revisit only if a *single* test dominates.

## 7. Out of scope
- Parallelizing within one test (Why3 `-j`/goal scheduling).
- Changing prover selection or timelimits (except as a §2 mitigation).
- The dual-oracle `run_suite.py` runner (same pattern applies; do later if wanted).

## 8. Rollout checklist
- [ ] Factor `run_one` / add `--worker` sub-mode (behaviour byte-identical to current per-file block).
- [ ] Embed the exact `get_cpu_count()` script (Linux + Darwin) verbatim; default
      `JOBS = get_cpu_count()/2` (floor 1); `--jobs`/`PYCSL_JOBS` override; `--jobs 1` == today.
- [ ] Result-file aggregation + sorted summary + correct exit code.
- [ ] **§5 validation gate: parallel result set == serial result set** on a range incl. slow tests.
- [ ] Measure & record speedup; set the default K.
- [ ] Doc: script header + `config/skills/pycsl-how-to-develop`.

> **In one line:** the sweep is a serial loop over independent, prover-bound, file-isolated tests —
> fan it out with `xargs -P`, sized at **exactly half the machine's cores** via the portable
> `get_cpu_count()` script (Ubuntu + Mac), aggregate per-test result files into a sorted summary, and
> gate on *parallel results == serial results* so the speed-up never costs a false failure.
