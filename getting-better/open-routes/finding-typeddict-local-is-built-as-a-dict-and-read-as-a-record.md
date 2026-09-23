# FINDING (#49, gen #31) — a TypedDict LOCAL is BUILT as a dict and READ as a record

**STATUS: CONFIRMED LIVE by measurement, with the emitted WhyML read. NOT a soundness
route — Why3 rejects the mismatch, so it is fail-closed. NOT repaired here; the capability
is named at the end.**

## THE CLAIM

annotations.md §12.12: "a TypedDict class synthesizes a WhyML record `type td = { x: int;
y: int }`, **field access `p["x"]` becomes record-field access `p.x`**, and **construction
`{"x": 1, "y": 2}` becomes a record literal**." No position is excepted.

## THE MEASUREMENT — THREE POSITIONS, TWO BEHAVIOURS

| position | program | verdict |
|---|---|---|
| RETURN | `def build() -> Pt: return {"x": 1, "y": 2}` with `ensures \result.x == 1` | **SUCCESS** |
| PARAMETER | `def getx(p: Pt) -> int: return p["x"]` with `ensures \result == p["x"]` | **SUCCESS** |
| LOCAL | `p: Pt = {"x": 1, "y": 2}` then `return p["x"]` | **FAILED** |

and the local case's emission says exactly what is wrong:

```whyml
  type pt = { mutable x: int; mutable y: int }          (* the record IS declared *)

  let f () : int
    ensures  { (result = 1) }
  =
    let p = ref (map_update_some (map_update_some (const (None: option int)) "x" 1) "y" 2) in
    !p.x
```

The construction took the GENERIC BODY-DICT path (`map_update_some` over
`map int (option int)`, §12.1's model) while the READ took the TypedDict path (`!p.x`, the
record projection §12.12 promises). The two halves of one variable disagree about its type,
and Why3 rejects the file.

So the record-literal lowering is keyed on the RETURN position (and the parameter type),
not on a LOCAL's annotation.

## WHY IT IS NOT A ROUTE

The mismatch is a type error, caught by the backend. Nothing is proved. As with the
legacy-`Generic[T]` and bare-`Callable`-domain findings the same day, what stops it is
Why3's typechecker rather than a rule in PyCSL — sound, but by accident of the model rather
than by design.

## WHAT IT COSTS

A user following §12.12 writes the local form first (it is the natural one) and gets
`This expression has type map …, but is expected to have type pt` — an error naming two
types, neither of which they wrote. There is no diagnostic pointing at the position rule,
because the position rule is not written down anywhere.

## THE CAPABILITY, NAMED SO THE NEXT WINDOW CAN PRICE IT

The mechanism is not a guess — `_typeddict_record_literal`
(`module6_whyml/expressions.py`) says it in its own docstring:

> The construction context is **detected from `_func_return_type`** (a
> `return {"x":1,"y":2}` in a `-> Point` function): if the return type is a known TypedDict
> record's whyml_name, the literal is matched field-by-field against the record's declared
> fields … **Returns None for non-TypedDict construction contexts** (byte-identical
> fallback to the empty-map stub).

and its first two lines are

```python
frt = getattr(self, "_func_return_type", "")
if not frt:
    return None
```

So the RETURN type is the only construction context there is. An assignment to an annotated
local never reaches the record branch and falls back to the dict model, while the READ side
(`_typeddict_field_access`, invoked from `_handle_subscript`) looks the receiver up in
`_record_types` and projects. Two different context tests on the two halves of one variable.

**The fix is to give `_typeddict_record_literal` a second construction context — the
assignment TARGET's declared type — and have the annotated-assign path pass it.** The
record lookup it already does (`info.get("whyml_name") == frt and info.get("is_typeddict")`)
is the whole test; only the source of the type name changes. Scoping it to an annotated
target keeps every un-annotated dict literal on the existing path, which is what makes the
change byte-inert rather than merely measured-inert.

CENSUS, which is why a repair would be cheap to gate: **zero corpus files declare a
TypedDict LOCAL**, precisely because it does not work. Every TypedDict driver in the corpus
either returns a literal (`1787`, `1788`) or reads a parameter (`0891`). A repair is
corpus-byte-inert by construction and wants one positive driver plus a false twin.

Measured 2026-09-23.
