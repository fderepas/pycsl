# Seventy-two postconditions the spec language could not say, and the two it still cannot

Generation #31, 2026-09-26T07:40Z. Backlog #60a, built and proved.

## The gap, and it was not a proof gap

`bin/price-the-conversions.py` had just measured that only 165 of 922 converted mirror
functions carry a postcondition claiming anything. The largest single family of missing ones
was obvious and unreachable:

    #@ ensures \result["type"] == "None"
    def _csl_none(self, node: CSLNone) -> Dict[str, Any]:
        return {"type": "None"}

    unbound function or predicate symbol 'subscript_get'

`frontend/Module5_IREmitter.py` has **74** single-`return`-a-dict-literal IR CONSTRUCTORS whose
`"type"` key IS the emitted node's tag — the fact every Module-6 walker's dispatch depends on.
All 74 carried `#@ ensures True`, and not because the model was missing: the BODY position has
read those keys through `_EMIT_IR_PROJ` (`kind_of`, `name_of`, `op_of`, …) for many
generations. Only SPEC position fell through to `val subscript_get (x: int) (i: int) : int`,
a PROGRAM val, which a logical term cannot apply.

**The sentence had nowhere to go.** That is a different and much cheaper kind of wall than a
value model.

## The patch, and why it is byte-inert by construction

In `_handle_subscript`, before every other branch:

    if (self._in_spec and value["type"] == "Result"
            and self._func_return_type == "emit_ir"
            and index is a String literal in _EMIT_IR_PROJ):
        return f"({_EMIT_IR_PROJ[key]} result)"

It fires only in spec position, only on `\result`, only when the enclosing function returns
the faithful `emit_ir` sum, and only for a key already in the projection table. A contract of
that shape is an L3-tc ERROR today, so no passing corpus program and no mirror can contain
one. The emitted clause is the one a human would write by hand:

    let pycsltojsonemitter___csl_none (self: pycsltojsonemitter) (node: cslnone) : emit_ir
      ensures { ((kind_of result) = "None") }

## 72 of 74 PROVE, and the two that do not are a TIMEOUT, not a falsehood

Annotated mechanically from the AST (every single-return dict literal with a literal `"type"`
key and an `#@ ensures True`): 74 functions, 71 emitted clauses, **L3-tc green, zero
`subscript_get`**. The whole file proves — except:

    Sub-goal postcondition of goal pycsltojsonemitter___py_expr_tuple'vc
      Timeout (30.00s, 39,981,778 steps)
    Sub-goal postcondition of goal pycsltojsonemitter___py_expr_ifexp'vc
      Timeout (30.00s, 80,324,449 steps)

while the other 72 discharge in well under a second each. The two that time out are exactly
the two whose construction carries SUB-NODE children built by a comprehension over
`self._py_expr_to_ir`, so `kind_of` has to be pushed through a recursive application the flat
constructors never build. **Left as `ensures True` deliberately, with the measurement written
at the site: a postcondition nobody can discharge is not a stronger contract, it is a red
gate.**

## AND THE IMPORTING MODULE CANNOT SAY IT AT ALL — which is a finding of its own

`pycsl.py` imports `PyCSLToJSONEmitter`, so its `.mlw` re-emits all 72 contracts on imported
`val` stubs. It failed to type-check with 72 copies of `subscript_get result 1342639453`,
because in THAT file the same function's stub is typed

    val pycsltojsonemitter___csl_append (self: …) (node: int) : map int (option int)

**The same function has two different modelled return types in two files** — the faithful
`emit_ir` where it is defined, the opaque `map int (option int)` where it is imported. In the
importing context the clause has no faithful reading at all, so it is DROPPED, structurally
(`_ensures_needs_emit_ir_result`, which looks for the IR shape, not for a rendering).

Dropping is sound in the only direction that matters: **a `val` with fewer `ensures` ASSUMES
LESS**, so every caller obligation is unchanged or harder. The defining module still proves
the clause; the importer simply does not get to use it. `pycsl.py` then proves (30 minutes).

The two-return-types inconsistency is recorded, not papered over. Closing it would let the
importing context carry these 72 facts too, which is where they would actually be USED — and
it is the same shape as the I4 bridge re-typing (#55): one end of a call edge moved and the
other did not.

## Result

    functional postconditions   165 -> 237 of 922 (18% -> 26%)
    mirror movers               2, both declared and both re-proved
                                (frontend__Module5_IREmitter, pycsl)
    emitter change              byte-inert for both corpora by construction, measured at the gate
