# ROUTE #116 — `F("name")(args)` is lowered as a call to the function NAMED BY THE STRING,
# whatever `F` actually returns

**Status: FOUND, REPRODUCED (gen #23, 2026-09-14). NOT REPAIRED.**
**Severity: SEV-1. First-order.** A callable class constructed from a string is ordinary Python.

## PROVENANCE

Generator `carve-out-census`, found while verifying route #115's fence story. A recognizer
written for ONE mirrored file was installed for EVERY program, and its only fence is a census
comment.

## THE MECHANISM, quoted

`src/pycsl/frontend/Module5_IREmitter.py`, `_py_expr_call` ("CLASS-BY-NAME FACTORY"):

```
        # ... Measured across the whole tree:
        # 171 `_N` sites, 161 with a string-literal argument, all in `pure_ast.py`; the
        # reference corpus has none.
        if (isinstance(expr.func, ast.Call)
                and isinstance(expr.func.func, ast.Name)
                and len(expr.func.args) == 1
                and not expr.func.keywords
                and isinstance(expr.func.args[0], ast.Constant)
                and isinstance(expr.func.args[0].value, str)):
            _cls_ir: Dict[str, Any] = {
                "type": "Call", "func": expr.func.args[0].value,
                "args": [self._py_expr_to_ir(a) for a in expr.args]}
```

The outer callee's NAME is never consulted: `pure_ast.py`'s `_N("If")(...)` and a user's
`Pick("inc")(3)` are the same shape, and both become `Call(func="inc")`. **A census is a
measurement of today's tree, not a guard.**

## MEASURED at baseline worktree `21d5029e` (source == HEAD `6f36d67f`)

`n_strfactory_cls.py`:

```python
#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1

class Pick:
    #@ assigns self.name
    def __init__(self, name: str) -> None:
        self.name = name

    #@ ensures \result == y - 1
    #@ assigns \nothing
    def __call__(self, y: int) -> int:
        return y - 1

#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return Pick("inc")(3)
```

`[+] Verification SUCCESS` rc=0. Emitted body of `f`: `(inc 3)`. **CPython returns 2.**

Also LIVE with a `\trusted` factory function `pick(s) -> Callable` (the trust asserts nothing
about the return, so it does not justify the proof) — logged, not used as the witness. Two
VACUOUS attempts logged (a function used as a value is emitted twice: "Symbol dec is already
defined"; a lambda-bodied factory is a Why3 type error).

## REPAIR SKETCH (census first)

Key the recognizer on the OUTER CALLEE'S IDENTITY — the mirror's `_N` helper, resolved as the
module-level function of that name — not on the argument shape; everything else falls to the
ordinary computed-callee path (route #24's opaque value, once route #115's Module 5 catch-all
no longer pre-empts it). The companion VARIABLE-NAME arm (`ClassByNameCall`) has the same
un-keyed outer callee and must be checked in the same increment.

---

## SECOND CARRIER — THE VARIABLE-NAME ARM DECLINES TO THE LITERAL `0` (measured, gen #23)

Predicted above, then run. `name = "inc" if c else "dec"; return Pick(name)(3)`:
`_collect_class_name_ternaries` (statements.py) accepts ANY single-assigned local whose value
is a ternary of two string literals — no pyast-parser gate — so Module 5's `ClassByNameCall`
finds an entry. Outside the pyast model `_ctor` is `None`, so the arm's own decline test

```
                if not (_ctor and isinstance(_lw, str)
                        and _lw.startswith(f"({_ctor} ")):
                    return "0"
```

returns the LITERAL `0` for the whole construction. False `ensures \result == 0` PROVES
(rc=0), emitted body `let name = ref (if (c <> 0) then 1556256700 else 2004353471) in 0`;
CPython returns 2 for both values of `c`. This is also a `witness-census` site (the census's
`expressions.py:17130`). The repair must make a DECLINE opaque (route #24's
`opaque_dynamic_call`), never `0`.

---

## THE DRAFT FENCE HAS A CARRIER ALREADY (gen #23, order 2) — #116 IS NOT CLOSED BY BATCH-2

Batch-2 keys the recognizer on a genuine `globals()` lookup helper. Carrier-rerun on that fence:
a module-level `_g["inc"] = dec` (a SUBSCRIPT store into the namespace — the fence counted NAME
targets only, the campaign's lesson 9 exactly) keeps `_N` qualified and `_N("inc")(3)` is still
`(inc 3)`: false `\result == 4` PROVES, CPython 2. Its root is route #118 (a rebinding of the
looked-up name is not consulted at all, even by a DIRECT call). Batch-2 closes the `Pick("inc")`
callable-class carrier, the fake-dict `_N`, and the ternary decline; the namespace-mutation
carrier stays open under #118.
