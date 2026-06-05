The **emission-identical gate** is the acceptance test for a *refactor* of the PyCSL compiler:
because PyCSL is an output-deterministic transpiler, a refactor is correct **iff the emitted WhyML
(`.mlw`) is byte-identical before and after**, across the whole corpus and every memory model.

"The tests still pass" is too weak a bar — a subtle IR/emission change can silently change what is
*provable*. Byte-identical output is the only signal strong enough.

---

## Why the emission-identical gate matters in PyCSL

A refactor is supposed to change *structure, not output*. PyCSL maps a Python file
deterministically to a `.mlw` file, so the refactor's correctness is directly observable: diff the
generated WhyML. A diff means a behavior change (or a baseline that was not clean).

The procedure:

1. **Clean baseline.** Generate the corpus WhyML from the pre-refactor code into a baseline dir.
2. **Deterministic generation.** For each `test-suite/corpus/pycsl-reference/*.py`, run
   `PYTHONHASHSEED=0 python src/pycsl/pycsl.py <f> --no-proof --keep-mlw <per-file flags>`.
   `PYTHONHASHSEED=0` is mandatory — string-literal ids are `hash()`-based and vary per run
   otherwise. Honor each file's `# pycsl-flags:` so model-specific files emit under their model.
3. **Diff.** `diff -rq base after` → **0 diffs, 0 "Only in base"**. Anything else is a regression.
4. **Cover all four memory models** (`hoare` / `concurrent` / `typed` / `store`) — the differential
   only validates the branches the corpus exercises.
5. Back it with a **full proof sweep** showing zero pass/fail delta, and keep commits small and
   individually-diffed.

**Carve-out:** CLI / orchestration changes (`pycsl.py` `main()` / argparse) change control flow,
not WhyML, so the differential cannot see them — gate those with `test-suite/cli-behavior-test.sh`
(exit codes + output markers) instead.

---

## Concrete examples

### A pure refactor passes

Unifying two duplicated parameter-type dispatch sites emitted byte-identical `.mlw` across all 454
emitting corpus files and zero proof-sweep delta — proving the change was a no-op.

### A latent bug fix is *not* a refactor

If a refactor would change emission (even an improvement), it is not behavior-preserving; the fix is
split into a separate commit with its own [demand-driver](demand-driver.md).

---

## Related terms

- [reference test](reference-test.md)
- [load-bearing](load-bearing.md)
- [demand-driver](demand-driver.md)

> **In short:** the emission-identical gate accepts a compiler refactor only when the generated
> WhyML is byte-identical across the whole corpus and all memory models — "tests pass" is not
> enough.
