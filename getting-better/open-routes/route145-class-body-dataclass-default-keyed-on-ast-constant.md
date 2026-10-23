# ROUTE #145 — the CLASS-BODY `@dataclass` default collector keyed on `isinstance(value, ast.Constant)`

**Status: CLOSED AND FULLY GATED by gen #28 (2026-09-16), battery A.**
Severity 1. Generator: **carrier-rerun on GEN #27's OWN route-#139 repair** (order 2).
Witnesses `1428 1429 1430 1431` (XFAIL), `1439 1440` (PASS).

## The defect

Gen #27's route #139 taught `field_defaults` to fold a unary-minus literal — in the
`__init__`-BODY collector. **The CLASS-BODY collector, the one every `@dataclass` uses
(`src/pycsl/frontend/Module5_IREmitter.py:3398`), was left on the raw test**

```python
if (stmt.value is not None and isinstance(stmt.value, ast.Constant)
        and isinstance(stmt.value.value, (int, float))):
    field_defaults[stmt.target.id] = int(stmt.value.value)
```

and **Python's parser does not fold**. A field with no `field_defaults` entry falls to
`_field_default`'s **definite** literal `0`.

## The four measured shapes (each PROVING at `2887ba44`, CPython contradicting)

  - `xfld: int = -7` — `UnaryOp` → proved `0`; CPython `-7`. (1428)
  - `xfld: int = 2 + 3` — `BinOp` → proved `0`; CPython `5`. (1429)
  - `xfld: int = field(default=5)` — `Call` → proved `0`; CPython `5`. (1430)
  - `xfld: int = field(default_factory=five)` — carrier-rerun on the repair's own first
    draft: a factory carries no `default=` keyword, so the unwrap yields None and a SCALAR
    field kept the definite `0`; CPython `5`. (1431)

## The repair — three arms, and the ORDER is load-bearing

  1. `field(default=<x>)` is UNWRAPPED first: it is the dataclass spelling of a default and
     the wrapper hides every shape below it. A `default_factory` on a COLLECTION field is
     left exactly as it was (the typed default IS what `dict`/`set`/`list` produce, and all
     13 corpus sites are of that form); on a SCALAR field it is marked UNKNOWN.
  2. the numeric-`ast.Constant` path is kept VERBATIM (so `True` / `2.5` behave exactly as
     before), then `_const_int_value` folds the unary-minus literal.
  3. anything else name-free-but-COMPUTED is marked UNKNOWN (`(any int)` via route #83's
     `init_unknown_fields`), **never given a witness value** — a completeness fix that
     supplies a witness is a soundness route waiting to happen. String/None constants and
     collection literals/factory calls are EXCLUDED from that arm because they are carried
     by their own channels (#51's `field_str_defaults`, #85's map literals, #87's list
     literals).

Honest cost, measured and accepted: 1429's TRUE twin `\result == 5` is refused too — a
`BinOp` default is now unknown rather than wrong.

## Census (byte-inert)

Over the two corpora, the 53 mirrors and `pycsl_lib`: **48** numeric class-body defaults
(arm 2, unchanged), **161** non-numeric `ast.Constant` and **14** collection literals /
factory calls (all excluded by construction — the 13 `default_factory` sites are all
`Set[int]` / `Dict[...]` / `List[...]`, i.e. `_NONSCALAR`, which Module 6's `(any int)`
substitution skips), and **ZERO** UnaryOp / BinOp / Name. Both new arms have live
population 0. None of the 38 frozen conformance IR goldens declares a `@dataclass`.

## FAIL-CLOSED alongside (logged, not routes)

A NamedTuple class-body default carries the same `isinstance(ast.Constant)` rule, but the
N7 arity gate refuses the zero-argument construction outright (`class Pee(NamedTuple):
xfld: int = -7` → PIPELINE ERROR), so that path fails closed.
