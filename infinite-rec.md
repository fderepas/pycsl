# What happened: the `cmmi-audit.sh` ↔ supervisor infinite recursion

**Date:** 2026-06-01
**Symptom:** CPU load exploded — runaway process fan-out, not a hang.
**Trigger:** Gap 9 of the ER ("Extreme Rigor") retrospective —
*"wire `bin/er-retrospective-check.sh` into `cmmi-audit.sh`"*.

---

## The one-line cause

I added an `[ER]` step to `cmmi-audit.sh` that runs the *retrospective
check*. But the retrospective check runs the *supervisor*, and the
supervisor runs `cmmi-audit.sh` as one of its gate steps. So
`cmmi-audit` called something that called `cmmi-audit` — a cycle with
no base case.

---

## The exact call chain

```
cmmi-audit.sh                       (you, or CI, run this)
  └─ [ER] step  ─────────────────►  bin/er-retrospective-check.sh
                                       │  (proves the ER mechanism is
                                       │   "load-bearing": mutate a plan,
                                       │   assert the supervisor halts,
                                       │   revert, assert it passes again)
                                       │
                                       ├─ run #1 baseline:  bin/agent-feature-supervisor --feature-file <plan> --skip-gate
                                       ├─ run #2 mutated:   bin/agent-feature-supervisor --feature-file <plan> --skip-gate
                                       └─ run #3 reverted:  bin/agent-feature-supervisor --feature-file <plan> --skip-gate
                                                               │
                                                               │  each run EVALUATES the plan's acceptance claims
                                                               │  (agent-feature-supervisor.py:1134 — runs even under
                                                               │   --skip-gate; only the gate at :1201 is skipped).
                                                               │  missing-bytes-struct-feature.md's `**Acceptance:**`
                                                               │  blocks contain literal commands like:
                                                               │     `bin/cmmi-audit.sh --quick 2>&1 | grep -c …`
                                                               │
                                                               └─ acceptance claim shells out ──► bin/cmmi-audit.sh --quick
                                                                                                    │
                                                                                                    └─ [ER] step ──► bin/er-retrospective-check.sh
                                                                                                                        └─ supervisor ×3 ──► cmmi-audit ──► …
```

The arrow closes the loop: **`cmmi-audit` → retrospective → supervisor →
(acceptance claim) → `cmmi-audit`**, forever.

### Why `--skip-gate` does NOT save you

The retrospective always calls the supervisor with `--skip-gate`, so my
first instinct — "the supervisor's *gate step* re-runs cmmi-audit" — was
the wrong back-edge. `--skip-gate` skips the gate
(`agent-feature-supervisor.py:1201`), but it does **not** skip
**acceptance evaluation** (`:1134`), which is the supervisor's whole
reason to exist. And the ER plans' `**Acceptance:**` blocks are written
to call `bin/cmmi-audit.sh --quick` directly (that's how a phase proves,
e.g., `grep -c "[VERIFIED]" >= 2`). So the loop closes through the
**acceptance claims**, not the gate — which is exactly why it fired even
though every supervisor call in the retrospective passes `--skip-gate`.

(The gate step at `:570/:1201` is a *second*, independent back-edge that
would also recurse in full non-`--skip-gate` mode. The guard below closes
both.)

---

## Why it was an *explosion*, not a slow infinite loop

A plain infinite recursion grows linearly (depth N uses N stack frames).
This one **fanned out multiplicatively**, which is why the machine fell
over so fast:

1. **Branching factor ≥ 3 (really 3 × N).** Each `cmmi-audit` run
   triggers *one* retrospective, but the retrospective runs the
   supervisor **three times** (baseline / mutated / reverted), and each
   supervisor run evaluates **every** cmmi-audit-invoking acceptance line
   in the plan (`missing-bytes-struct-feature.md` has several). So one
   level spawns 3 × N child `cmmi-audit` processes, each of which spawns
   3 × N more: the count multiplies every level — 1 → 3N → (3N)² → … —
   exponential.

2. **Each node is heavyweight.** A supervisor invocation isn't cheap: it
   shells out to the full gate (cmmi-audit, doc-coherency, and — in deep
   mode — `run-reference-tests.sh`, which alone can run for minutes). So
   the tree wasn't just wide, every node was burning real CPU.

3. **Concurrent, not sequential.** Several of these ran as backgrounded
   `bash` subprocesses, so the layers piled up in parallel rather than
   waiting on each other. The scheduler saw an ever-growing population of
   CPU-bound Python + shell processes → load average spiked.

That combination — exponential fan-out × expensive-per-node × parallel —
is what saturated the CPU before any depth limit or OOM kill could
intervene.

---

## The fix (already applied)

A re-entrancy guard via an environment variable, in
`bin/cmmi-audit.sh` (lines ~300-331):

```sh
if [[ -n "${CMMI_AUDIT_NESTED:-}" ]]; then
    skip "ER retrospective informational" "nested cmmi-audit invocation"
elif [[ -x "$REPO_ROOT/bin/er-retrospective-check.sh" ]]; then
    echo "[ER] er-retrospective-check.sh — load-bearing mechanism proof"
    export CMMI_AUDIT_NESTED=1          # <── any cmmi-audit spawned below sees this
    "$REPO_ROOT/bin/er-retrospective-check.sh" …
    unset CMMI_AUDIT_NESTED
fi
```

How it breaks the cycle:

- The **top-level** `cmmi-audit` sees `CMMI_AUDIT_NESTED` unset → runs the
  `[ER]` step, and **exports `CMMI_AUDIT_NESTED=1`** before doing so.
- Every `cmmi-audit` reached *underneath* it (retrospective → supervisor →
  cmmi-audit) inherits `CMMI_AUDIT_NESTED=1` → **skips** the `[ER]` step.

So the recursion is bounded to **depth 1**: the ER step runs exactly once,
at the outermost invocation, and never re-enters itself. The supervisor's
own `cmmi-audit --quick` gate still runs in full — it just no longer
re-triggers the retrospective.

---

## Status / what still needs checking

- The guard edit **is in the tree** (`bin/cmmi-audit.sh`).
- It was **never verified end-to-end** — the verification run is the tool
  call that was interrupted when the CPU spiked. Before trusting it, run
  (single-threaded, with a timeout, watching load):

  ```sh
  CMMI_AUDIT_NESTED=1 timeout 180 bin/er-retrospective-check.sh   # should NOT recurse
  bin/cmmi-audit.sh --quick                                       # [ER] runs once, then skips when nested
  ```

  Run these deliberately, not in the background, so a regression spikes
  one core for one run instead of forking a tree.

## Safer-design note (optional follow-up)

The env-var guard is the minimal fix. A more robust design would be to
**not call the supervisor from inside an audit step at all** — the
audit's job is to inspect the tree, and proving the supervisor halts on a
mutation is a different, heavier concern that belongs in CI or a
dedicated `make er-check` target (gap 8), invoked separately from the
fast `cmmi-audit` path. Coupling a cheap inspection to an expensive
mutate-and-prove cycle is the underlying smell; the guard treats the
symptom.
