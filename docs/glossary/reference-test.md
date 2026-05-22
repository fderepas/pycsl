A **reference test** is a numbered example file in
`test-suite/corpus/pycsl-reference/` that demonstrates one supported annotation
pattern, proof pattern, or expected failure mode.

---

## Why reference tests matter in PyCSL

Reference tests are the public regression corpus for the language. They do three
jobs at once:

- show users the intended syntax
- pin a feature to an executable example
- support traceability from `test-suite/annotations.md` to concrete files

This is why new language features should add reference tests, not just
implementation code.

---

## Concrete examples

### Numbered corpus files

Files like `0006.py` or `0288.py` are small, named checkpoints in the reference
corpus.

### Traceability

`test-suite/traceability-pycsl.md` maps each annotation reference item to the
reference tests that cover it.

### Expected failures

Some reference tests intentionally carry `# pycsl-expected: FAIL` so the suite
can lock in known rejection behavior as well as success cases.

---

## Related terms

- [trusted stub](trusted-stub.md)
- [verification condition](verification-condition.md)
- [proof companion](proof-companion.md)

> **In short:** a reference test is the canonical executable example for one
> PyCSL feature or failure mode.
