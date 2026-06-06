A **load-bearing** file is one whose incorrect modification produces *silent*
unsoundness in the proof pipeline — the toolchain still runs and reports
success, but the guarantee it certifies is no longer true.

Load-bearing files are enumerated in
`config/skills/agent-stdlib-annotate/references/load-bearing-files.md`. The
feature supervisor (`bin/agent-feature-supervisor`) treats any plan phase that
names one of them as a modification target by raising the `human-needed`
signal (exit 75) rather than editing it autonomously.

---

## Why load-bearing files matter in PyCSL

Most files fail loudly when edited wrongly: a test breaks, a proof fails, the
build errors. Load-bearing files are dangerous precisely because they can fail
*quietly* — a wrong edit to the parser, IR schema, or proof corpus can make the
pipeline emit verification conditions that pass while no longer corresponding to
the source program. Nothing downstream catches it, so the error has to be
prevented at the editing boundary by human review.

This is why they are excluded from autonomous agent edits even after
coding-LLM delegation lands: an agent that is right 99% of the time is still
unacceptable when the 1% is a silent soundness hole.

---

## Concrete examples

### The compiler pipeline

- **Modules 2–6 and the grammar (`csl.lark`)** — parser → IR → WhyML emitter.
  A wrong edit can silently emit unsound WhyML.
- **`ir_schema.py`** — the Module 5 ↔ Module 6 contract.
- **`exception_model.py`** — the trigger table for `no_exception`; wrong edits
  add or drop exception predicates from VCs.

### The proof corpus

- **`formal-semantics/`** — the Rocq + Lean soundness proofs.

### Normative documents

- The three `docs/pycsl-*-reference.md` files and the paragraph-stable
  `annotations.md` / `traceability-pycsl.md` — structural drift is caught by
  `bin/doc-coherency.py`, but the *content* needs human judgement.

---

## Related terms

- [trusted computing base](trusted-computing-base.md)
- [trust seam](trust-seam.md)
- [extreme rigor](extreme-rigor.md)

> **In short:** a load-bearing file is one whose wrong edit breaks soundness
> *silently* — so agents never touch it without a human in the loop.
