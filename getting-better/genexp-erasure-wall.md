# genexp-erasure-wall.md — `any`/`all` generator expressions erase to an unconstrained oracle, and the `Any`-tree walkers they live in are vacuous

**REVIEWED — see `genexp-erasure-wall-response.md` (verdict CONFIRM-WITH-CARVE-OUT). The review
REFUTED two load-bearing claims of this report and showed a third to be an understatement; the
corrections are applied inline below and marked `[CORRECTED]`. Do not read this document without
them — the uncorrected §3/§4 and §6c were wrong.**

**State-of-the-art report on a VACUITY wall, not a conversion wall: 9 `IRScanner`
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

**[CORRECTED] "8 fully erased" is a LOWER BOUND, not the exposure.** The probe is a whole-FUNCTION
test (it fires only when the emitted body mentions none of the parameters the live body uses), so a
function that erases one read while using its other parameters is invisible to it. The reviewer
found two more VERIFIED functions carrying a live, branch-controlling `any_1 (Array.make 1 0)`:
`statements.py::_handle_fieldassign_stmt` (from `if not any(stripped.startswith(p) for p in
map_prefixes)`) and `Module5_IREmitter.py::_union_arm_tag`. So the oracle sits on a load-bearing
branch in **at least 11** verified functions, not 9.

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

**Corpus exposure is ZERO** — confirmed by the reviewer over a verified population of 782 emitted
files (0 `any_1`/`all_1` sites, one source-level user). So a program-plane fix is byte-inert on the
corpus by construction.

**[CORRECTED] The claim that the SPEC plane already lowers `all(...)` faithfully to `forall` was
FALSE — this report's worst error.** `0021.py`'s `all(x >= 0 for x in a)` is a plain Python
`assert` inside `if __name__ == "__main__":` — not a `#@ assert`, not a spec context, and NOT
EMITTED AT ALL; the two `forall`s in its `.mlw` come from hand-written `#@ ensures \forall` /
`#@ loop invariant \forall` clauses and have nothing to do with `all()`. Probed directly: a genexp
inside `#@ assert` does not even PARSE (`expected ')' (got NAME 'for')`), and a non-genexp
`all(arr)` in a `#@ assert` lowers to the SAME unconstrained `all_1`. There is one handler
(`expressions.py:5392`, `if func_name in ("any","all")`) reached from every context. So there is no
faithful lowering in either plane, and no "existence proof that the shape is expressible" — that
argument is withdrawn. This cuts both ways: it removes a free-lunch argument AND raises the value of
(A), which must now serve BOTH planes and additionally repair `#@ assert all(...)`.

## 4. SOTA lens — what would make these real
Two independent capabilities, and the report's claim is that BOTH are needed for the 9:
- **(A) bounded `any`/`all` in program position.** `any(pred(x) for x in seq)` → an executable
  bounded fold/loop over `seq` accumulating `||`, with the predicate inlined at the bound
  variable. Byte-inert (§3). **[CORRECTED]** there is no spec-plane existence proof (§3); instead
  the fold is now oracle-PROVEN buildable by the reviewer: a pure `let function` with an **iff**
  postcondition, a positive driver and a working evil twin, Valid on BOTH z3 and Alt-Ergo,
  axiom-free (`anyfold.mlw`). This alone does NOT de-vacuify `IRScanner` — its `obj` is still
  int-erased.
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
alongside, the `map` — making `.values()` a list walk.

**[CORRECTED by the review — better news AND a harder blocker than this section supposed.]**
The assoc-list carrier WORKS: the reviewer folded the full `uses_string` as executable pure
`let rec function`s with a `size` variant over a mutually recursive `hval/hval_list/hval_pairs`,
proving a nested-`{"type":"String"}` positive driver (0.02s) and its evil twin (0.24s), axiom-free.
**So `.values()` over a `Dict[str,Any]` is NOT unmodellable** — §10.3 and `frontier_exhaustion_map`
are too pessimistic on this point, and that carve-out should propagate. BUT: "alongside the map"
is measurably DEAD. Re-adding the `HMap (map string (option hval))` arm to the same sum — nothing
else changed, the fold never even recursing into it — takes the evil twin from Valid to
**Timeout at 71M steps** (z3, 20s), and the logic-level variant dies outright at 60s with
`High failure (signaled)`. It is the NEGATIVE direction that dies, i.e. exactly the one that
distinguishes a real proof from a vacuous one. Not lesson (g): z3 proves `"Number" <> "String"` in
0.00s. The cause is the infinite-map theory coexisting with the ADT in one mutually recursive sum.

