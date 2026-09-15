# ROUTE #118 — a MODULE-LEVEL REBINDING of a function name (`inc = dec`) is ignored: every
# later call `inc(...)` is modelled against the ORIGINAL `def inc`

**Status: FOUND, REPRODUCED (gen #23, 2026-09-15). NOT REPAIRED.**
**Severity: SEV-1. First-order.** `inc = dec` is ordinary Python.

## PROVENANCE

Generator `carrier-rerun`, on gen #23's OWN draft fence for route #116 (the class-by-name
recognizer may resolve `_N("inc")` only when `_N` is a genuine `globals()` lookup). The question
"can the looked-up NAME be rebound?" needed a control that rebinds the name with no factory at
all — and the control was the sharper route.

## MEASURED at baseline worktree `21d5029e` (source == HEAD) and on the batch-2 draft

`direct_rebind.py`:

```python
#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1

#@ ensures \result == y - 1
#@ assigns \nothing
def dec(y: int) -> int:
    return y - 1

inc = dec

#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
```

`[+] Verification SUCCESS` rc=0 in both trees; emitted body `(inc 3)`. **CPython returns 2.**

Siblings (logged): two `def inc` — FAIL-CLOSED, the model agrees the LAST def wins;
`global inc; inc = dec` inside a function — VACUOUS (the rebinding is invisible in the emission,
but the run died on the unrelated "Symbol dec is already defined").

## SECOND-ORDER CARRIER — route #116's draft fence (logged, order 2)

`_g = globals(); def _N(name): return _g[name]; _g["inc"] = dec` — a SUBSCRIPT store into the
namespace, not a rebinding — still qualifies `_N`, and `_N("inc")(3)` is emitted `(inc 3)`:
false `\result == 4` PROVES, CPython 2. Same root: the name -> def binding is assumed immutable.

## POPULATION (AST census, all four trees, gen #23)

Module-level rebinding of a def/class name: **0**. Module-level subscript store through a name:
**0**. `globals()` calls: 2 (pure_ast's `_g = globals()` and corpus 1318). `global <defname>`:
**0**. Duplicate defs: 1 (mirror `ir_resolve._contract_referenced_var_names`, last-def-wins
agrees with Python). A REFUSAL repair is therefore byte-inert by census.

## REPAIR SKETCH

Refuse (fail-closed, in the front end) a module whose top level rebinds a def/class name
(`Assign`/`AugAssign`/`AnnAssign`/`import ... as` onto it), declares `global <defname>` in any
function, or stores through a `globals()`-bound name or `globals()[...]` — or model the rebinding
faithfully. The #116 fence then inherits it for free.
