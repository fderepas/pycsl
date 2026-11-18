# Run #8 executor lvW report: typed tuple-return exception + `_why3_typecheck` conversion (BATCH A)

Executor lvW. Tree `/home/fabrice/git/pycsl-lvW`, branch `run8-lvW`, base `0057c8b94` (`\trusted` 367, ledger 3).
Spec: the run7-sp5 spike `getting-better/run8-spike-typed-tuple-return.md` (VERDICT GO). Commits only, never pushed.
- Every heavy job went through `scratchpad/heavy/heavy.sh`, with cwd = tree root and `source scratchpad/g29/env.sh`.
- Every `--fun` ran with `PYTHON_CPU_COUNT=4`, and only one `--fun` of mine ran at a time.
- oom_kill was 0 at every START and END I recorded. The slice was reset by the 12:14Z reboot.
- No job of mine returned rc 137.

## 0. Commits

| commit | what |
|---|---|
| `b65e75bfc` | **SRC-FINAL** (written to progress.txt 12:59Z): the spike src ported onto 0057c8b94, plus the de-trusted row in `getting-better/trusted-reasons.tsv` |
| `f1406a4c3` | corpus witnesses 10150-10159 |
| `badcb9b5a` | WIP: evidence (sweeps, compares, leaf-reachability) |
| `50b977429` | witnesses rewritten without trivially-true clauses (for claim-vacuity); wrap `--fun`; slow planes |
| (this commit) | report + remaining evidence |

Notes on SRC-FINAL:
- The port is `git diff 06cb88013 run7-sp5 -- src/`, applied with `git apply`. There were no conflicts: since
  06cb88013 the base changed only `src/pycsl/frontend/ir_resolve.py`.
- The `trusted-reasons.tsv` edit is the honest sync for a removed marker. `check-trusted-reasons` was RED without
  it (rc 1, "DELETE these rows"); after it, rc 0 with 338 markers <-> 338 rows.
- There was **no SRC-CHANGED**. No gate forced a src edit after SRC-FINAL.

## 1. Source change (the sp5 spike, verbatim)

- **Raise arm:** `src/pycsl/module6_whyml/stmt_control_flow.py::_handle_return_stmt`. Its mirror twin is
  VERIFIED, so the same body sits verbatim and inline in `src/self-annotate/src/module6_whyml/stmt_control_flow.py`.
- **Catch arm:** `src/pycsl/module6_whyml/statements.py::_wrap_body_with_return_catch`. Its twin is VERIFIED;
  verbatim and inline in the mirror.
- **needs / decl:** `src/pycsl/module6_whyml/preamble.py::_scan_preamble_needs` and `_emit_preamble_exceptions`.
  Both twins are `\trusted`, so the mirror is untouched and its emission does not move.
- **`_why3_typecheck`:**
  - [T] the signature becomes `-> Tuple[bool, str]`.
  - [R] `_diag` gets an explicit stdout fallback in place of `or`.
  - Live `src/pycsl/pycsl.py` and mirror `src/self-annotate/src/pycsl.py` are verbatim.
  - The mirror's `#@ \trusted reviewer: pycsl-self-annotate` line is removed. The contract is unchanged
    (`requires True / ensures True / assigns \nothing`).
- No helper was extracted, no new `\trusted`, no axiom, no contract weakened.
- L3-tc of the 3 changed mirror files (`--no-proof --keep-mlw`): all `L1 ✓ L2 ✓ L3-tc ✓`
  (`scratchpad/lvW/proofs/tc_*.log`).

## 2. Gates

### Mirror sweep vs `scratchpad/run8/base8/mir` (rule 32: base is 0057c8b94, `done.txt` present)

`heavy.sh bin/mirror-emit-sweep.sh scratchpad/lvW/mir`, then `byte-diff-compare.py <base8>/mir scratchpad/lvW/mir --min-files 45`.

- Result: **53 / 53; 3 MOVED, 0 GONE, 0 APPEARED**.
- The 3 movers are exactly the expected ones: `module6_whyml__statements`, `module6_whyml__stmt_control_flow`,
  `pycsl`.
