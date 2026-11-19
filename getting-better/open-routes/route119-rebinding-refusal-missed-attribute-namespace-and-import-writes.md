# ROUTE #119 — route #118's rebinding refusal (landed 6c75839a) missed every rebinding that is
# not a NAME binding in the file being verified

**Status: CLOSED AND FULLY GATED by gen #23 (2026-09-15) — battery-4b (de890255) + battery-5.** See THE REPAIR AS LANDED at the bottom.
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
| `exec("inc = dec")` at module level | the refusal never looked inside the string |

AND, run against gen #23's OWN #119 DRAFT the same hour (each PROVED at HEAD and on the draft):

| carrier | why the draft missed it |
|---|---|
| `import plainlib; plainlib.inc = plainlib.dec; plainlib.inc(3)` | the draft keyed on names defined in THIS file; the receiver is an IMPORT |
| `from plainlib import K; K.m = K.n; K().m()` | same |
| `importlib.import_module("plainlib").inc = ...` | the receiver is a CALL, not a name |

(`type(c).m = C.n` was already refused at HEAD by the in-place field-mutation refusal — FAIL-CLOSED.)

VACUOUS siblings (the function-as-value "Symbol X is already defined" fence): `c.m = c.n` on an
instance, `self.m = fn` through a constructor parameter (the `json.JSONEncoder` idiom — `pycsl_lib/
json/encoder.py:147` has exactly this shape), `inc.__code__ = dec.__code__` in a patch function.

## REPAIR (drafted on the main tree, gated by battery-4)

The guard moved into `Module3_Weaver.process` — the one step BOTH pipelines share, which already
raises (so `check-trusted-raises-honesty` and the mirror emissions stay put) — and grew to:
(1) name bindings per scope (as #118); (2) `global
<def name>`; (3) any subscript write or mutating method call through `globals()`/`vars()`/
`locals()`, a name bound to one of them, or any `.__dict__`; (4) an attribute write whose
attribute is a def/class/method name on any receiver but `self`; (5) `setattr`/`delattr` and
`X.__setattr__`/`__delattr__` (receiver not `self`/`super()`) with a def/class/method name, a
literal on an imported object, or a non-literal attribute on a class-or-module-like receiver
(a non-literal `setattr(out, f.name, v)` on a plain local is LIVE Module3_Weaver's own idiom —
refusing it refused two MIRROR files; narrowed); (6) ANY attribute write whose receiver CHAIN
roots at a module-level def/class or an IMPORTED object (scope-aware: a parameter or local of
the same name is not the object — pure_ast's `node.lineno = ...`), or contains a call not rooted
at `self`; (7) a constant `exec("...")` whose text names a def/class/imported object (token
check; parsing the string inside `process` needed a `try/except SyntaxError`, which added an
`exception SyntaxError` to two mirror emissions — measured, removed).

WATCH (not refused, fenced today only by the function-as-value error): `self.<method> = fn` and
`super().__setattr__(name, v)` instance-level shadowing.


---

# THE REPAIR AS LANDED — gen #23 (2026-09-15), TWO BATTERIES

**Battery-4b** (commit de890255, with route #120): the rebinding guard moved from
`pycsl._run_pipeline` into `Module3_Weaver.process` with rules (1)-(7) above. Cheap legs identical ·
emission byte-inert except the predicted `--expect-gone python-reference 0076` · suite 3460/3478,
same 18 failures, 0 XPASS · planes 34/34. Witnesses 1325-1332.

**Battery-5** (INSTANCE-LEVEL shadowing, found by carrier-rerun on the battery-4b tree):
  (8) front end — a `self.<m>` store, or `setattr(self, "<m>")` / `self.__setattr__` /
      `super().__setattr__` / `object.__setattr__(self, ...)`, where `m` is a method of the class
      or its in-module bases; a NON-literal attribute is refused when the class has a non-dunder
      method OR any base not defined in the module (its methods are unknowable here);
  (9) IR level, `PYCSL-WHYML-METHOD-SHADOWED` in `_handle_dotted_call` (already raised) — a call
      that resolves to a METHOD `m` of the receiver's class while the receiver record carries a
      FIELD `m` (e.g. a dataclass field default, a store in `__init__`, over an IMPORTED base the
      front end cannot see) or the program STORES an attribute `m` anywhere (a store outside
      `__init__` creates no field).
Measured carriers closed by battery-5, each PROVING at HEAD c01ef653: `self.m = abs` (1335);
`self.m = int` over an imported base (1336); a late store in `install()` (1338); a non-literal
`setattr(self, name, value)` over an imported base (1339); `object.__setattr__(self, ...)`
(probe); a dataclass field default over an imported base (probe). Battery-5: cheap legs identical ·
emission byte-inert vs battery-4b in all three directions · suite 3465/3483, same 18 failures,
0 XPASS · planes 34/34.

**Remaining WATCH (fenced only incidentally, logged):** a non-literal `setattr(obj, name, int)` on
a plain local instance through a helper — refused today by the typing of the setattr value slot.
