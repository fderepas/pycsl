# Verification Workflow

Spin is a code generator wrapped around a model checker. The standard flow is: take the `.pml` model, generate a C verifier (`pan.c`), compile it, run it. This page covers the command sequence, the output to expect, the common errors, and the counter-example replay loop.

## The standard four commands

```bash
spin -a model.pml          # generate pan.c from the Promela model
gcc -O2 -o pan pan.c       # compile the verifier
./pan                      # run the verification
spin -t -p model.pml       # if it failed, replay the counter-example
```

That's the entire core workflow. The Spin GUI (`ispin`) wraps these commands; on the command line they are what you'll actually run, and what CI scripts will invoke.

## What `./pan` checks by default

A bare `./pan` invocation checks for three things on every reachable state:

1. **Assertion violations.** Any `assert(P)` that evaluates false.
2. **Invalid end states.** Any state where no process can make progress *and* at least one process is in a non-`end`-labeled state. This is Spin's name for *deadlock*.
3. **Unreached code.** At the end of verification, Spin reports which lines of each `proctype` were never reached. This is a coverage report; lines that should be reachable but aren't usually indicate a guard that's too strict or a transition that's structurally dead.

This default set is what you want for "is there a deadlock?". For liveness and LTL properties, see `properties.md`.

## Reading a successful verification

A run with no errors looks roughly like:

```
(Spin Version 6.5.x ...)
        + Partial Order Reduction

Full statespace search for:
        never claim         - (none specified)
        assertion violations    +
        cycle checks        - (disabled by -DSAFETY)
        invalid end states  +

State-vector 24 byte, depth reached 47, errors: 0
       512 states, stored
       198 states, matched
       710 transitions (= stored+matched)
      ...
unreached in proctype Sender
        (0 of 12 states)
unreached in proctype Receiver
        (0 of 9 states)
```

The lines to read:

- **`errors: 0`** — no property was violated.
- **`states, stored`** — the size of the explored state space. Compare across runs to see whether changes to the model are growing or shrinking the search.
- **`State-vector N byte`** — memory per state. Cutting variables to smaller types (e.g., `byte` instead of `int`) shrinks this.
- **`depth reached`** — the longest execution path explored. If it equals the configured maximum (default 10000), the search was *truncated*; raise it with `./pan -m100000` and re-run.
- **`unreached in proctype X`** — coverage. `0 of N states` means all transitions were explored. Anything else means part of your model is dead — investigate before declaring success.

## Reading a failed verification (deadlock)

```
pan:1: invalid end state (at depth 4)
pan: wrote model.pml.trail

(Spin Version 6.5.x ...)
        + Partial Order Reduction

Full statespace search for:
        never claim         - (none specified)
        assertion violations    +
        cycle checks        - (disabled by -DSAFETY)
        invalid end states  +

State-vector 24 byte, depth reached 4, errors: 1
         5 states, stored
         0 states, matched
         5 transitions (= stored+matched)
```

The lines to read:

- **`invalid end state (at depth 4)`** — Spin found a reachable state where no process can progress and at least one process is not in an `end`-labeled state. This is a deadlock.
- **`pan: wrote model.pml.trail`** — the counter-example trail file. Replay this with `spin -t -p model.pml`.
- **`errors: 1`** — by default Spin stops at the first error. Pass `-c0` to find all errors (much slower).
- **`depth reached: 4`** — the shortest path to the bug is 4 transitions. Short paths are *good news* — they're easier to read in replay.

The depth is also a clue to the *kind* of bug. A deadlock at depth 4 in a model with 3 processes usually means a missing initialization or a guard that's too strict. A deadlock at depth 200 in the same model usually means a circular wait that only manifests after several rounds.

## Replaying a counter-example

```bash
spin -t -p model.pml
```

`-t` follows the trail file, `-p` prints each statement as it's executed. The output is a step-by-step transcript of the path that led to the deadlock or assertion failure:

```
  1:  proc  0 (Sender:1)  model.pml:12  (state 1)    [ready = 1]
  2:  proc  1 (Receiver:1)  model.pml:21  (state 1)  [link ? msg]
  ...
spin: trail ends after 4 steps
#processes: 2
       link = [empty]
       ready = 1
  4:  proc  1 (Receiver:1)  model.pml:21  (state 1)
  4:  proc  0 (Sender:1)  model.pml:14  (state 2)
2 processes created
```

The final block shows the deadlocked state: which line each process is at, and what every variable and channel holds. This is the diagnostic; from here you can usually see directly which transition's guard was too tight or which message wasn't sent.

Additional useful replay flags:

- **`-g`** also prints values of global variables as they change.
- **`-l`** also prints values of local variables as they change.
- **`-s`** marks send operations explicitly.
- **`-r`** marks receive operations explicitly.

For a thorough diagnostic, `spin -t -p -g -l -s -r model.pml` shows nearly everything. Verbose, but unambiguous.

## Diagnostic strategies

When a counter-example is hard to read, the standard moves are:

- **Re-run with a shallower depth limit.** `./pan -m20` forces Spin to find shorter trails. Combined with `-c0` (all errors), this often surfaces the simplest counter-example.
- **Add assertions to narrow the failure.** If the deadlock is happening but you can't tell why, add `assert(invariant)` at points where you expect specific properties to hold. The first assertion to fail tells you where the model's reality diverged from your expectation.
- **Print state with `printf`.** Promela supports `printf`. Adding `printf("MM: in state X, ready=%d\n", ready)` at strategic points makes the trail readable. (Spin ignores `printf` during state exploration; it only fires on replay.)
- **Shrink the model.** If a 5-process model deadlocks and you can't see why, replace 4 of them with stubs that do nothing and see if the bug persists. Then add them back one at a time. The first one whose addition reintroduces the bug is the participant in the bug.

## Common compilation and runtime errors

- **`pan.c:N: error: ...`** — Spin generated invalid C. Usually a typo in the Promela that the Spin parser accepted but the C compiler rejected. Run `spin -c model.pml` (no `-a`) to check the Promela for syntax errors.
- **`spin: error: d_step contains a statement that can block`** — exactly what it says. Find the statement, prove it can't block (and lift the proof into the guard), or move it outside the `d_step`.
- **`pan: out of memory`** — state space exploded. The fixes are: shrink data types, collapse transitions into `d_step` blocks, reduce the number of process instances, or use `-DCOLLAPSE` for state compression. See "scaling" below.
- **`pan: max search depth too small`** — the default `-m` (depth bound) is 10000. For deep models, pass `./pan -m100000` or more.

## Scaling: when the state space is too big

If `./pan` runs out of memory or takes hours, in this order:

1. **Shrink data.** `bit` and `bool` are one bit each; `byte` is 8 bits; `int` is 32. The state vector includes every variable and every channel slot, so smaller types compress the state vector linearly.
2. **More `d_step`.** Every statement folded into a `d_step` is one fewer interleaving point. Most state explosions are model-level, not protocol-level, and disappear after tightening the discipline.
3. **`-DCOLLAPSE`.** Compile `pan` with `-DCOLLAPSE` for component-wise state compression. Often a 4-10x memory saving with no semantic change.
4. **Bitstate hashing.** `-DBITSTATE` (compile flag) uses approximate hashing; doesn't guarantee completeness, but gives you a fast "no error found in the explored subset" check. Useful as a smoke test before full verification.
5. **Reduce process count.** If you have 10 instances of a `proctype`, try 2 first. If a coordination bug needs more than 3 participants to manifest, that's itself a useful finding — and 3 is usually enough.

## Running from a CI pipeline

A typical CI step for a Spin model:

```bash
spin -a model.pml
gcc -O2 -DSAFETY -DCOLLAPSE -o pan pan.c
./pan -m100000 -c1
```

- `-DSAFETY` disables cycle checking (faster for deadlock-only checks).
- `-DCOLLAPSE` enables state compression.
- `-c1` stops after the first error (also faster).

Exit code is non-zero on any error, which makes this CI-friendly out of the box. Capture stdout for the report; on failure, archive the `.trail` file as a build artifact so a developer can replay it locally.
