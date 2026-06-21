# Non-vacuity gate false-positive: `any`-Valid over a dead-branch / sibling-contaminated selection

**Status:** FIXED (gate logic). The fix narrows the os "vacuity" set from 15 files
(over-reported) to 6 files with GENUINE vacuity, all in one family.

## How it surfaced

A user asked why `formal_os_close.py::close_makes_fd_unusable` verifies even though `open`
(which RAISES) sits outside the try/except. The mechanical answer: PyCSL auto-infers
`raises { FileNotFoundError, OSError }`, and `ensures { result = 1 }` is a NORMAL-exit
postcondition, so the open/close raise-paths leave via the declared exceptional exit and
carry no `ensures` obligation. But running `--check-vacuity` reported the function VACUOUS —
and 15 of 18 `formal_os_*` files with it.

## Root cause (the GATE, not the proofs)

`_run_vacuity_gate` injected `ensures { false }` into one function, selected goals with
`why3 -g <file>:<line>`, and flagged the function if **ANY** selected record was Valid. Two
defects:

1. **Sibling contamination.** `-g file:line` returns the false-goal AND nearby goals (the
   real `result = 1` postcondition, preconditions). Those are legitimately Valid, so `any`
   fired even when the false-goal itself was Unknown. (`chflags_total_zero`: false-goal
   Unknown standalone, yet flagged.)

2. **Dead-branch conflation (the deep one).** `split_vc` emits ONE `ensures false` goal per
   NORMAL-EXIT path. A consequence test has a provably-DEAD "didn't-happen" branch BY DESIGN
   — e.g. `close_makes_fd_unusable`'s `return 0` is reached only if `fstat` returns normally
   on a closed fd, which `close`'s post-state (`fd_open[fd]=0`) makes impossible. The false
   goal on that dead path proves Valid (witnessing unreachability — sound and expected),
   while the LIVE `return 1` path's false goal is Unknown/Timeout. `any`-Valid flagged the
   whole (sound) function on the dead branch.

A function is vacuous iff EVERY normal exit is inconsistent. The correct criterion is
**ALL** normal-exit false-goals Valid, not ANY.

## The fix (src/pycsl/pycsl.py `_run_vacuity_gate._probe_one`)

- FILTER records to the injected goal only (`loc.start-line == probe_line_no`).
- Best-of-N across provers per path (a path is inconsistent if ANY prover proves its
  false-goal), then require **ALL** false-goals Valid.
- A function with no normal-exit false-goal (only `raises`) is not flagged.

## True vacuity after the fix

Of the 15 files the OLD gate flagged, **9 were false positives** (sound all along):
`close, content, fd, fdchain, listing, lseek, meta, pure, rwsize`.

**6 files have GENUINE vacuity**, all asserting *absence after removal*
(`dir_lookup(...) < 0` post unlink/rmdir/remove):
- `formal_os_dir`        : formal_os_remove, formal_os_rmdir, formal_os_unlink
- `formal_os_enoent`     : open_removed_yields_enoent
- `formal_os_namespace`  : rmdir_then_access_absent, unlink_then_access_absent
- `formal_os_namespace2` : remove_then_access_absent
- `formal_os_query`      : access_absent_after_rmdir
- `formal_os_raises`     : formal_os_stat_absent_raises

Each has a SINGLE normal-exit whose context is inconsistent → real vacuity, localized to the
dir-removal / `dir_lookup`-after-zeroing apparatus (NOT a blanket os problem). This is the
residual hole to investigate next (likely a `dir_lookup` removal axiom interacting with the
//256 dirent packing). The csys case (ROOT-CAUSE.md) should be re-evaluated under the ALL
criterion too — its repro's false postcondition also proved on only one path.

## Verification

- `close`, `formal_os_pure`, `formal_os_roundtrip`, `formal_bank_transfer`, `formal_os_symlink`,
  `formal_os_namecodec` — now PASS the gate (sound).
- `formal_os_namespace` — still correctly FAILS on the two genuinely-vacuous functions while
  passing the 5 sound ones (the gate still catches real vacuity; it is not blinded).
