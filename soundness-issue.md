# Soundness issue: false greens from the best-of-N prover-result merge

**Severity:** High — the verifier reported `Verification SUCCESS` for proofs in
which a real proof obligation was never discharged.
**Status:** FIXED (commit `fa3668d`, branch `os-exception-rootcause`).
**Scope of impact (measured):** 2 previously-green proofs were unsound
(`formal_os_close.py`, `0286.py`); `pycsl os/__init__.py` was vacuously green on
`lseek`. See [Blast radius](#blast-radius).
**Component:** `src/pycsl/pycsl.py` — `_merge_best_of_n` / `_parse_goal_blocks`.

---

## 1. One-paragraph statement

When PyCSL runs more than one SMT prover, it merges their per-goal verdicts into a
single best-of-N result. The merge keyed each Why3 sub-goal by its *header text*.
But `why3 prove -a split_vc` routinely emits **several distinct sub-goals that
share a byte-identical header** — most importantly the *then-branch* and
*else-branch* proof obligations of a single postcondition, which sit at the same
source line and carry the same `Sub-goal Postcondition of goal f'vc.` label.
Because the merge used the header as a dictionary key, those distinct obligations
**collapsed into one entry**, and the merge kept only the *best* verdict among
them. A `Valid` sub-goal therefore **masked** a sibling `Timeout`/`Unknown`/`Invalid`
at the same line. The downstream success test (`not unknown_goals and not
invalid_goals`) then saw a clean sheet and printed `Verification SUCCESS`, even
though a genuine obligation was never proved.

This is a soundness defect: the tool's "green" did not entail "proved".

---

## 2. Background: how PyCSL dispatches and merges provers

`_dispatch_provers` (pycsl.py) runs best-of-N across the configured provers
(default `alt-ergo`, `z3`):

- The first prover runs on the whole file (`why3 prove -a split_vc -P <p> ...`).
- Each subsequent prover re-runs only the still-non-Valid goals
  (`-g <file>:<line>` selectors from `_residual_selectors`).
- The per-prover stdouts are combined by `_merge_best_of_n`, and the *merged*
  string is what the success/failure logic parses:

```python
output, merged_stderr, returncode = _dispatch_provers(base_cmd, provers, "30", mlw_filename)
...
unknown_goals = [l for l in output.splitlines() if "Unknown" in l or "Timeout" in l]
invalid_goals = [l for l in output.splitlines() if "Invalid" in l]
if returncode == 0 and not unknown_goals and not invalid_goals and ("Valid" in output or not output):
    _gate_vacuity_then_succeed("\n[+] Verification SUCCESS! ...")
```

So the integrity of the *merged* output is load-bearing for the SUCCESS verdict.

### How goals are parsed and keyed

`_parse_goal_blocks` splits a Why3 stdout into `(header, result_line)` pairs. The
*header* is every line up to (not including) the `Prover result is:` line:

```
File "<f>", line N, characters X-Y:
Sub-goal Postcondition of goal f'vc.        <-- header (2 lines)
Prover result is: Valid (...)               <-- result_line
```

The original `_merge_best_of_n` used that header string as the merge key.

---

## 3. The bug

`split_vc` decomposes one function's verification condition into many sub-goals —
one per branch / per invariant / per path. **The header does not uniquely identify
a sub-goal.** Two sub-goals collide on the header whenever they share the same
source line *and* the same descriptive label. The canonical case is a postcondition
checked on both arms of an `if`:

```
File "f.mlw", line 119, characters 15-27:
Sub-goal Postcondition of goal getpid_constant'vc.
Prover result is: Timeout (...)      <-- then-branch obligation

File "f.mlw", line 119, characters 15-27:
Sub-goal Postcondition of goal getpid_constant'vc.
Prover result is: Valid (...)        <-- else-branch obligation
```

Both blocks have an identical header. The old merge:

```python
best: Dict[str, str] = {}        # header -> best result line
for out in outputs:
    for header, result_line in _parse_goal_blocks(out):
        r = _verdict_rank(result_line)
        if header not in best:
            best[header] = result_line; ...
        elif r > best_rank[header]:   # Valid (rank↑) overwrites Timeout
            best[header] = result_line; ...
```

The second block (Valid) lands on the **same key** as the first (Timeout) and,
because `Valid` outranks `Timeout`, *overwrites* it. The merged output then
contains a single `Valid` line for that header — the `Timeout` has vanished.
`unknown_goals` is empty ⇒ `Verification SUCCESS`.

The same collapse corrupts the **non-vacuity gate**: `_probe_one` checks whether
any sub-goal proves an injected `ensures { false }`. A statically-dead branch
proves `false` soundly; with the collapse, that Valid result was the only one kept,
so the gate both (a) mis-reported dead-branch functions as "vacuous" and (b) could
not distinguish them from genuinely-masked obligations.

### Why a `Valid` sibling exists to do the masking

The masking needs a `Valid` block at the same header as the unproven one. That is
extremely common:

- **Dead branches.** `if cond: return 1 else: return 0` where a callee's `ensures`
  makes one arm unreachable. The unreachable arm's obligations are *vacuously*
  Valid (its path assumption is contradictory). The reachable arm carries the real
  obligation. Both arms' postconditions share the line ⇒ the vacuous Valid masks a
  hard/failing real obligation.
- **Multi-path postconditions.** Any postcondition proved on several paths where
  one path is easy (Valid) and another is hard (Timeout) at the same line.

---

## 4. Reproduction and proof of the defect

Minimal live witness: `getpid_constant` in `src/pycsl_lib_test/formal_os_query.py`:

```python
#@ ensures \result == 1            # mutate to == 2 for the false twin
def getpid_constant():
    return 1 if getpid() == 1 else 0   # val getpid ensures \result == 1
```

Mutated to the impossible postcondition `\result == 2` (a value the body cannot
return), the verifier still reported success **before** the fix:

```
$ pycsl formal_os_query.py --fun getpid_constant     # ensures \result == 2
Sub-goal Postcondition of goal getpid_constant'vc.
Prover result is: Valid (0.01s, 762 steps)
[+] Verification SUCCESS! All contracts formally proven.       <-- WRONG
```

Running Why3 directly on the *same* module shows the truth — two postcondition
sub-goals at the same line, one of which never proves:

```
$ why3 prove -a split_vc -P z3 -t 30 <module>
Sub-goal Postcondition of goal getpid_constant'vc.  Timeout (30.00s, 25,638,167 steps)  <-- then-branch (live)
Sub-goal Postcondition of goal getpid_constant'vc.  Valid   (0.01s, 762 steps)          <-- else-branch (dead)
```

The merge dropped the `Timeout` and kept the `Valid 762`, yielding the false green.

**Independent confirmation that this is a merge artifact, not real inconsistency:**
an `ensures { false }` probe that touches the module's global state times out at
**120 s on both alt-ergo and z3** (no solver derives `false`). The assumed context
is *consistent*; the green came purely from the collapse.

---

## 5. The fix

Key the merge by **`(header, occurrence-index-within-one-prover-output)`** instead
of by header alone. `split_vc` is deterministic and emits sub-goals in a stable
document order for a given `.mlw`, so the *k-th* occurrence of a given header
denotes the *same* sub-goal across every prover's output. Aligning by occurrence
merges each sub-goal with its true counterpart:

```python
order: List[Tuple[str, int]] = []
best: Dict[Tuple[str, int], str] = {}
best_rank: Dict[Tuple[str, int], int] = {}
for out in outputs:
    occ: Dict[str, int] = {}                 # header -> count seen in THIS output
    for header, result_line in _parse_goal_blocks(out):
        n = occ.get(header, 0); occ[header] = n + 1
        key = (header, n)
        r = _verdict_rank(result_line)
        if key not in best:
            order.append(key); best[key] = result_line; best_rank[key] = r
        elif r > best_rank[key]:
            best[key] = result_line; best_rank[key] = r
parts = []
for key in order:
    header = key[0]
    parts.append((header + "\n" + best[key]) if header else best[key])
return "\n\n".join(parts)
```

### Why the fix is correct

- **Occurrence alignment is sound across provers.** Two sub-goals collide on a
  header iff they share `File "...", line N` (the header *includes* that line).
  `-g file:line` selects *all* sub-goals at that line, so a residual re-run emits
  the colliding siblings together, in the same `split_vc` order. Hence the k-th
  occurrence in prover A's output corresponds to the k-th in prover B's. Best-of-N
  is then taken per real sub-goal.
- **No regression for unique goals.** A header that occurs once keeps occurrence
  index 0 — identical behaviour to the old code. Only genuinely-colliding headers
  change.
- **Masking is eliminated.** A `Timeout` sub-goal now occupies its own
  `(header, k)` slot; a `Valid` sibling at `(header, k')` (k'≠k) can no longer
  overwrite it, so it survives into the merged output and is counted by
  `unknown_goals` ⇒ the run correctly FAILS.

### Verification of the fix

| Check | Before fix | After fix |
|---|---|---|
| `getpid_constant`, real `\result == 1` | SUCCESS | **SUCCESS** (no false failure) |
| `getpid_constant`, false twin `\result == 2` | SUCCESS (wrong) | **FAILED** (then-branch surfaces) |
| `formal_os_close.py` (full proof) | SUCCESS (wrong) | **FAILED** then FIXED — see §6 |

---

## 6. Blast radius

Measured by running each test with the same harness **with** and **without** the
fix and diffing (the fix can only turn a result green→red, never the reverse, so a
baseline diff isolates exactly the exposed false-greens).

- **Formal suite (`src/pycsl_lib_test/formal_*.py`, 121 files): 120 still PASS.**
  The single newly-red test is `formal_os_close.py` — a genuine false-green: its
  post-close `fstat` had to *raise* for the test's postcondition to hold, but the
  `fstat` contract permitted a normal return on a closed fd, so the obligation was
  never real-proved. Fixed in commit `4a2728d` by adding a body-proven EBADF
  normal-return ensures (`fd < 64 ==> _filesystem.fd_open[fd] != 0`), backed by the
  kernel `sys_fstat` post-state (zero trust). `formal_os_close` now proves with
  full proof.

- **Reference corpus (`test-suite/corpus/pycsl-reference/`, 670 files):** exactly
  **one** test, `0286.py` (quicksort sortedness — a genuinely hard recursive SMT
  goal), was a masked false-green. It carries `# pycsl-flags: --no-proof`, so its
  canonical CI invocation only typechecks; **CI is unaffected**. Every other
  non-passing corpus file fails on the baseline too (Rocq-backed proofs my bare
  `pycsl <file>` harness does not replay, or pre-existing on this branch).

- **os module itself (`pycsl os/__init__.py`):** now honestly **red on `lseek`
  only** — the known-remaining genuine vacuity case, previously masked. Separate
  follow-up.

The narrow blast radius is expected: the collapse only changes a verdict when an
unproven obligation happened to share a source line with a Valid one. Most proofs
either have no colliding headers or have all-Valid siblings (where masking is a
no-op).

---

## 6b. Defense-in-depth landed

Three layers now guard this class, in increasing fundamentality:

- **Tier 0 — fail-closed conservation (trust-free).** `_check_goal_conservation`
  rejects any merge that yields fewer goals than the first full-file run, raising
  `_MergeConservationError` (loud `SOUNDNESS ABORT`, never a silent green). Survives
  any future rewrite of the merge. Unit-tested.
- **Tier 1 — false-twin mutation harness.** `bin/false-twin.py` flips a proven
  `\result == N` to `== N+1` and asserts the proof now FAILS; a surviving mutant is
  a false-green by any mechanism. Self-test = the `getpid_constant` witness.
- **Tier 2 / #6 — structured `--json` (root cause).** Identity, merge and verdict
  now run over `why3 prove --json` records (one per sub-goal) instead of re-grepping
  human stdout; canonical legacy text is synthesised from the merged records so the
  rest of the pipeline is unchanged. Two same-loc sub-goals are distinct list
  elements, so the masking collapse is impossible by construction. Landed behind
  Tiers 0/1, as the lesson below dictates.

## 7. Lessons / follow-ups

1. **A parser/merge keyed on non-unique identifiers is a soundness risk.** The
   header was treated as a primary key; it is not one. Any future merge/dedup over
   Why3 goals must preserve per-sub-goal identity (occurrence, or a Why3-emitted
   unique goal id if available).

2. **The earlier "nonlinear integer-division vacuity" diagnosis was wrong for the
   os/csys cases.** The gate's stock explanation pointed at nonlinear div; the real
   cause was this merge collapse plus dead-branch over-flagging. The gate's
   advisory text should be revisited.

3. **Open (precision, not soundness): the non-vacuity gate over-flags dead
   branches.** `_probe_one` treats "any sub-goal proves `ensures false`" as
   vacuous, but a statically-dead branch proves `false` soundly. It should judge
   vacuity on the function's reachable/entry context, not per dead branch.

4. **Regression guard worth adding:** a test that asserts an impossible
   postcondition on a function with a dead branch (the `getpid_constant \result==2`
   shape) must FAIL — this is the direct regression witness for this bug.
