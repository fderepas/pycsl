# TY3 Gap — Multi-instantiation Module 6 field-mangling collision

**Status:** GAP (conformance-agent finding, Gate C).
**Date:** 2026-06-27
**Construct:** TypeVar/Generic (TY3) — multi-instantiation monomorphization.
**Spec:** `typing-engagement/ty3/typevar-generic-twoplane-spec.md` §1.2 G3.

## 1. The finding

The monomorphization pass correctly emits TWO specialized copies for a module
with `Stack[int]()` + `Stack[str]()` — `Stack_int` and `Stack_str`, each with
substituted field types and contracts. The IR is well-formed
(`type_decls` carries two distinct records with the SAME field names `_items`/
`_size`).

Module 6's record emission then **mangles the field names** to avoid a WhyML
clash (it prefixes fields with the lowercased class name when two records share
field names — the existing inheritance-dedup behaviour). So `Stack_int._items`
becomes `stack_int__items` in the WhyML record declaration. BUT the
**invariant** and the **method `requires`/`ensures`/body** references to
`self._items` are NOT consistently mangled — they keep `self._items` /
`_items`. The result is an unbound-symbol Why3 typecheck failure:

```
type stack_int = { mutable stack_int__items: array int; mutable stack_int__size: int }
  invariant { ((stack_int__size >= 0) && (stack_int__size <= (Array.length _items))) }
                                                                    ^^^^^^^ unbound
```

## 2. Why it is a gap, not a blocker

- The **single-instantiation** path (the feasibility-probe shape, the S5_int
  conformance driver, the P5 no-blend driver) proves 10/10 VCs — there is only
  one record, so Module 6 does NOT mangle the field names, and the invariant/
  requires references resolve.
- The **multi-instantiation** path is the case the overview §4.1 names ("emit
  one specialized copy per instantiation"). The monomorphization pass produces
  the correct IR; the gap is in Module 6's field-mangling consistency, NOT in
  the monomorphization machinery itself.
- Per `typing-global-impl.md` §0: "divergence-by-strictness is legitimate and
  recorded; divergence-by-weakness is a bug." This is neither — it is a
  lowering inconsistency for a shape (two records with shared field names) that
  pre-exists monomorphization (inheritance already produces it). The honest-
  scope discipline (impl guide §0) says a gap doc is the right move, NOT a
  `\trusted` shortcut or a weakened clause.

## 3. The fix (for a follow-up, NOT this delivery)

Module 6's field-mangling (in `module6_whyml/` — the record emission +
invariant/field-access lowering) must apply the SAME mangling to:
- the record declaration's field names,
- the `invariant { ... }` references,
- the `by { ... }` witness,
- every method's `requires`/`ensures`/`assigns`/body field access.

The cleanest fix is to make the field-mangling a single pass that rewrites
ALL field references consistently, rather than mangling at emission-time in
multiple places. This is a Module 6 refactor, scoped to the
shared-field-name case (which is exactly what inheritance + monomorphization
produce).

## 4. What graduates NOW

- The monomorphization machinery (COLLECT, GT3/GT4, BOUNDS, EMIT, CLASSIFY)
  graduates for the **single-instantiation-per-generic** case (the feasibility-
  probe shape, proven 10/10). This is the load-bearing path the overview §4.1
  names and the probe verified.
- The multi-instantiation case is gated behind this gap doc — a driver with
  `Stack[int]` + `Stack[str]` in one module does NOT yet prove. The gap is
  recorded here, NOT shortcut.

## 5. Artefacts

- `typing-engagement/ty3/mono_stack_two.py` — the multi-instantiation driver
  (fails L3-tc on the unbound `_items`).
- `typing-engagement/ty3/mono_stack_int.py` — the single-instantiation driver
  (10/10 VCs Valid).
