# Typecheck audit — the honest-gate backlog (refactor.md Phase D)

**What this records.** Phase D's principle: *a run is SUCCESS only if the emitted WhyML at least
type-checks* — emitting text that does not even type-check is the silent success the laws forbid
(`refactor.md` §1.5). The `--typecheck` gate (`pycsl … --no-proof --typecheck`) makes this checkable: it
runs `why3 prove --type-only` on the emitted `.mlw` and reports a per-level status `L1 ✓ L2 ✓ L3-tc {✓|✗}`,
exiting non-zero on `L3-tc ✗`.

**The finding (snapshot).** Of the **588** reference drivers that emit WhyML and report `--no-proof`
SUCCESS, **54 emit WhyML that does NOT type-check** — i.e. they have been reporting a *dishonest* SUCCESS.
The failure is real, not a harness artifact: the production `why3 prove -a split_vc -P <prover>` path fails
the same drivers with the same diagnostic (verified on `0250`: `unbound function or predicate symbol
'counter'`), and none of the 54 are marked `# pycsl-expected: FAIL`.

Regenerate the list at any time with `bin/typecheck-audit.sh`.

## The 54, by category

- **Concurrency (28):** drivers using `#@ critical`/`acquires`/`releases`/`shared`/`thread_entry`/
  `mutex_invariant`/`lock_order`. **ROOT CAUSE (diagnosed):** the mutex-invariant lowering emits a *logic*
  `predicate` whose body dereferences a *program* mutable ref — which WhyML forbids (logic cannot see
  mutable program state). For `0250`: shared state is `val counter : ref int`
  (`module6_whyml/preamble.py:610`), but the invariant is `predicate lock_counter_inv = (!counter >= 0)`
  (`preamble.py:623`) → `why3` reports `unbound function or predicate symbol 'counter'` at the predicate
  line. **FIX (D1, one root cause covers ~all 28):** parameterize the predicate by the shared values —
  `predicate {mutex}_inv ({var}: int …) = {bare invariant}` — and apply it with the dereference at every
  program-context use site: `_check_initial` (`preamble.py:633`) and the critical-section assume/prove
  (`module6_whyml/statements.py:534-535`), i.e. `assert { {mutex}_inv !{var} }`. This CHANGES the
  concurrency `.mlw` (so it is byte-diff-visible and gated by: the fixed `.mlw` type-checks **and** the
  corpus pass/fail is otherwise unchanged), unlike the rest of this refactor's byte-preserving bricks.
- **Other (26):** `0050 0303 0386 0406 0407 0477 0478 0479 0480 0482 0483 0484 0485 0486 0487 0488 0489
  0557 0560 0563 0575 0601 0631 0634 0636 0638` — assorted features whose lowering emits an
  ill-typed/undeclared symbol. Each needs its own diagnosis.

## Why the gate is opt-in (not yet default-on)

Flipping `--typecheck` to a default, *enforced* gate today would flip these 54 from PASS to FAIL — a large
baseline regression. So the gate ships **opt-in** (the capability + the honest per-level status), and the
default `--no-proof` SUCCESS message is unchanged (no regression, fast dev sweeps preserved). The staged
path to honest-by-default:

1. **D0 (done):** the `--typecheck` capability + per-level status + this audit. ← *here*
2. **D1:** fix the 54 (start with the concurrency emission gap — one root cause covers ~28) or mark the
   genuinely-unsupported ones `# pycsl-expected: FAIL`.
3. **D2:** make the typecheck run by default and gate SUCCESS on it — the spec's end state.

Until D2, treat a plain `--no-proof` SUCCESS as "WhyML emitted", and `--no-proof --typecheck` SUCCESS as
"WhyML emitted **and** type-checks".
