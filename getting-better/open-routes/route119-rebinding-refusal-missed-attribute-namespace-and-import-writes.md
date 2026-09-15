# ROUTE #119 — route #118's rebinding refusal (landed 6c75839a) missed every rebinding that is
# not a NAME binding in the file being verified

**Status: FOUND (gen #23, 2026-09-15), ORDER 2 — the carrier is gen #23's own landed repair.**
**Severity: SEV-1.** Every carrier PROVES a contract of the original def while CPython runs the
replacement.

## PROVENANCE

Generator `carrier-rerun`, run on route #118's refusal about an hour after it was marked CLOSED.
The campaign rule, again: **a carrier surviving a repair is a second route, not a failed repair.**

## CARRIERS, all measured at HEAD `c01ef653` (#118 landed), each false claim PROVED, CPython 2

| carrier | why #118 missed it |
|---|---|
| `C.m = C.n` at module level, then `c.m()` | an ATTRIBUTE store, not a Name binding |
| `vars()["inc"] = dec` | #118 knew `globals()` only |
| `locals()["inc"] = dec` (module level: IS globals) | same |
| `setattr(sys.modules[__name__], "inc", dec)` | a call, not a binding |
| `type.__setattr__(C, "m", C.n)` | the dunder spelling of setattr |
| `inc = dec` inside an IMPORTED module (`from rebindlib import inc`) | the refusal sat in `pycsl._run_pipeline`; imported dependencies are ingested by `frontend/ir_resolve.py` with their own Module 1-3-5 and never pass through it |

VACUOUS siblings (the function-as-value "Symbol X is already defined" fence): `c.m = c.n` on an
instance, `self.m = fn` through a constructor parameter (the `json.JSONEncoder` idiom — `pycsl_lib/
json/encoder.py:147` has exactly this shape), `inc.__code__ = dec.__code__` in a patch function.

## REPAIR (drafted on the main tree, gated by battery-4)

The guard moved into `Module3_Weaver.process` — the one step BOTH pipelines share, which already
raises (so `check-trusted-raises-honesty` and the mirror emissions stay put) — and grew to:
(1) name bindings per scope (as #118), constant `exec("...")` bodies included; (2) `global
<def name>`; (3) any subscript write or mutating method call through `globals()`/`vars()`/
`locals()`, a name bound to one of them, or any `.__dict__`; (4) an attribute write whose
attribute is a def/class/method name on any receiver but `self`; (5) `setattr`/`delattr` and
`X.__setattr__`/`__delattr__` (receiver not `self`/`super()`) with a def/class/method name or a
non-literal attribute; (6) ANY attribute write on an object that IS a module-level def or class,
scope-aware (a parameter or local of the same name inside a function is not the def — pure_ast's
`node.lineno = ...` is exactly that case).

WATCH (not refused, fenced today only by the function-as-value error): `self.<method> = fn` and
`super().__setattr__(name, v)` instance-level shadowing.
