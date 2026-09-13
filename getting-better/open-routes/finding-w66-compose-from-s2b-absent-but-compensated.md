# FINDING w66 — `compose_from`'s "provider-refines-dependency" obligation (S2b) has NO
# IMPLEMENTATION, and it does not need one: flatten-and-re-verify discharges it

**CERTIFIED BOUNDARY. MEASURED. NOT A ROUTE.** Recorded so the next generation does not spend
the round I just spent — the census flagged this GUARD-NOT-FOUND and it looked like the best
remaining candidate.

## THE DEFERRAL, DOUBLED

`Module2_Parser` says `#@ compose_from` *"synthesizes the composition obligations (unique
provider per dependency, **provider-refines-dependency**, **init-hook**) checked by the Module4
pass (S2)"*. Module 4 is dropped; the successor is `ir_resolve.apply_composition`, whose own
docstring **defers again**: *"The provider ⊑ dependency refinement goal **is S2b**."*

`grep -rn "S2b" src/pycsl/` returns **exactly one line — that comment**. There is no
implementation. Same for `init-hook`: `grep -rn "init-hook\|init_hook"` returns only the
Module2_Parser docstring. So the cross-reference chain is
*parser → "Module4 S2" → apply_composition → "S2b" → nothing*, which is the #92 shape squared.

## WHY IT IS NOT A ROUTE — MEASURED

Probe: a mixin that **assumes a strong dependency** composed with a provider that guarantees
something **strictly weaker and in fact false**.

```python
#@ mixin
class CoreEmit:
    #@ provides emit
    #@ ensures \result == 0          # the real provider ALWAYS returns 0
    def emit(self, x: int) -> int: return 0

#@ mixin
class MapOps:
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result >= 10       # the mixin ASSUMES this
    #@ provides handle_get
    #@ ensures \result >= 10
    def handle_get(self, k: int) -> int: return self.emit(k)

#@ compose_from CoreEmit, MapOps
class Facade:
    #@ ensures \result >= 10
    def run(self, k: int) -> int: return self.handle_get(k)
```

| | verdict |
|---|---|
| **0549** (the flagship, provider genuinely refines) | **PROVES** — control, the algebra works |
| the exploit above | **FAILS** |

And — per the rule that a failing control is a claim about the control until you read *which*
goal failed — the unproven goal is **`facade__handle_get'vc`, the POSTCONDITION of the
FLATTENED clone**, not something incidental.

**THAT IS THE WHOLE ANSWER.** `apply_composition` deep-copies each provider-carrying mixin
method into the composer (`clone["name"] = f"{c}__{tail}"`) and the clone is re-emitted and
**re-verified against the CONCRETE provider**. So the refinement obligation is discharged
*implicitly, by re-verification*, and a provider that fails to refine its declared dependency
makes the composed file fail. S2b is unimplemented and unnecessary — for this shape.

>>> **A MISSING CHECK IS NOT A HOLE IF A DIFFERENT MECHANISM HAPPENS TO COVER THE SAME GROUND.
>>> BUT "HAPPENS TO" IS THE OPERATIVE PHRASE: NOTHING NAMES THE DEPENDENCY.** The compensating
>>> mechanism is a *flattening optimisation*, not a soundness check, and no comment anywhere
>>> says "S2b is unnecessary because clones are re-verified". Anyone who makes flattening lazier
>>> — clone only what the composer actually calls, or re-use the mixin's isolation proof instead
>>> of re-verifying — **re-opens a severity-1 route while believing they made an optimisation.**

## THE RESIDUE THE CENSUS NAMED — CHECKED, AND UNREACHABLE

The census flagged that `if not f.get("provides"): continue` skips non-provider mixin methods
from flattening, so they are never re-verified. **They are also never reachable**: not being
flattened means `self.<tail>` in the composer does not resolve to them, so the facade cannot
call them. The mixin's own isolation copy (`<mixin>__<tail>`) still exists and still proves its
postcondition under the *abstract* dependency — but nothing in the composed program consumes
that copy, and the measured file FAILED on the clone regardless.

## REOPENING CONDITIONS

1. **Any change that makes flattening lazier or reuses the mixin's isolation proof** instead of
   re-verifying the clone against the concrete provider. This is the likely one, because it
   looks like a pure performance win.
2. **A path that makes a non-`provides` mixin method callable from the composer.**
3. `init-hook` is still **GUARD-NOT-FOUND and UNPROBED** — I measured the refinement obligation,
   not that one. It is not covered by this finding.
