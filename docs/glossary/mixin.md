A **mixin** is a class annotated with `#@ mixin` whose methods are composed into
a facade class via `#@ compose_from`, rather than being instantiated directly.

In PyCSL the mixin discipline makes Python mixin composition
**machine-checkable**: each mixin declares the methods it provides, the sibling
methods it depends on, and the facade state it reads or writes. The verifier
checks the composition is sound before flattening everything into the composer.

---

## Why mixins matter in PyCSL

PyCSL's own emitter (`Module6_WhyMLTranspiler`) is a facade that composes many
handler mixins (`ExpressionEmissionMixin`, `StatementEmissionMixin`,
`PreambleEmissionMixin`, …). Without mixin annotations, the cross-mixin
dependencies — shared state, sibling method calls — are invisible to the
verifier. The `#@ mixin` / `#@ compose_from` surface lets PyCSL verify each
mixin **once** in isolation, then check that the full composition is consistent.

---

## Directive summary

| Directive | Scope | Purpose |
|---|---|---|
| `#@ mixin` | class | Marks the class as a composable mixin. |
| `#@ provides <m>` | method | Declares the method as a provider. |
| `#@ shared_state <name>: <type>` | method | Deliberately shared facade state (multiple mixins may access it). |
| `#@ touches_field <name>: <type>` | method | Owned field (at most one mixin may own a given name). |
| `#@ depends_method <m>: <sig>` | method | Concrete dependency on a sibling's method. |
| `#@ requires_method <m>: <sig>` | method | Abstract operation the composer must supply. |
| `#@ compose_from <M1>, <M2>, …` | class | Composes the named mixins into the facade class. |

---

## Design: shared state and concrete dependencies

PyCSL's mixin model differs from textbook trait systems in two deliberate ways,
both driven by how PyCSL's own facade (`Module6_WhyMLTranspiler`) actually
composes its handler mixins.

**Shared state vs owned fields.** Textbook traits assume each mixin owns
disjoint fields; two mixins touching the same field is a conflict. PyCSL's
emission mixins do the opposite — `ExpressionEmissionMixin`,
`StatementEmissionMixin`, `PreambleEmissionMixin`, etc. all share facade state
(`self.program_ir`, `self._in_spec`, …). The `#@ shared_state` directive
declares a field as **deliberately shared** (not a conflict); `#@ touches_field`
keeps the owned-field / single-owner semantics for fields that genuinely should
be disjoint.

**Concrete dependencies vs abstract holes.** Textbook `requires_method` is
an abstract hole the composing class fills. PyCSL's sub-mixins instead call
**concrete** helpers that live in a sibling (`self._e`, `self._deref`,
`self._stmts_to_whyml`). The `#@ depends_method` directive models this: a
concrete dependency on a sibling's method, where the provider's contract must
**refine** the declared one. Both relations lower to the same abstract `val` at
verification time; the distinction is whether the dependency is resolved by the
composer (abstract) or by a named sibling (concrete).

---

## Verify-once property

Each `#@ mixin` is verified **once** in isolation against its declared
interface — dependencies become abstract `val`s (reusing the existing
abstract-op machinery). On `#@ compose_from`, only the resolution moves are
re-checked: unique-provider, contract refinement, and field classification.
This incremental property comes from the trait verification literature
(Damiani et al. 2014) and avoids re-proving every mixin method when the
composed class changes.

---

## Concrete example

From the reference corpus (`0549.py`):

```python
#@ mixin
class CoreEmit:
    #@ shared_state program_ir: int
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return x if x >= 0 else 0

#@ mixin
class MapOps:
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result >= 0
    #@ provides handle_get
    #@ ensures \result >= 0
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        return self.emit(k)

#@ compose_from CoreEmit, MapOps
class Facade:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
```

Each `#@ mixin` is verified once against its declared interface (dependencies
become abstract `val`s). On `#@ compose_from`, Module 4 checks that every
dependency has exactly one provider, no method has two providers, and every
written field is declared.

---

## Tiering

- **Tier 1** (implemented): conflict-free, diamond-free composition with shared
  state — the subset needed for PyCSL's own facade.
- **Tier 2** (gated): `#@ resolve` / `#@ exclude` for two-provider conflicts.
- **Tier 3** (shelved): diamonds and full behavioral-subtyping refinement.

---

## Literature

The mixin discipline is grounded in the trait verification literature:

- N. Schärli, S. Ducasse, O. Nierstrasz, A. Black. *Traits: Composable Units of
  Behaviour.* ECOOP 2003, LNCS 2743, pp. 248–274.
  — Introduces traits as composable, conflict-aware units; the `provides` /
  `requires` / `exclude` / `resolve` vocabulary PyCSL adopts.

- S. Ducasse, O. Nierstrasz, N. Schärli, R. Wuyts, A. Black. *Traits: A
  Mechanism for Fine-grained Reuse.* ACM TOPLAS 28(2), 2006, pp. 331–388.
  — The journal-length formalization (flattening property, diamond-free
  composition algebra).

- F. Damiani, J. Dovland, E. B. Johnsen, I. Schaefer. *Verifying Traits: An
  Incremental Proof System for Fine-grained Reuse.* Formal Aspects of Computing
  26(4), 2014, pp. 761–793.
  — Proves the **verify-once** property: each trait is checked in isolation;
  composition only re-checks resolution moves. This is the theoretical
  foundation for PyCSL's incremental mixin verification.

## Related terms

- [class invariant](class-invariant.md)
- [abstract op](abstract-op.md)
- [pure function](pure-function.md)
- [referential transparency](referential-transparency.md)

> **In short:** a mixin is a composable class fragment whose cross-mixin
> dependencies and shared state are declared so PyCSL can verify the composition
> is sound.
