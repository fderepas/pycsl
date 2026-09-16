# ROUTE #146 — a KEYWORD-ONLY `@dataclass` field stayed in the POSITIONAL binding list

**Status: CLOSED AND FULLY GATED by gen #28 (2026-09-16), battery A.**
Severity 1. Generator: carrier-rerun (on gen #28's own route-#144 repair).
Witnesses `1432` (XFAIL), `1441 1442` (PASS).

## The defect

Python 3.10 added THREE spellings that make a `@dataclass` field keyword-only, and all
three change the ORDER of the synthesized `__init__`'s POSITIONAL parameters:

  - `@dataclass(kw_only=True)` — every field is keyword-only;
  - `x: int = field(kw_only=True)` — that one field is (and `kw_only=False` forces a field
    back to positional, overriding both the class-level flag and the sentinel);
  - `_: KW_ONLY` — a SENTINEL pseudo-field: it declares no field and every member after it
    is keyword-only.

`_is_dataclass_decorated` recognized `@dataclass(...)` and **ignored its keywords**, and
the synthesized `init_params` took every `AnnAssign` in declaration order.

## The measured shape (PROVING at `2887ba44`, CPython contradicting)

```python
@dataclass
class Pee:
    xfld: int = field(kw_only=True, default=0)
    yfld: int = 0

Pee(5, xfld=1).yfld     #@ ensures \result == 0   <-- PROVED; CPython gives 5
```

`yfld` is Python's FIRST positional parameter. The model made it the second, bound `xfld`
from the `5`, then let the explicit `xfld=1` keyword OVERWRITE that binding, and left
`yfld` on its default — a definite `0` for a field Python sets to 5.

## The repair

The dataclass branch of `_collect_init_construction` splits the field list into a
POSITIONAL half and a KEYWORD-ONLY half, honouring all three spellings, and the keyword-only
names leave on **route #82's existing channel** (`init_kwonly_params` /
`init_kwonly_defaults`), which binds BY NAME ONLY and can never take a positional argument.
`apply_inheritance` carries `dataclass_kwonly_fields` separately from `dataclass_fields`,
so a subclass inherits a keyword-only field AS keyword-only — without that it would be
absent from `bindable` and an explicit keyword naming it would be SILENTLY IGNORED.

## Census (byte-inert)

`kw_only` / `KW_ONLY` over the two corpora, the 53 mirrors and `pycsl_lib`: **ONE file**,
`src/pycsl_lib/dc/__init__.py` — and that is the STUB DECLARING `field(...)`, not a use.

## FAIL-CLOSED alongside (logged, not routes)

  - `@dataclass(kw_only=True)` called with ALL keywords was already faithful and still is
    (witness 1442, the positive control, passes on BOTH sides).
  - the `KW_ONLY` sentinel shape was REFUSED at HEAD and is now faithful (`Pee(1, yfld=7)
    .xfld == 1` proves; CPython 1).