- With `--expect-moved` naming those three, the compare returns rc 0.
- Logs: `scratchpad/lvW/mir-cmp.txt`, `mir-cmp-expected.txt`, `mirdiff-*.txt`.

Line counts of the diffs: statements 63, stmt_control_flow 157, pycsl 48.

Inside `pycsl.mlw`:
- `exception Return_tup_int_string (int, string)` is added, and `val _why3_typecheck` becomes a `let` body that
  raises and catches it.
- Three callers of `_why3_typecheck` gain a `raises { ...OS family... }` clause. This is honest: the converted body
  exposes `ext_subprocess_run_op`'s open-world raises, which the `\trusted` val hid.

### Corpus byte-diff vs `scratchpad/run8/base8/bd`

`heavy.sh bin/byte-diff-sweep.sh scratchpad/lvW/bd` (NORMAL, cwd = root). The comparator ran once per tree, and the
file counts were asserted:
- **root: 3275 baseline / 3285 candidate; 0 MOVED, 0 GONE, 0 APPEARED; 10 new source files ignored** (my
  10150-10159). Log `scratchpad/lvW/C-root.txt`.
- **pyref: 2185 / 2185; 0 MOVED, 0 GONE, 0 APPEARED** (`--min-files 2000`). Log `scratchpad/lvW/C-pyref.txt`.
- The sweep log is `scratchpad/lvW/bd.log`: it emitted 3286 of 6232 sources and 2185 of 2217 pyref.

### `--fun` proofs (PYTHON_CPU_COUNT=4, one at a time; `scratchpad/lvW/prove.sh`)

| target | result | handler goals | wall incl. queue | oom |
|---|---|---:|---:|---|
| statements `statementemissionmixin___wrap_body_with_return_catch` | **1088 / 1088 Valid**, SUCCESS | 963 | 18677 s | 0->0 |
| stmt_control_flow `controlflowstmtmixin___handle_return_stmt` | **3534 / 3534 Valid**, SUCCESS | 3288 | 5897 s | 0->0 |
| pycsl `_why3_typecheck` (converted) | **761 / 761 Valid**, SUCCESS | 8 | 16070 s | 0->0 |

- The goal counts are identical to sp5's (1088 / 3534 / 761).
- The walls are dominated by heavy-queue waits: slot 1 held the driver's statements whole-file proof all night.
- Logs: `scratchpad/lvW/proofs/fun_*.log`; START / END lines are in `scratchpad/lvW/proofs/summary.txt`.

### Whole-file `pycsl.py` mirror proof (HEAVY_LOW=1, PYTHON_CPU_COUNT=6)

__WHOLE__

### Mutation test + leaf-reachability on `_why3_typecheck`

Both ran on a separate detached snapshot tree, `/home/fabrice/git/pycsl-lvW-mut` at f1406a4c3, which has the same
src as SRC-FINAL. My tree was never edited for them.

**Leaf-reachability** (patch `scratchpad/lvW/leafassert.patch`):
- An `#@ assert 1 == 2` sits at the head of each of the 3 innermost terminal blocks: the `except FileNotFoundError`
  body, the `if r.returncode == 0` body, and the `if not _diag` body.
- These three are mutually exclusive paths, so no assert masks another. The try body is upstream of all three, so
  its reachability is implied.
- Result: **3 / 3 NOT proved**. Each is Timeout under every prover; the run is FAILED at 761 / 767 (6 non-Valid
  lines = 3 goals x 2 provers). oom 0->0. Log `proofs/fun_why3tc_leafassert.log`.

**Mutation** (patch `scratchpad/lvW/leafmut.patch`):
- The leaf ensures `\result[0] == True ==> \result[1] == ""` is **Valid on all 4 return paths**.
- The mutant ensures `\result[0] == True` is **refused on the 3 `False` paths** (Timeout, Timeout, and Unknown
  "Out of memory"). It is Valid only on the `rc == 0` path.
- The run is FAILED at 762 / 768, as a mutant must be. oom 0->0. Log `proofs/fun_why3tc_leafmut.log`.

### Corpus witnesses (IDs 10150-10159 only)

These are sp5's t1-t5 ported, plus 5 red-team witnesses. Logs: `scratchpad/lvW/wit-head/wit.log` and
`scratchpad/lvW/wit-base/wit.log`, the final versions after the claim-vacuity fix.

