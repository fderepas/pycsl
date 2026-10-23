# ROUTE #134 — route #116's `F("name")(args)` recognizer takes `G = globals()` as bound once from the TOP-LEVEL statements only

**Status: CLOSED AND FULLY GATED by gen #25 (2026-09-15), battery-A (cheap legs, emission vs HEAD byte-inert in all three, suite 3503/3521 same 18 0 XPASS, planes 34/34 — every leg predicted and hit).**
**Severity: SEV-1. Second-order (the carrier is route #116's own justification check, `Module5_IREmitter._m116_assigned`).**

## MEASURED at HEAD `65237fdb`
`_g = globals()`, `if True: _g = {"inc": dec}`, `#@ \trusted def pick(name): return _g[name]`, and
`g() = pick("inc")(3)` with `\result == 4`: PROVES (emission `(inc 3)`); CPython 2. Without `\trusted` on `pick` the
same lowering of `g` happens and the file is refused only by a Why3 type error in `pick`'s own body.
Same premise, fenced: `collect_module_globals` (`G = Counter(3); if True: G = Counter(5)` — emission ignores the
rebinding, but no entry-state fact reaches a function).

## REPAIR (Module3_Weaver.process, #132's rebinding arm)
The single-binding candidates now also include a module name bound to `globals()`/`vars()`/`locals()` or to an
instance of a module-defined class: bound again anywhere in module scope and read, it is refused. `globals` itself
rebound is #131; `pick` rebound in a compound statement is #122. Witness 1377. Census: sweep byte-inert.