## 5. Honestly-costed routes
- **R1 (cheap, certain): re-trust the 9.** They are not verified in any meaningful sense; the
  honest classification is FLOOR/F3 (generic-`Any` tree walker) with a recorded reason. Cost:
  **count 981 → 990**, a visible regression that is really a correction of an overstatement.
- **R2 (bounded): build (A) alone.** Removes the `any_1` oracle everywhere, byte-inert,
  fixture-witnessed. Does NOT fix the 9 on its own. Also unblocks the verbatim port of
  `_pattern_has_constructor` (currently a hand-rewritten index loop — see wall-lessons (j)).
- **R3 [RE-SCOPED by the review — it is a CARRIER REPLACEMENT, not an addition]:** the map carrier
  is load-bearing today (`HMap` constructions and `Map.get` reads live in the already-converted
  `_collect_final_registry` / `_collect_type_params` / `_collect_typevar_registry`, plus a
  `map string (option (map string (option hval)))` return type, across 5 hval-emitting mirror
  files). So R3 = replace the carrier + re-lower every existing `hval` consumer + re-certify
  Phase2f + a mirror-wide L3-tc sweep. Its make-or-break Gate-S spike is condition 7 of the
  response: the assoc-list `hval` with ALL real arms in one sum, proving the evil twin under z3 in
  bounded time. If the map arm must stay, R3 DIES there. Original framing follows: (A) + (B) with an assoc-list `HMap`. Makes the 9 real. Requires an
  `hval` ADT change + re-certification + the `.values()` fold. High payoff, high risk.

## 6. Honest limits + certificate
(a) Does an assoc-list `HMap` still certify axiom-free (ledger 3), or does the cons-list carrier
break the Phase2f cert? (b) Does Why3 accept the recursive `hval` with a bespoke pair-list carrier
(the non-strictly-positive trap that forced `pyval_list` over `seq`)? (c) **[CORRECTED — this risk was FALSE on both halves and is withdrawn.]** It claimed
`uses_string` is emitted as a pure `let function` and that a loop with a mutable accumulator is not
pure, and guessed this might sink (A). The reviewer refuted both with Why3 and with the emitter: a
`let function` MAY contain a `while` loop over local `ref`s (they are allocated inside, so the
interface stays effect-free — `purity1.mlw` Valid), and the emitter does not emit these as
`let function` anyway (`let irscanner__uses_string (self) (obj: int) : int` with `try/raise Return`).
The REAL constraint, which this report missed, is the converse: the fold must be a pure
`let function` in order to be usable in a SPEC position (`assert`/`ensures`) — a plain `let` gives
`unbound function or predicate symbol`. That is satisfiable, and it is now a mandatory condition.

## 7. The make-or-break question for review
Can `any(pred(x) for x in xs)` in PROGRAM position lower to a bounded, executable fold that
TYPECHECKS and PROVES a non-trivial postcondition (e.g. `any(x > 10 for x in xs)` on a built
3-element array reads back `True`, and an evil twin reads `False`) — **axiom-free, ledger 3** —
given that the containing function is emitted as a PURE `let function`? And, separately: does an
association-list-carrier `hval` typecheck in Why3 and still certify axiom-free, so that
`obj.values()` becomes a real fold? **An oracle run — a hand `.mlw` with a bounded any-fold over
an array, a driver proving the positive AND refuting an evil twin, `why3 prove -P z3`, plus an
axiom check — should CONFIRM or REFUTE before any emitter edit.**
