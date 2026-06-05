A **demand-driver** is a real, verification-grade program that **fails today specifically because
of a missing capability** — the concrete justification PyCSL requires before that capability is
built.

It is "Gate A" of the project's development discipline: *don't build a feature without a
demand-driver.* If you cannot even write the program that fails for want of the feature, the
feature is deferred.

---

## Why demand-drivers matter in PyCSL

PyCSL deliberately collapses most Python types onto `int` because that tractability is *why* its
SMT goals discharge in milliseconds. Adding a real type or a new construct is therefore expensive
and is justified **demand-first, not category-first** — "strings are a category" is not a reason;
"this program proves nothing today *because* string content is hashed" is.

The discipline around a demand-driver:

- **FAIL-first.** Commit the driver as a numbered [reference test](reference-test.md) marked
  `# pycsl-expected: FAIL`, *then* implement the minimal slice that flips it to PASS. The feature
  is "done enough to justify itself" exactly when its driver flips.
- **One driver per operation.** Back the flagship with one driver per operation the feature
  enables — the corpus *is* the acceptance suite, satisfied operation-by-operation.
- **A negative driver too.** Ship a deliberately-false contract committed `# pycsl-expected: FAIL`
  so the modeled content is shown to have teeth (a positive-only test never shows the check can
  fail).
- **YAGNI exit.** If the driver turns out not to need the track, stop.

For new *theory* (recursive/algebraic types), a demand-driver is paired with a Gate-B
SMT-feasibility spike — a hand-written `.mlw` proved before any pipeline work.

---

## Concrete examples

### A driver that flips

A `Dict[int, str]` program asserting `\str_length(d[k]) == \str_length(s)` after `d[k] = s` fails
today (dict values are `int`); committed `# pycsl-expected: FAIL`, it flips to PASS exactly when the
parametric-map track lands.

### No driver, no build

A reflection dunder PyCSL already silently drops gets *recognize-and-document* treatment, not code —
there is no program that proves something new with it.

---

## Related terms

- [reference test](reference-test.md)
- [load-bearing](load-bearing.md)
- [emission-identical gate](emission-identical-gate.md)

> **In short:** a demand-driver is a real program that fails today for want of a feature, committed
> as an expected-FAIL test first and flipped to PASS when the feature lands — no driver, no build.
