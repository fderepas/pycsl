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

## Related terms

- [class invariant](class-invariant.md)
- [abstract op](abstract-op.md)
- [pure function](pure-function.md)
- [referential transparency](referential-transparency.md)

> **In short:** a mixin is a composable class fragment whose cross-mixin
> dependencies and shared state are declared so PyCSL can verify the composition
> is sound.
