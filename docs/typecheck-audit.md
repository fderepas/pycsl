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
  **STATUS — predicate fix LANDED:** the `unbound symbol` error is gone on all concurrency drivers; **7 now
  fully type-check** (`L3-tc ✓`), non-concurrency `.mlw` byte-identical, no pipeline regression. The fix
  peeled the onion: a SECOND layered blocker (25 drivers) — the source `#@ \diverges` on the worker
  (modelling lock-blocking as possible non-termination) lowers to a `diverges` effect (`functions.py:286`),
  but the critical section is modelled as non-blocking (havoc+assume), so why3 sees a terminating body and
  rejects it (*"this expression does not diverge"*). That is a **modelling decision, not a turnkey emission
  fix** (model lock-acquire as diverging, or revisit the `\diverges` annotation); the 7 that pass are exactly
  the concurrency drivers WITHOUT `#@ \diverges`. (Plus 0417: a separate unit-vs-int return-type mismatch.)
- **Other (26):** `0050 0303 0386 0406 0407 0477 0478 0479 0480 0482 0483 0484 0485 0486 0487 0488 0489
  0557 0560 0563 0575 0601 0631 0634 0636 0638` — assorted features whose lowering emits an
  ill-typed/undeclared symbol. **D1 diagnosis (2026-06) groups these:**
  - **Logic-context abstract op declared as program `val` (4) — FIXED:** `0631 0634 0636 0638`
    (`\in_globals` / `isinstance`/`\typeof` / `\in_scope`). The lowering emitted `val in_globals_op` /
    `val typeof_op` / `val in_scope_op` (program functions) but used them inside `ensures`/`requires`
    (logic terms) → why3 *"unbound function or predicate symbol"*. A pure program `val` is not visible in
    logic; the symbols are uninterpreted (pure by construction), so the correct WhyML form is `val function`
    (a logic function usable in both terms and code). Fix: `module6_whyml/expressions.py` —
    `_tag_of_value` (`typeof_op`), `_handle_in_globals_expr` (`in_globals_op`), `_handle_in_scope_expr`
    (`in_scope_op`) now emit `val function …`. All four now `L3-tc ✓`; the change is a single-line
    `val`→`val function` per driver, byte-identical on the decided-true/false neighbors
    (`0603 0630 0632 0633 0635 0637`) and the rest of the corpus.
  - **String feature demand-drivers (13) — DEFERRED (expected-FAIL stretch targets, not a clean cohort):**
    `0477 0478 0479 0480 0482 0483 0484 0485 0486 0487 0488 0489`. All carry `# pycsl-expected: FAIL` and
    document the unsupported `str`-object surface (`<`, `*`/`%`, `hash`/`str`/`repr`/`format`, iteration).
    The type errors are heterogeneous (string-valued exprs used where `int` is expected; undeclared
    `hash_1`/`str_conv`/`repr_conv`/`format_1`/`iter_length`) — symptoms of the absent strings feature,
    not one emission bug. Correct resolution is the strings feature (strings-plan.md), not a patch.
  - **`list.append` Seq-vs-Array representation mismatch (2) — REPORT (modelling, sub-threshold):**
    `0406 0407` (the only two with NO `expected: FAIL` — genuinely dishonest). `list` params type as
    `array int` but `.append` lowers to `Seq.snoc` (sequence) → *"has type array … but is expected …"*.
    Choosing the canonical `list` representation (Seq vs growable Array) is a modelling decision, and it is
    a 2-driver cohort (below the ≥3 clear-cohort bar). Left for human decision.
  - **Singletons — REPORT (each a distinct negative/boundary test, all `expected: FAIL`):**
    `0050` (`variant … with subterm` — syntax error from the structural-variant lowering);
    `0303` (`\proj` out-of-range → undeclared `z_` from tuple-projection lowering);
    `0386` (strict-no-exception unannotated callee → undeclared `external_helper_1`);
    `0557` (arithmetic on a datatype quantifier binder — `color` vs `int`, ill-typed by design);
    `0560` (non-terminating lemma — *"cannot prove termination"*, the intended boundary);
    `0563`/`0575` (non-strictly-positive inductive — why3 correctly rejects, the point of the test);
    `0601` (returning an array of tuples — unsupported `array (int,int)` vs `array int`).
    These are intentional negatives whose "type error" IS the documented behavior; no emission fix applies.

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
