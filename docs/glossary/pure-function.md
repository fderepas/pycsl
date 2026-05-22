In PyCSL, a **pure function** is a function or method whose contract says
`#@ assigns \nothing`.

For contract-call purposes, PyCSL also expects that function not to be
`#@ \diverges`; if it is recursive, it needs a `#@ \variant`. So in PyCSL,
"pure" mostly means "safe to mention inside specifications," not just "written
in a functional style."

---

## Why pure functions matter in PyCSL

PyCSL allows pure functions to appear inside `requires`, `ensures`, and loop
invariant expressions.

That matters because pure helpers let you write contracts in the language of
the program instead of repeating arithmetic by hand. They also interact cleanly
with frame conditions:

- `#@ assigns \nothing` says the call does not mutate verification-relevant
  state
- contract calls stay trustworthy because the helper cannot hide side effects
- read-only methods often count as pure and do not need invariant-guarding
  preconditions

---

## Concrete examples

### Contract helper: `abs_val`

In `0194.py`, `abs_val` is declared with `#@ assigns \nothing`, and another
contract uses it directly:

```python
#@ ensures \result == abs_val(a) + abs_val(b)
def sum_abs(a: int, b: int) -> int:
```

This is the standard PyCSL pattern: define a side-effect-free helper once, then
reuse it in specifications.

### Recursive pure helper: `sum_to`

In `0195.py`, `sum_to` is both pure and recursive:

```python
#@ assigns \nothing
#@ \variant n
def sum_to(n: int) -> int:
```

The `\variant` matters because recursive contract-callable helpers still need
an explicit termination measure.

---

## Related terms

- [class invariant](class-invariant.md)
- [loop invariant](loop-invariant.md)
- [verification condition](verification-condition.md)

> **In short:** in PyCSL, a pure function is a side-effect-free contract
> helper, not just a stylistic programming preference.
