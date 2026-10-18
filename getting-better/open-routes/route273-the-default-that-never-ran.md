# OPEN ROUTE #273 — DEF-TIME EVALUATION OF NESTED `def` DEFAULTS, `lambda` DEFAULTS AND NESTED `class` BODIES IS DROPPED
**Status: REPAIRED (gen #36, 2026-10-18; opened the same day), Severity 1.** Red-team round 5; driver-reproduced at HEAD (v09 rc=0 CPython 5; v04 rc=0
CPython ZeroDivisionError). Witnesses `witnesses-r273/` (v02 diverging default, v04/v07 raising defaults, v05/v09/v12/v13
effectful defaults, v06 lambda default diverging, v08 class-body raise, v10 nested class call, v03 decorator).
Mechanism: nested def/class lifting (and lambda lowering) discards default expressions / class-body statements, which Python
evaluates when the def/class statement runs; their effects/raises/divergence vanish. #269's vanished-call scan doesn't walk them.
Repair: evaluate default expressions/class-body statements at the definition point (or refuse any non-literal default /
non-trivial nested class body).

## REPAIR (2026-10-18, branch r273 off 5a307a33)

**Rule** (inline in `pycsl.py::_run_pipeline`, beside route #269's vanished-call scan; mirror twin `\trusted`;
no Module 1-6 change). AST-level, fail-closed, `PYCSL-SEM-DEF-TIME-EVALUATION`. Inside a LOWERED function (not
`\trusted`/`\abstract`, together with everything nested in it) every nested `def`/`async def`/`lambda`/`class`
is checked for what CPython evaluates when the statement (expression, for `lambda`) runs:
- every default (`defaults`, `kw_defaults`) must be a literal, a bare name, a signed numeric literal or a
  tuple/list/set/dict display of those;
- every decorator of a nested def/class must be a (dotted) name (a call decorator is refused; a plain-name
  decorator was already refused by Module 3's binding check, v03);
- every annotation (params, `*args`/`**kw`, return) and class base/keyword must be type-shaped (names,
  attributes, subscripts, tuples/lists, string literals, `|`);
- a nested class body may hold only defs, nested classes, `pass`, docstrings and `name = <literal>` /
  `name: <type> = <literal>` bindings.
None of those can call, raise (beyond an unbound name's NameError, route #264's ground) or loop, so nothing the
lifting drops was ever evaluated with effect — which is also why #269's vanished-call scan needs no extension to
these positions: no call can remain there. Module-level defs/classes (import time) are outside the rule.

| witness (corpus) | shape | 5a307a33 | after |
|---|---|---|---|
| 2960 (v04) | `def inner(y=10 // x)`, `x == 0`, `no_exception \all` | PROVED | refused |
| 2961 (v02) | `def inner(x=spin())`, `spin` `\diverges`, caller terminating | PROVED | refused |
| 2962 (v06) | `lambda x=spin(): x` | PROVED | refused |
| 2963 (v09) | `def inner(y=push(xs))`, `push` writes `xs[0] = 5` | PROVED | refused |
| 2964 (v08) | `class K: v = 10 // x` under `no_exception \all` | PROVED | refused |
| 2965 (v10) | `class K: v = push(xs)` | PROVED | refused |
| 2966 (v13) | method: `def inner(y=self.push())` | PROVED | refused |
| 2967 | controls: literal / name / `-1` defaults, `lambda a=None`, class of literal attributes + method | PASS | PASS |

CPython ground truth in each `__main__` (ZeroDivisionError / "does not terminate" / 5 / 3). `witnesses-r273/`:
v02/v04/v06/v08/v09/v10/v12/v13 PROVED at base and are refused after; v03 was already refused (Module 3, a
plain-name decorator on a nested def); v05 (`count` global not nameable in a contract) and v07 (`raises
ValueError` without `when`) are front-end errors at base and after — not witnesses.

**Census + blast radius (CPython-`ast` prototype of the predicate, before landing).** pycsl-reference 0,
self-annotate mirror 0, pycsl_lib 1 (`json/encoder.py::iterencode`, default `self.allow_nan` — already refused
for another reason), python-reference 1 (0078, class body `x = Desc()` — already refused at base: no `.mlw`
in either sweep). Measured after: corpus root 0 MOVED / 0 GONE / 0 APPEARED, pyref 2186/2186 0/0/0; mirror
emission unchanged by this half.

RESIDUALS: module-level def defaults/decorators and module-level class bodies run at IMPORT time and are not
part of any verified function's evaluation (outside this rule; the default value itself never reaches the
model of a call that omits the argument — not probed here). A literal display default (`[]`) is admitted
here; a mutable default is refused separately by `core_ir_semantic` (shared-object default).
- **NEW UNSOUND SHAPE, found after the gates (OPEN, not closed here):** a BARE-NAME default is admitted by this
  rule (it cannot raise/write/diverge), but its VALUE is bound at def time while the model reads the name at CALL
  time: `def inner(z: int = x): return z; x = 5; return inner()` PROVED `\result == 5` after this repair (CPython:
  the caller's original `x`, 0 for `f(0)`). Reproducer: scratchpad `r273/repro/name_default_def_time_value.py`.
  Candidate fix: admit only literal defaults (census of bare-name defaults in nested defs owed first).