| file | expected | head (b65e75bfc src) | base 0057c8b94 |
|---|---|---|---|
| 10150_typed_tup_bool_str_early_return | PASS | PASS 9/9 | FAIL (L3-tc) |
| 10151_typed_tup_bool_str_leaf_claim | PASS | PASS 2/2 | FAIL |
| 10152_typed_tup_bool_str_leaf_mut | FAIL | FAIL 1/3 | FAIL |
| 10153_typed_tup_mixed_codomains | PASS | PASS 11/11 | FAIL |
| 10154_typed_tup_loop_return_mut | FAIL | FAIL 4/6 | FAIL 4/6 |
| 10155_typed_tup_shared_codomain | PASS | PASS 6/6 | FAIL |
| 10156_typed_tup_shared_codomain_mut | FAIL | FAIL 5/7 | FAIL |
| 10157_typed_tup_recursion | PASS | PASS 4/4 | FAIL |
| 10158_typed_tup_recursion_mut | FAIL | FAIL 3/5 | FAIL |
| 10159_typed_tup_nested_function | PASS | PASS 4/4 | FAIL |

- All 10 run under CPython (`ulimit -v 2000000`, `python3 -I`); every mutant's false claim is visible in its
  printout.
- 10154 is all-int, `(bool, int)`, so it takes `Return_2` at both commits. That is the same FAIL for the same
  reason.

### Planes

**Fast planes:**
- `heavy.sh bash bin/run-soundness-planes.sh` on the final witness set: **62 / 62 green, rc 0**
  (`scratchpad/lvW/planes-fast-2.log`).
- The first run, before the trusted-reasons sync, was 61 / 62, with `check-trusted-reasons` RED
  (`planes-fast-1.log`). The sync fixed it.
- Planes in that set: count-trusted-directives, check-self-annotate-mirror-sync, self-annotate-mirror-check.sh,
  check-sibling-concrete-fidelity, check-mirror-coverage, check-vacuous-drivers, check-claim-vacuity,
  core-only-conformance, frontend-only-conformance. All `ok`.

**Individually** (`scratchpad/lvW/slowplanes.sh`):
- Emit dir: `scratchpad/lvW/planes/emit_dir`, a single-underscore emission of 53 files.
- Full output is in `scratchpad/lvW/planes/*.log`.
- The rc column of that run's `summary.txt` is wrong: a `$(date)` substitution clobbered `$?`. That bug is fixed in
  the script now, and the verdicts below are read from each log's final `[+]` / `[!]` line.

