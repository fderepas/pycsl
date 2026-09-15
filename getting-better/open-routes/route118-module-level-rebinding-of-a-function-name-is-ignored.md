# ROUTE #118 — a MODULE-LEVEL REBINDING of a function name (`inc = dec`) is ignored: every
# later call `inc(...)` is modelled against the ORIGINAL `def inc`

**Status: CLOSED AND FULLY GATED by gen #23 (2026-09-15, batch 3)** — see THE REPAIR AS LANDED at the bottom. Original finding preserved below.
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


---

# THE REPAIR AS LANDED — gen #23 batch 3 (2026-09-15)

Routes #109 and #118 landed together in ONE battery (commit recorded in `driver-progress.log`).
Every verdict PREDICTED before it ran: cheap legs identical to battery-2 (metric 459/484/25/0 ·
trusted-raises 13/62 · type-only 53/0 · dropped-mutation 0/51/9/0 · sync 887) · emission
BYTE-INERT vs the battery-2 tree over pycsl-reference, python-reference and all 53 mirrors (zb 0),
so no mirror proof is owed · suite 3450/3468, the SAME 18 failures, ZERO XPASS · planes 34/34 `ok` COUNTED.

**What landed.** A front-end REFUSAL `PYCSL-IR-FUNCTION-NAME-REBOUND` in `pycsl.py::_run_pipeline`
(the choke point that already raises): one pass per SCOPE (the module and every class body),
over every child node except nested def/class/lambda bodies, keyed on the NAME being bound —
Name Store/Del, import alias, except-as, match capture — plus `global <defname>` anywhere and any
store through a `globals()`-bound name or `globals()[...]`.

**It took three cuts, and each miss is logged as a probe:** (1) placed in `Module5.visit_Module`
it moved `check-trusted-raises-honesty` 62 -> 65 (three mirror stubs share the name) and two mirror
emissions — relocated; (2) it enumerated module-level statement KINDS and a class-body `m = n`
walked past it; (3) it still enumerated statement kinds and a module-level walrus `if (inc :=
dec):` walked past it. The final cut keys on the path being written, not the statement shape —
the campaign's lesson 9, which this generation cited and then violated twice in one hour.

**Witnesses.** 1321 (module `inc = dec`), 1322 (#116's `_g["inc"] = dec` carrier), 1323
(class-body `m = n`), 1324 (walrus) — all XFAIL by refusal. Census: ZERO sites in all trees
(byte-inert). Siblings: duplicate `def` FAIL-CLOSED (last def wins, as in Python); function-as-
value probes VACUOUS on the pre-existing "Symbol X is already defined" error.
