# FINDING (#49, gen #31) — a TypedDict LOCAL is BUILT as a dict and READ as a record

**STATUS: CLOSED (2026-09-23, gen #31).** Was: confirmed live, fail-closed, not a
soundness route. The repair is at the end; the prototype and the price that made it cheap
are the two sections before it.

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


---

## PRICE (added 2026-09-23, after route #213 showed why this matters)

Route #213's record priced its own repair an order of magnitude too high by ASSUMING that
a function in `module6_whyml/expressions.py` is mirrored un-trusted; `_lower_getattr` turned
out to have no mirror twin at all, and the fix cost one small mirror re-proof instead of the
largest in the tree. So this finding's price is CHECKED rather than assumed:

| function | mirror twin | cost of editing it |
|---|---|---|
| `_typeddict_record_literal` | **UN-TRUSTED** (verbatim body port) | verbatim mirror edit + the `expressions.py` mirror whole-file re-proof (21347 goals, ~4 h) |
| `_expr_to_whyml` (its only caller) | `\trusted` | free — no verbatim sync, no re-proof |

So the OBVIOUS edit — give `_typeddict_record_literal` a second construction context — is
the EXPENSIVE one. The cheap shape is to leave that function alone and supply the context
from the `\trusted` side: `_expr_to_whyml`'s `DictLit` branch can set
`self._func_return_type` to the annotated assignment target's type around the call and
restore it afterwards, so the existing record lookup fires unchanged.

What still has to be found is where the TARGET's declared type is available at that point.
`_expr_to_whyml` does not know the assignment target, so either the annotated-assign
statement handler passes it down through an instance field (check ITS mirror twin first —
the same way), or the DictLit branch reads it from the symbol table for the local being
assigned. **That lookup is the open question, and it is the only one**; the rest of the
repair is the context switch above.


---

## PROTOTYPED (2026-09-23, in a scratch copy of the compiler — the tree was frozen for a suite)

The repair is TWO changes, both in `\trusted`-mirrored functions, and both were needed —
the first alone produced a record literal that the second step then threw away.

**(1) `_handle_assign_stmt` (twin `\trusted`) — supply the construction context.** Around
the RHS lowering, when the RHS is a `DictLit` and the TARGET's declared type (read from
`self._current_symbol_table`) names a `_record_types` entry with `is_typeddict`, set
`self._func_return_type` to that record's `whyml_name` and restore it afterwards. That is
the only context `_typeddict_record_literal` consults, and the un-trusted function is left
untouched.

Instrumented, this alone gives `val = '{ x = 1; y = 2 }'` — the record literal.

**(2) `_emit_first_assign` (twin `\trusted`) — do not let the dict path overwrite it.**
`_first_assign_kind` classifies a `Pt`-annotated local as `"dict"` (its twin is UN-TRUSTED,
so it is deliberately NOT edited), and the `kind == "dict"` branch replaces `val` with
`_build_dict_literal_map`'s `map_update_some` fold. Bypass that branch for a TypedDict
target and emit `let X = ref { … } in`.

`ref`, not a bare value: the READ side (`_typeddict_field_access`) emits `!p.x`, so a
value binding gives `This expression has type PyCSL_Program.pt @rho` — measured, and the
one-token difference between the two attempts.

MEASURED in the scratch copy:

| driver | before | after |
|---|---|---|
| LOCAL `p: Pt = {…}` then `p["x"]` | FAILED | **SUCCESS** |
| LOCAL, `p["x"] + p["y"] == 3` | (could not emit) | **SUCCESS** |
| the false twin, `== 4` | — | **FAILED** |
| RETURN position (`-> Pt`) | SUCCESS | SUCCESS |
| PARAMETER position (`p: Pt`) | SUCCESS | SUCCESS |

So the price is settled: **no un-trusted mirror edit, no `expressions.py` re-proof**, two
trusted-side changes, and a census that already says zero corpus files declare a TypedDict
local. What remains before landing is the ordinary discipline — byte-diff, the corpus
TypedDict drivers (`1787`, `1788`, `0891`), and a positive/false-twin pair in the corpus.


---

## LANDED (2026-09-23, gen #31)

Both changes are exactly the prototype above, in the live tree:

* `_handle_assign_stmt` (twin `\trusted`) supplies the construction context from the
  TARGET's declared type, scoped to that one lowering and restored immediately;
* `_emit_first_assign` (twin `\trusted`) returns `let X = ref { … } in` for a TypedDict
  target instead of falling into the dict path that rebuilds the `map_update_some` fold.

`_typeddict_record_literal` and `_first_assign_kind` — both UN-TRUSTED twins — are
untouched, so no `expressions.py` or `types.py` re-proof is owed.

MEASURED: the LOCAL form verifies (`1865`), its false twin `== 4` FAILS (`1866`), and the
RETURN and PARAMETER positions are unchanged. All SEVEN corpus TypedDict drivers keep their
verdicts (`0743`, `0888`, `0889`, `0890`, `0891` PASS; `1787`, `1788` REFUSED). BYTE-DIFF
1345 -> 1349 (the four new drivers across this batch), **0 MOVED / 0 GONE / 0 unexpected
APPEARED**; 2199 python-reference `.mlw` byte-identical — corpus-byte-inert exactly as the
census predicted, because zero corpus files declared a TypedDict local. Fidelity 886
verbatim; IR conformance 38 goldens 0 MISMATCH.