| plane | verdict |
|---|---|
| check-assigns-writes-survival | `[+] OK` — HOLE 0, HOLE-NOWRITES 8 (ceiling 8), TRAP 1398 (ratchet 1399), TRAP-NMS 1501 |
| check-trusted-frame-honesty | `[+] OK` — trusted 0/1, converted 0/63 |
| check-getattr-erasure | `[+] OK` — DECLARED 0 |
| check-mirror-coverage | `[+] OK` — 549 / 41 (ratchets 549 / 41) |
| check-vacuous-drivers | `[+] OK` |
| check-claim-vacuity | first run **NOT OK**, caused by my witnesses: claim-vacuous files 1792 > 1791 (10150's two `ensures True`) and `requires True` files 1138 > 1131. **Fixed in the witnesses**, not in the gate (commit 50b977429): the `requires True` lines are dropped and 10150's claims are now real. Green in the fast rerun |

**Fidelity** (`scratchpad/lvW/fidelity.log`): check-self-annotate-sync.sh, self-annotate-mirror-check.sh and
doc-coherency --check. __FID__

### Ledger and `\trusted`

- **Proof-axiom ledger: 3**, unchanged. `src/pycsl/proof_axiom_allowlist.py` has no diff vs 0057c8b94.
- **`\trusted`: 366** (grep-substring 367 -> 366). `bin/count-trusted-directives.py` reports markers 338,
  attached 338, unattached 0, OK. The pycsl.py mirror goes from 21 to 20 hits.

## 3. Red-team self-check

Probes: `scratchpad/lvW/rt/rt/*.py`. Results are under `scratchpad/lvW/rt/rt-{head,head2,head3,head6,base,base6}/wit.log`,
with the emitted `.mlw` beside each.

### (a) Non-scalar tuple codomain: never silently mis-typed

| probe | slot type | head | base |
|---|---|---|---|
| `r1c_list` | `Tuple[List[int], str]` | old path (`Return_2`), byte-identical to base; L3-tc REFUSED | same |
| `r1_nested` | `Tuple[Tuple[int,int], str]` | new path; L3-tc REFUSED | L3-tc REFUSED |
| `r1b_record` | `Tuple[P, str]` | new path; L3-tc REFUSED | L3-tc REFUSED |

Why `r1_nested` and `r1b_record` take the new path:
- The PRE-EXISTING signature lowering already gives these functions the codomain `let f ... : (int, string)`. The
  nested pair, or the record, collapses to `int`.
- The gate keys on that lowered codomain, so they get `Return_tup_int_string`.
- The raised payload `((1, 2), "pos")` / `({a=1}, "pos")` then fails L3-tc, exactly as `Return_2` did at base.
- Both are fail-closed at both commits.

`r6` (`Tuple[Any, str]`, early returns) PASSES at head, and its claim `\result[1] == "a"` is true:
- `Any` lowers to `int` in the existing value model.
- At base, the SAME function with a single tail return (`r6b`) already PASSES with the same `(int, string)`
  codomain.
- So the typed exception extends the existing tail-return typing to early returns. It adds no new unsoundness.

`r6c` (`Tuple[float, str]`) gets `Return_tup_real_string`, and PASSES with a true claim.

### (b) try/finally + early typed return

`r2_tryfinally` and its mutant are **REFUSED at both commits** by ROUTE #156's fail-closed check. The message is "a
`try ... finally:` ... has no handlers and its body jumps out". A first variant hit route #319's
parameter-rebinding refusal instead. No unsound path either way.

### (c) Generator and nested function

- **Generator** (`r3b_generator`, `Iterator[Tuple[bool, str]]`): it never takes the typed path. It emits
  `Return_void`, byte-identical to base, and the proof FAILS (0/2 at both commits).
- **Nested function returning a typed tuple:** PASS at head (witness 10159, `r3d`). Its mutant `r3dm` FAILS 4/6;
  base FAILS both.
- Two other nested probes are refused by pre-existing limits, not by this change:
  - `r3_nested_fn` and `r5_rec` unpack the tuple (`ok, msg = inner(x)`), and tuple-unpack declares the str slot as
    `ref 0`.
  - `r3c` compares a string inside `and`, which lowers to a hashed-int literal.
  - Both are L3-tc failures, so they are fail-closed.

### (d) Two functions with the same codomain share one exception

Witnesses 10155 and 10156 (`r4`): `f` and `h` are `(bool, str)` and `g` is `(int, str)`.
- They share one declaration, `exception Return_tup_int_string (int, string)`.
- Each function catches it locally (`try ... with Return_tup_int_string r -> r end`), so the payloads do not leak.
- 10155 PASSES 6/6; the 10156 mutant FAILS 5/7.

### (e) Recursion

Witnesses 10157 and 10158 (`r5b`): the base case is an early typed raise, and the inductive step reads the
recursive call's typed result.
- 10157 PASSES 4/4; the 10158 mutant FAILS 3/5.
- The emitted catch binder `r` shadows the function name `r` only inside the handler, which is harmless.

## 4. Not run, or caveats

- I did not run the whole-file statements.py, stmt_control_flow.py or expressions.py proofs (rule 10). The driver
  runs them on a snapshot of b65e75bfc.
- The witnesses were edited after the corpus sweep: the claim-vacuity fix touched only the comment/contract lines of
  the 10 NEW files. They are "new source files" to the comparator, so the 0/0/0 result is unaffected. Their
  head/base verdicts were re-proved after the edit.
- Extra worktrees, all detached at my commits: `/home/fabrice/git/pycsl-lvW-base` (0057c8b94, used for base probe
  verdicts) and `/home/fabrice/git/pycsl-lvW-mut` (f1406a4c3, used for the mutation/leaf runs, restored clean).
  The driver may remove them.
