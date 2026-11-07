# ROUTE #115 — an expression Module 5 does not recognise becomes `UnknownPyExpr`, and Module 6
# lowers `UnknownPyExpr` to the DEFINITE VALUE `0`

**Status: CLOSED AND FULLY GATED by gen #23 (2026-09-15)** — see THE REPAIR AS LANDED at the bottom. Original finding preserved below.
**Severity: SEV-1. First-order.** `(lambda y: y + 1)(x)` is ordinary Python.

## PROVENANCE

New generator **`witness-census`** (gen #23), the campaign's hard-won rule turned into a sweep:

>>> **A COMPLETENESS FALLBACK THAT SUPPLIES A WITNESS VALUE IS A SOUNDNESS ROUTE WAITING TO
>>> HAPPEN.** Enumerate every emitter site that RETURNS A DEFINITE CONSTANT (`"0"`, the empty
>>> map, `"true"`) for a construct it does not model, and ask whether it is reachable in value
>>> position.

`grep 'return "0"$|= "0"$|return "(const (None|return "true"$|return "false"$'` over
`src/pycsl/module6_whyml/` gives 57 sites. This is the first one run.

## THE MECHANISM

`src/pycsl/frontend/Module5_IREmitter.py` `_py_expr_to_ir`: two catch-alls return
`{"type": "UnknownPyExpr"}` — any `ast` expression type absent from `_PY_EXPR_HANDLERS`
(`Await`, `Yield`, ...), and a `Call` whose `func` is neither a `Name` nor an `Attribute`
(nor the one `getattr(self, local)(...)` dispatch shape).

`src/pycsl/module6_whyml/expressions.py`:

```
        if isinstance(node, UnknownPyExprExpr):
            return "0"
...
        if t in ("UnknownPyExpr", "GenExp"):
            # genexp-erasure-wall R2a parity: ... lowering to the scalar `0` ...
            return "0"
```

No refusal and no warning anywhere between them.

## MEASURED at baseline worktree `21d5029e` (source == HEAD `6f36d67f`)

`u_lamcall.py`:

```python
#@ requires x >= 0
#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    return (lambda y: y + 1)(x)
```

`[+] Verification SUCCESS` (rc=0). The whole emitted body is `0`. **CPython: f(0) = 1,
f(5) = 6** (run).

VACUOUS sibling (logged): `fs: List[Callable[[int], int]] = [inc]; return fs[0](x)` — the
erasure fired (body `... in 0`) but the run died on an unrelated Why3 error ("Symbol inc is
already defined") before any goal ran. It measured nothing about provability.

## REPAIR SKETCH (census the population FIRST)

`UnknownPyExpr` in VALUE position must REFUSE (fail-closed) or lower to an UNCONSTRAINED value
(`any_int ()`-style havoc), never to `0`. The `GenExp` arm's comment records that emitter code
in the mirror (`sum(ord(c) for c in name)`) currently depends on the scalar `0` shape, so the
population must be censused over all four trees before choosing refusal vs havoc.

---

## SECOND CARRIER — THE VERY SHAPE ROUTE #24's REPAIR SAYS IT COVERS (order 2)

Route #24 (corpus 0996) replaced a computed-callee erasure with `(opaque_dynamic_call 0)`,
and its comment claims the arm is reached for "a call whose CALLEE is not a plain name ...
`type(self)(...)`, `self.fns[0]()`, a computed constructor". `type(self)()` does reach it —
Module 5 builds a `ClassByNameCall` node (callee `Call(Name, [Name|Subscript])`), which Module 6
resolves or sends to the opaque arm. (Corrected after reading `_py_expr_call`: an earlier draft
of this line said "Call-of-Call"; the same reading found route #116.) A **Subscript** or **Lambda** callee does not: Module 5's
`_py_expr_call` returns `UnknownPyExpr` for it, and Module 6 lowers that to `0` long before
the opaque arm could see it.

`u_subcall2.py`:

```python
#@ requires len(fs) > 0
#@ ensures \result == 0
#@ assigns \nothing
def f(fs: List[Callable[[int], int]], x: int) -> int:
    return fs[0](x)
```

`[+] Verification SUCCESS` rc=0, whole body `0`; CPython `f([lambda y: y + 1], 0)` = 1.
**A REPAIR COMMENT THAT NAMES A SHAPE IS A CLAIM ABOUT A COLLECTOR — COUNT WHAT REACHES IT.**
`bin/check-computed-rhs-erasure.py`'s census ("exactly ONE site tree-wide") counted the
emitted `:= 0` shape and so could not see a `0` that is a whole function body.

AST census (all four trees) of the Module 5 catch-all population: `Call` with a `Call` callee
167 (mostly the mirror, handled by the Call-of-Call arm), `Yield` 80, `YieldFrom` 12,
`Await` 4 (python-reference 0098/0152), `Lambda`/`Subscript` callee **0**. The lambda and
subscript carriers are therefore corpus-inert to repair; `Yield`/`Await` need the emission
census before choosing refusal vs havoc.

---

# THE REPAIR AS LANDED — gen #23 (2026-09-15)

Landed with routes #111–#117 as ONE combined battery (commit recorded in `driver-progress.log`).
Every verdict was PREDICTED in the progress log before it ran:
metric 459/484/25/0 · doc-coherency rc=0 · mirror sync 887 verbatim · mirror-check same 3
pre-existing drifts · trusted-raises 13/62 · trusted-reasons 459↔459 · type-only 53, 0
ill-typed · dropped-mutation 0/51/9/0 · byte-diff pycsl-ref 22 MOVED / GONE only 0996 (an
expected-FAIL witness now refused) · python-ref 6 MOVED · mirror emission 7 MOVED, every hunk
read and attributed · suite 3444/3462, the SAME 18 failures, ZERO XPASS · whole-file proofs of
all 7 moved mirrors SUCCESS, 0 bad (statements 17630, expressions 21347, stmt_control_flow
12284, pure_ast 3372, functions 1199, Module5_IREmitter 2109, preamble 216 Valid) · planes
34/34 `ok` COUNTED (after narrowing `check-singleton-constant-lowering`'s baseline: the split arm orphaned two entries whose justifications #115/#116 had just refuted — removed — and renamed the GenExp half's key; constant arms 14 -> 12; emission re-verified byte-identical).

**What landed.** `expressions.py`: `UnknownPyExpr` (typed and dict arms) lowers to `(any int)`,
never `0` (`GenExp` deliberately untouched). Both carriers refused: `(lambda y: y + 1)(x)` and
`fs[0](x)`. Collateral read in the sweep: discarded expression statements `let _ = 0` became
`let _ = (any int)` (1031, python-reference 0061/0141/0175, pure_ast); `type(self)(...)` in
pure_ast became `(any int)`; corpus 0996 (route #24's witness, expected-FAIL) is now REFUSED by
the pre-existing ERASED-TRUTHINESS check, whose message was corrected. Corpus 1313, 1314 (XFAIL).
