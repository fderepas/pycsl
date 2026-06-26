# os.walk generator + heterogeneous-tuple return not emittable

**Category:** Ergonomics gap (language coverage)
**Filed by:** test-supervise-sl (os.walk fleet, gap-3)
**Date:** 2026-06-23 16:30

## Problem

Two related emission gaps block a faithful `os.walk` formal test:

1. **`yield` not supported.** A generator function (`yield top, dirs, nondirs`)
   emits the `yield` expression as type `()` (unit), causing a WhyML type
   error on the walk import stub ("This expression has type (), but is
   expected to have type int"). PyCSL has no generator/coroutine model.

2. **Heterogeneous tuple return not inferable.** Rewriting `walk` to return
   `[(top, dirs, nondirs)]` (a list of `(string, list string, list string)`
   tuples) fails: the tuple component-type inference defaults to `int`, so
   `return [(top, dirs, nondirs)]` emits "expression has type
   `(string, seq string, seq string)`, expected `int`". A `list string`
   return alone also fails (defaults to `seq int`).

## Consequence

`os.walk` could not be formally tested through the public API. Workaround
landed (gap-3): `walk` rewritten as a NON-generator returning the bounded
COUNT of subdirectory names (`ensures 0 <= \result <= 16`), body-verified
zero-TCB. This narrows the public return (the original yielded
`(top, dirs, nondirs)` triples) but preserves the totality + bounded-result
consequence a caller can prove. `os/__init__.py` still SUCCESS;
`formal_os_walk.py` now PASS.

## Suggested fix

1. Model `yield` (generator functions) — at least single-`yield` producers
   lowered to a list-return + a `Return_seq` payload, or an opaque iterator
   with a `has_next`/`next` contract.
2. Infer tuple/seq component types from the body (`return (s, lst)` where
   `s: string`, `lst: list string` → `(string, seq string)`, not `int`).
   Would let `walk` return the faithful `(top, dirs, nondirs)` shape.
3. Once either lands, restore `walk`'s faithful tuple/list return and
   strengthen the formal test to assert the yielded triple's structure.
