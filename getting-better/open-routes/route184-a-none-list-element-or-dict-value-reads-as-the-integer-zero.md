# ROUTE #184 — a `None` list element / dict-literal value reads back as the integer 0

**Status: CLOSED by gen #29 (battery W green: suite 3780/3798, same 18 CONFIRMED FAIL, zero XPASS; planes --slow 34/34).** Severity 1.
Generator: the route #56 carriers measured by gen #29 (the FIELD one is route #183).

## Measured at `e842b16d`

    xs: List[Optional[int]] = [None];   return xs[0] == 0        PROVED True   (CPython False)
    xs: List[Optional[int]] = [None];   v = xs[0]; return v + 1  PROVED == 1   (CPython TypeError)
    d: Dict[str, Optional[int]] = {"a": None};  return d["a"] == 0            PROVED True (CPython False)

`Array.make 1 0` and `map_update_some … 0`: the `None` literal lowers to the integer 0 everywhere
(`_expr_to_whyml`'s `t == "None"` arm), so the element/value is a DEFINITE zero.

## Repair (draft)

Narrow, at the two literal builders (not the global `None` arm, which route #56 records as needing the
value model): a `None` element of a list literal, and a `None` value of a dict literal with an int
codomain, lower to route #44's opaque `pycsl_none`. Reads become UNDECIDED instead of wrong.
Emission byte-inert (corpus/pyref/mirrors). Witnesses 1651-1653 (XFAIL), 1654 (PASS: ordinary int
literals unchanged). Fast planes 19/19, conformance, sync green.

## Measured and NOT adopted (recorded)

Giving the TYPED `NoneExpr` arm the same opaque — which would also close the STORE positions
(`xs[0] = None`, `d["a"] = None`, `self.v = None`, `xs.append(None)`, all still PROVING `== 0`) —
moves 16 mirror emissions and breaks `check-singleton-constant-lowering`: that is route #56's general
repair (a distinguishable `None` in the value model), not a fail-closed fence, so it is left to the
value-model campaign. The dict-shaped arm's stale baseline entry in that plane is retired here.

## Still open (route #56)

Optional LOCALS in the conditional-join shape (#56 itself) and every other `None` position keep the
integer-0 lowering; the general repair is a distinguishable `None` in the value model.
