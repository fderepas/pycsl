# genexp-erasure-wall.md — `any`/`all` generator expressions erase to an unconstrained oracle, and the `Any`-tree walkers they live in are vacuous

**For review. State-of-the-art report on a VACUITY wall, not a conversion wall: 9 `IRScanner`
methods are booked as CONVERTED and PROVEN while their emitted WhyML never reads its input. The
question for review is whether the `hval` value model + a bounded `any`/`all` lowering can make
them real, or whether this is a genuine CERTIFIED-BOUNDARY and the 9 must be re-trusted (count
981 → 990).**

## 1. Global picture
PyCSL lowers annotated Python to WhyML discharged by Why3/SMT; the self-annotation campaign drives
the mirror's `#@ \trusted` count down. Count is **981**; ledger **3** (must stay 3). The campaign's
anti-facade gate is a MUTATION TEST (perturb a discriminant → the emitted `.mlw` must change).
This report concerns a facade family that PASSES that test.

## 2. The wall — first seen
`bin/check-emitted-vacuity.py` (built this run) reports **8 fully-erased + 4 partially-erased**
VERIFIED functions — a body that never references a parameter its LIVE counterpart uses. All 8
fully-erased are `IRScanner`'s generic-tree predicates. Canonical instance:

```python
@staticmethod                                  let irscanner__uses_string (obj: int) : int =
def uses_string(obj: Any) -> bool:               if ((typeof_op 315) = 4) then
    if isinstance(obj, dict):                      if ((obj_get_1 1342639453) = 1153884070) then
        if obj.get("type") == "String":               raise (Return 1)
            return True                            else raise (Return (if (any_1 (Array.make 1 0))
        return any(uses_string(v)                                       then 1 else 0))
                   for v in obj.values())       else if ((typeof_op 315) = 3) then …
    if isinstance(obj, list):
        return any(uses_string(item) for item in obj)
    return False
```

Three separate erasures compose:
- **`obj` is `Any` → `int`.** `isinstance(obj, dict)` becomes `typeof_op 315` — applied to the
  HASH CONSTANT 315, not to `obj`. Likewise `obj.get("type")` → `obj_get_1 1342639453`.
- **String literals become hashes.** `"String"` → `1153884070`.
- **`any(genexp)` → `any_1 (Array.make 1 0)`**, where `val any_1 (a: array int) : bool` is
  UNCONSTRAINED and the argument is fabricated from nothing.

Net: `obj` appears NOWHERE in the emitted body. The proof is vacuous with respect to the input.

**Why the mutation test misses it:** changing `"String"` changes its hash, so the emitted `.mlw`
DOES move. The gate is satisfied by the erasure itself.

**Not unsoundness — vacuity.** An unconstrained `bool` guard forces the verifier to prove both
branches, so nothing false was derived. What is missing is CONTENT: nine proofs that say nothing.

## 3. The `any`/`all` half is broader than the `Any` half, and independently measurable
The erasure is NOT specific to generic trees. Minimal spike (`scratchpad/anyspike/a1.py`):
```python
def has_big(xs: List[int]) -> bool:      let function has_big (xs: array int) : int =
    return any(x > 10 for x in xs)         (if (any_1 (Array.make 1 0)) then 1 else 0)
```
A plain `List[int]` with a trivial predicate erases identically — `xs` is dropped.

**Corpus exposure is ZERO.** One reference program (`0021.py`) uses `all(...)`, and it sits in a
`#@ assert` — a SPEC context, which already lowers FAITHFULLY to `forall i. 0 <= i < n -> arr[i]
>= 0`. Across the 782-file emitted baseline there are **0** `any_1`/`all_1` sites. So the spec
plane has a faithful lowering and the PROGRAM plane does not, and any program-plane fix is
byte-inert on the corpus by construction.

## 4. SOTA lens — what would make these real
Two independent capabilities, and the report's claim is that BOTH are needed for the 9:
- **(A) bounded `any`/`all` in program position.** `any(pred(x) for x in seq)` → an executable
  bounded fold/loop over `seq` accumulating `||`, with the predicate inlined at the bound
  variable. The spec plane's `forall` lowering is the existence proof that the shape is
  expressible; the program plane needs the executable analogue. Byte-inert (§3). This alone does
  NOT de-vacuify `IRScanner` — its `obj` is still int-erased.
- **(B) the generic-`Any` tree value model.** `obj: Any` must become a real ADT. The campaign
  already has one: **`hval = HStr | HInt | HArr | HMap | HNode`** (certified axiom-free,
  Phase2f, ledger-neutral). `isinstance(obj, dict)` → `is_hmap`, `obj.get("type")` → a projection,
  recursion → structural recursion over `hval`.

**The suspected blocker inside (B), and the real question for review:** `obj.values()`. `HMap`
carries `map string (option hval)`, and a Why3 `map` is an INFINITE function — it cannot be
iterated, so `for v in obj.values()` has nothing to fold over. This is precisely the
"generic-dict `.values()` walker" class that `frontier_exhaustion_map` and lesson §10.3 record as
not modellable. The candidate escape is to give `HMap` an **association-LIST carrier** (a bespoke
cons-list of `(string, hval)` pairs, the `pyval_list` pattern that Why3 accepts) instead of, or
alongside, the `map` — making `.values()` a list walk. That would change the certified `hval`
ADT and require re-certification (ledger must stay 3).

## 5. Honestly-costed routes
- **R1 (cheap, certain): re-trust the 9.** They are not verified in any meaningful sense; the
  honest classification is FLOOR/F3 (generic-`Any` tree walker) with a recorded reason. Cost:
  **count 981 → 990**, a visible regression that is really a correction of an overstatement.
- **R2 (bounded): build (A) alone.** Removes the `any_1` oracle everywhere, byte-inert,
  fixture-witnessed. Does NOT fix the 9 on its own. Also unblocks the verbatim port of
  `_pattern_has_constructor` (currently a hand-rewritten index loop — see wall-lessons (j)).
- **R3 (session-scale): (A) + (B) with an assoc-list `HMap`.** Makes the 9 real. Requires an
  `hval` ADT change + re-certification + the `.values()` fold. High payoff, high risk.

## 6. Honest limits + certificate
(a) Does an assoc-list `HMap` still certify axiom-free (ledger 3), or does the cons-list carrier
break the Phase2f cert? (b) Does Why3 accept the recursive `hval` with a bespoke pair-list carrier
(the non-strictly-positive trap that forced `pyval_list` over `seq`)? (c) Can the emitter emit a
bounded `any`/`all` fold at all in a `let function` (PURE) context — `uses_string` is currently
emitted as a pure function, and a loop with a mutable accumulator is not pure? That third one is
the cheapest falsifier and may sink (A) on its own.

## 7. The make-or-break question for review
Can `any(pred(x) for x in xs)` in PROGRAM position lower to a bounded, executable fold that
TYPECHECKS and PROVES a non-trivial postcondition (e.g. `any(x > 10 for x in xs)` on a built
3-element array reads back `True`, and an evil twin reads `False`) — **axiom-free, ledger 3** —
given that the containing function is emitted as a PURE `let function`? And, separately: does an
association-list-carrier `hval` typecheck in Why3 and still certify axiom-free, so that
`obj.values()` becomes a real fold? **An oracle run — a hand `.mlw` with a bounded any-fold over
an array, a driver proving the positive AND refuting an evil twin, `why3 prove -P z3`, plus an
axiom check — should CONFIRM or REFUTE before any emitter edit.**
