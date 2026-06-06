# Operators and quantifiers

Load when writing the right-hand side of `#@ requires` / `#@ ensures`
/ `#@ loop invariant` and you need to recall what operators are
admissible.

**Comparison and arithmetic:** `==`, `!=`, `<`, `>`, `<=`, `>=`, `+`, `-`, `*`, `/`, `//`

**Boolean:** `and`, `or`, `not`

**Implication:** `==>` (implies), `<==>` (iff)

**Pre-state values:** `\old(var_name)` — refers to the value at function entry.

**Quantifiers:** Write `\forall i; body` and `\exists i; body` (the alias `\exist` without trailing `s` is accepted). The bound variable `i` ranges over integers; write the range as part of the body using `==>`:

```python
#@ requires \forall i; 0 <= i and i < n ==> arr[i] >= 0
```

Quantifiers may appear at the top level of an expression **or** as the right-hand side of `==>`, `and`, and `or` without parentheses:

```python
#@ loop invariant found == 0 ==> \exists j; i <= j and j < n and arr[j] == target
```
