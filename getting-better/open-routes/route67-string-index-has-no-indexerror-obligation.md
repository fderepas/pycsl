# OPEN ROUTE #67 — A STRING SUBSCRIPT READ CARRIES NO `IndexError` OBLIGATION
# (found 2026-09-11 by relaunch #55, at `247f3baa`)

## THE HEADLINE

```python
#@ no_exception \all
#@ ensures True
def f() -> int:
    s = "ab"
    return ord(s[5])      # CPython: IndexError: string index out of range
```

**`[+] Verification SUCCESS! All contracts formally proven.`**

It lowers to `(char_code_at !s 5)` with no assertion in front of it.

## THE LIST TWIN IS CORRECT, WHICH IS WHAT LOCALISES IT

Measured in the same batch, under the identical `#@ no_exception \all`:

  * `xs: List[int] = [1]; return xs[i]` with a SYMBOLIC `i` — **does NOT discharge.**
  * `b = bytearray([1]); return b[5]` — **does NOT discharge.**
  * `1 // (a - a)` — **does NOT discharge.**
  * `s = "ab"; return ord(s[5])` — **PROVES.**

An ARRAY subscript read goes through the wired `("subscript", "read")` row and gets
`in_bounds (Array.length a) i`. A STRING subscript read goes down a different path
(`char_code_at`) that no row covers.

## AND THE ABSTRACT VAL ASSERTS TOTALITY — THE SAME SHAPE AS `chr_op` IN ROUTE #66

```whyml
  val char_code_at (s: string) (i: int) : int
    ensures { 0 <= result < 256 }
    ensures { result = Char.code (Char.get s i) }
```

Both postconditions are UNCONDITIONAL in `i`. So the model does not merely omit an
obligation — it positively asserts that indexing a string at ANY integer yields a byte, for
a partial Python operation. **A missing trigger says nothing; a total contract on a partial
function says something FALSE, and every consumer inherits it.** That is now the second
instance (after `chr_op`), which makes it a pattern worth a sweep of its own: **audit every
abstract `val` whose `ensures` is unconditional in an argument that Python constrains.**

## THE REPAIR SHAPE

Wire it, do not refuse it — the bound is exact and available:
`("subscript", "read_str") -> ("IndexError", "in_bounds (String.length {0}) ({1})")`,
injected at the `char_code_at` site. `in_bounds` is already in `PREDICATE_LIBRARY`, and an
`assert` is a logic context, so `String.length` may be used directly there. A correct index
must still discharge.
