A **HAPPY** (**H**igh-level **A**ssertion-**P**roducing **PY**thon requirement) is a
module-level directive that declares one *cross-cutting whole-program integrity property*
over a shared instance field and **expands** it into many ordinary per-site obligations that
Why3 discharges.

It is PyCSL's analogue of ACSL / MetAcsl's **HILARE** (HIgh-Level Acsl REquirement) — borrowing
the *idea* (a high-level surface that lowers to existing primitives, **0 `\trusted`**), not the
multi-plugin machinery, since PyCSL has a single Why3/SMT backend.

The surface (`test-suite/annotations.md` §2.5):

```python
#@ happy region_integrity:
#@     region 512 .. 2560
#@     writes self.disk outside region
#@     except _write_inode, _write_directory
```

---

## Why HAPPY matters in PyCSL

A single requirement like "no method except the two writers ever writes outside the data region"
is awkward to state as a per-function contract — every method would need a clause about every
other method's region. HAPPY states it **once** and expands it into the obligations that actually
prove it.

The expansion is the load-bearing idea. A HAPPY over the location written `ℓ` becomes a per-write
`#@ check` injected **at every write site** `self.<field>[i] = …` in every method *not* in the
`except` set — e.g. `#@ check (i) < 512 or (i) >= 2560`. Each is an ordinary
[verification condition](verification-condition.md) Why3 already knows how to discharge.

Two properties make this sound without any alias or call-graph analysis:

- **Universal per-site coverage.** The obligation is injected at the *location actually written*,
  so an indirect write through a callee is caught at the callee's own site — the call graph is not
  load-bearing for soundness.
- **A trust boundary.** A `\trusted` / `\abstract` mutator that PyCSL cannot see into is opted into
  the property with `#@ \preserves`, which assumes a region-preservation `ensures` at that boundary.
  A non-exempt bodyless mutator *without* `\preserves` is a hard error.

Together these compose to a theorem: if every body-verified function carries the per-site `check`
and every other mutator is trusted-with-`\preserves`, then **no execution** violates the property,
because there is no third source of mutation.

Like `act` (its statement-level precedent), HAPPY adds **0 new IR nodes, 0 backend change, and
0 `\trusted`** — it is pure front-end expansion onto the existing statement-level `#@ check`
primitive.

---

## Concrete examples

### Region integrity

The `region_integrity` HAPPY above guards a virtual disk: every `self.disk[i] = …` outside the
two blessed writers must prove `i < 512 or i >= 2560`. A write inside `[512, 2560)` in any other
method fails its injected `check`.

### The `except` set

Methods that *legitimately* write the region (`_write_inode`, `_write_directory`) are listed in
`except` and receive no obligation. A typo in an `except` name is itself an error (it would
silently widen coverage).

### The trust boundary

A `\trusted` low-level writer carries `#@ \preserves` to assert it keeps the region intact; the
composition theorem then holds across both verified and trusted code.

---

## Related terms

- [class invariant](class-invariant.md)
- [meta-property](meta-property.md)
- [verification condition](verification-condition.md)
- [trusted stub](trusted-stub.md)
- [load-bearing](load-bearing.md)

## References — the HILARE / MetAcsl origin

HAPPY adapts the meta-property idea from Frama-C's **MetAcsl** plug-in, whose high-level ACSL
requirements (**HILARE**) are its direct ancestor:

- **MetAcsl: Specification and Verification of High-Level Properties** — V. Robles, N. Kosmatov,
  V. Prevosto, L. Rilling, P. Le Gall. *TACAS 2019*, LNCS 11427, pp. 358–364 (extended version
  arXiv:1811.10509). The tool paper: meta-properties, contexts, and the assertion-expansion
  transformation HAPPY mirrors.
- **Tame Your Annotations with MetAcsl: Specifying, Testing and Proving High-Level Properties** —
  same authors. *TAP 2019*, LNCS 11823. The detailed treatment; shows amenability to both proof
  *and* testing.
- **High-Level Program Properties in Frama-C: Definition, Verification and Deduction** — V. Robles,
  N. Kosmatov, V. Prevosto, P. Le Gall. *ISoLA 2024*, LNCS 15221. Recent overview, including the
  annotation blow-up cost and deduction techniques to manage it.

See `config/skills/acsl/references/metacsl-reference.md` and
`config/skills/acsl/references/bibliography.md` for the full treatment.

> **In short:** a HAPPY is one whole-program integrity requirement that expands into a per-site
> proof obligation at every write, so universal coverage — not call-graph reasoning — makes it
> sound.
