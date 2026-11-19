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

## STATUS: **CLOSED**

**WIRED, not refused**: `("subscript", "read_str")` carrying
`in_bounds (String.length {0}) ({1})`, injected at the `char_code_at` site. The bound is
exact, so it DISCRIMINATES — measured: `ord(s[5])` on `"ab"` now fails and `ord(s[1])` still
proves. Witnesses `1160` (negative, anti-vacuity verified both ways) and `1161` (positive
control). All 32 planes green; mirror 53/53 type-clean and byte-inert; both corpora
byte-inert; metric unchanged at 459.

## THE NAMED FOLLOW-UP THIS ROUTE LEAVES BEHIND

The assert makes the claim conditional AT EVERY USE SITE, which closes the soundness hole.
It does NOT change the abstract val itself: `char_code_at` still carries two `ensures`
unconditional in `i`, as `chr_op` did before route #66. That is the sharper, more general
target and it is NOT yet done:

**AUDIT EVERY ABSTRACT `val` WHOSE `ensures` IS UNCONDITIONAL IN AN ARGUMENT PYTHON
CONSTRAINS.** Two have already been found this way, both by accident while probing something
else. A `val` with a total contract on a partial function is a false axiom in the preamble —
strictly worse than a missing trigger, because it is available to every proof in the unit
whether or not anyone wrote `no_exception`. The mechanical form of the check: for each
`_add_abstract_op` string, ask whether Python's corresponding operation is TOTAL over the
declared argument types; if not, the `ensures` must be guarded by a `requires`, or the
obligation must be injected at every call site (what this route did).
