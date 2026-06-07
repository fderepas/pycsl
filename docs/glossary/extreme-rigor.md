**Extreme rigor** (ER) is the discipline that a unit of work is *done* only when
its explicitly-stated, machine-checked **acceptance claims** all pass — not when
its files were touched, not when the regression gate is green, and not when the
implementer feels finished.

The canonical statement (`feature-supervisor-extreme-rigor.md`):

> A phase is DONE when all its **Acceptance:** claims pass — not when its target
> files were touched, not when the gate is green, not when the implementer feels
> satisfied.

---

## Why extreme rigor matters in PyCSL

The verification gate (`cmmi-audit`, `doc-coherency`, reference tests) catches
*infrastructure* regressions: did the suite still pass? ER catches a different,
sneakier failure — the implementer *believing* a phase shipped its deliverable
when it didn't. The motivating incident: a phase declared "done" with every gate
green, while zero of its four target methods had actually been promoted from
`\trusted` to body-verified. The gate had nothing to say about it; only an
explicit acceptance claim (`grep -c "[VERIFIED]" >= 4`) would have caught it.

ER turns "done" into a predicate the machine evaluates, not a status a human
asserts.

---

## Concrete examples

### An ER plan

An **ER plan** is a `missing-*-feature.md` whose every `### Phase N` carries an
`**Acceptance:**` block of executable claims:

```markdown
**Acceptance:**
- `.venv/bin/python3 src/pycsl/pycsl.py unix-filesystem/UnixInodeFileSystem.py` exits 0
- `bin/cmmi-audit.sh --quick 2>&1 | grep -c "^    \[VERIFIED\]"` stdout >= `4`
```

`bin/agent-feature-supervisor` executes each claim and halts on the first
failure (`MISSING_ACCEPTANCE` if a phase has no claims; `STATUS_FORGED` if a
phase marked `**Status:** DONE` has a failing claim). See
[acceptance-syntax](../../config/skills/csl-from-scratch/references/acceptance-syntax.md).

### The recursive project-lifecycle link

ER is applied to its *own* rollout — the discipline is recursive across the
project lifecycle:

- The supervisor that enforces ER on feature plans is itself shipped under an ER
  plan (`feature-supervisor-extreme-rigor.md`), whose phases carry acceptance
  claims the supervisor must pass.
- That plan's **post-implementation retrospective** re-applies ER to the ER work
  itself, enumerating the gaps where the ER mechanism was not yet load-bearing
  and closing each with its own acceptance claim.
- This mirrors the CMMI tailoring (`cmmi-tailoring-plan*.md`): each layer of the
  lifecycle — code, the tool that checks code, the plan that ships the tool —
  is held to the same machine-checked "done" predicate.

### The stdlib bar

For standard-library annotation, ER is the *goal state*: body-verify what you
can, axiom-anchor what you cannot, and pair every remaining `\trusted` with a
named gap in a tracked plan (`stdlib-extreme-rigor.md`). `\trusted` stays a
tool; it stops being the default.

---

## Where ER begins: the source-of-truth squeeze

ER has two facets that meet here. It **begins** with the
[source-of-truth squeeze](source-of-truth.md) — layer S0 and cornerstone of the
[Squeeze Strategy](squeeze-strategy.md) — pinning *what the spec must say* between
the English norm and the reference implementation, before any invariant or
`\trusted` decision. It **ends** with the acceptance-claim "done" predicate above,
proving the squeezed spec actually shipped. Get the squeeze wrong and every
acceptance claim resting on it is *coherent and wrong*.

---

## Related terms

- [source of truth](source-of-truth.md)
- [squeeze strategy](squeeze-strategy.md)
- [load-bearing](load-bearing.md)
- [trusted stub](trusted-stub.md)
- [standard libraries](standard-libraries.md)
- [reference test](reference-test.md)

> **In short:** extreme rigor means "done" is an acceptance claim the machine
> checks — applied recursively to the code, the checker, and the plan that ships
> the checker.
