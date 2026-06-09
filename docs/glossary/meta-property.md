A **meta-property** is a single high-level, cross-cutting requirement over *many* functions or
write sites that **expands** into many ordinary per-site proof obligations, which Why3 discharges
individually.

It is the umbrella concept; [HAPPY](happy.md) (whole-program region integrity) is PyCSL's first
meta-property. The idea is borrowed from ACSL / MetAcsl's high-level requirements (HILARE), without
the multi-plugin machinery — PyCSL has a single Why3/SMT backend.

---

## Why meta-properties matter in PyCSL

Some properties are *whole-program*: "no method except these two ever writes outside the data
region", "this secret field is never written by any function but `encrypt`". Stating such a
property as per-function contracts is quadratic and brittle — every function would need a clause
about every other. A meta-property states it **once** and lets the compiler expand it.

The expansion follows the operating discipline established by HAPPY:

- **Desugar to existing primitives — never grow the TCB.** A meta-property adds **0 new IR nodes,
  0 backend change, 0 `\trusted`**; it lowers onto the existing statement-level `#@ check`
  primitive entirely in the front-end.
- **Universal per-site coverage, not call-graph reasoning.** The obligation is injected at the
  *location actually written/read*, so an indirect access through a callee is caught at the
  callee's own site — making it sound without alias or points-to analysis.
- **A trust boundary closes the gap.** A `\trusted` / `\abstract` function the compiler cannot see
  into is opted in with `#@ \preserves`; the per-site coverage plus that boundary **compose** to a
  whole-program theorem.

---

## Concrete examples

### Region integrity (a `\writing` meta-property)

A [HAPPY](happy.md) such as "writes `self.disk` outside `[512, 2560)` are forbidden except in two
writers" expands into a `#@ check (i) < 512 or (i) >= 2560` at every `self.disk[i] = …` site.

### Confidentiality (a `\reading` meta-property)

"Only `encrypt` reads `self.secret`" expands per-function: in every function except `encrypt`,
every read of the secret is an obligation that fails — caught at the reading site.

---

## Related terms

- [HAPPY](happy.md)
- [class invariant](class-invariant.md)
- [load-bearing](load-bearing.md)
- [trusted computing base](trusted-computing-base.md)

> **In short:** a meta-property is one cross-cutting requirement that expands into many per-site
> obligations, made sound by universal coverage plus a trust boundary — not by reasoning about the
> call graph.
