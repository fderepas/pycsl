**Source of truth** is the external authority that decides what a program or
library actually *means* — and therefore what a PyCSL contract must say. It is
**not** internal to the toolchain: a specification can be perfectly consistent
across the README, the reference docs, and the skills, yet still be *wrong* if it
does not faithfully reflect the source of truth (*coherent and wrong* — the worst
kind of green). Correctness is fidelity to it.

The source of truth has **two axes**, and you need both:

- **English — the normative specification.** What behavior is *specified*: the
  contract the language promises. This is what `ensures` clauses transcribe.
- **Execution — the reference implementation.** What behavior actually *happens*:
  it resolves whatever the English leaves implementation-defined or silent (edge
  cases, exact exception types, iteration order, boundary results), and it is the
  ground truth a runnable model must agree with.

Per `*CSL` family member:

| Language | English (normative) | Execution (reference impl.) |
|---|---|---|
| **Python** | [language reference](https://docs.python.org/3/reference/index.html) + [standard library reference](https://docs.python.org/3/library/index.html) | [CPython](https://github.com/python/cpython) |
| **C** | the ISO/ANSI C norms | GCC and LLVM/Clang |

---

## How the two axes divide labor

1. Read the **English** → write the strongest contract it justifies (the
   *intended* behavior, including documented exceptions).
2. Where the English is genuinely ambiguous or silent → the **reference
   implementation** decides, and the model must match what it actually does
   (pin it with a concrete test).
3. Where the two **disagree** → that is a finding to surface (a doc bug or an
   implementation quirk), not a coin to flip — record which source you followed.

## Relationship to ER and the Squeeze Strategy

Pinning a spec between its two sources of truth is the **cornerstone of the
[Squeeze Strategy](squeeze-strategy.md) (layer S0)** and the **first step of
[extreme rigor](extreme-rigor.md)**. Squeezed between English (which bounds the
contract from above) and the reference implementation (which bounds it from
below), the spec has **no freedom** — there is no "convenient" or "minimal"
contract to choose, only the one both sources force. This is *why* PyCSL's hardest
disciplines exist: faithful typing (no-more-int) is fidelity to the value model;
the exception model (faithful `KeyError`) is fidelity to what CPython raises; the
[standard libraries](standard-libraries.md) are transcribed from the library
reference and must behave as CPython does.

A directive's name lives in the *internal* canonical source
(`test-suite/annotations.md`); its *meaning* is anchored to the *external* source
of truth. Coherency (internal parity, checked by `bin/doc-coherency.py`) is not
the same as fidelity (to the source of truth, enforced by review and the
reference corpus).

Fuller statements: `config/skills/csl-philosophy/SKILL.md` "The source of truth";
`config/skills/csl-from-scratch/SKILL.md` §0.5 (S0); shapes the stdlib via
`config/skills/pycsl-stdlib-coverage/SKILL.md`.

---

## Related terms

- [squeeze strategy](squeeze-strategy.md)
- [extreme rigor](extreme-rigor.md)
- [standard libraries](standard-libraries.md)
- [trusted computing base](trusted-computing-base.md)
- [backend-as-enforcer](backend-as-enforcer.md)

> **In short:** the source of truth is the language's English norm *and* its
> reference implementation; a faithful contract is squeezed between them, and a
> spec that is internally coherent but unfaithful to them is coherent and wrong.
