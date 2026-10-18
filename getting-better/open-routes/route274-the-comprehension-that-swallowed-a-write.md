# OPEN ROUTE #274 — WRITE EFFECTS OF CALLS INSIDE COMPREHENSIONS / GENERATOR EXPRESSIONS VANISH
**Status: REPAIRED (gen #36, 2026-10-18; opened the same day), Severity 1.** Red-team round 5; driver-reproduced at HEAD (y10/y11 rc=0; CPython 5).
Witnesses `witnesses-r274/` (genexp first iterable, sum(genexp), listcomp, dictcomp, setcomp). `push(c)` with
`assigns c.v` inside a comprehension lowers to `list_comp 0` etc.; #269 refuses only raising/precondition callees and
models diverging ones. Repair: a call with a non-empty frame (any `assigns`/writes) inside an opaque comprehension must be
refused (or its frame havocked at the comprehension).

## REPAIR (2026-10-18, branch r273 off 5a307a33)

**Rule** (inline in `pycsl.py::_run_pipeline`, an extension of route #269's R3 vanished-call scan; mirror twin
`\trusted`), `PYCSL-SEM-VANISHED-CALL-EFFECT` (new message: "... which WRITES ..."). A callee has a FRAME if it
declares an `assigns` other than `\nothing`, or (frame undeclared, body lowered) its body writes a field /
element / slice, deletes an element, or calls a collection mutator (`IRScanner._MUTATING_METHODS`) on a base
that is not a FRESH LOCAL (a non-parameter, non-`self` name bound only by `Assign`s of a literal display or
comprehension) — closed transitively over undeclared-frame callers. A call inside a `ListComp`/`SetComp`/
`DictComp`/`GenExp`/`Lambda` IR node (the eager first iterable included: it is a child of the node) to a
frame-carrying callee, or to a receiver mutator (`out.append(y)`), is refused unless the function's OWN emitted
blocks (itself and its `<name>__*` walkers) apply the callee AT LEAST AS MANY TIMES as its IR calls it. Unlike a
raise/precondition (#269), one visible application elsewhere does NOT excuse it: each call is one more write
(2975). A callee whose every emitted spelling is a `val` WITHOUT `writes` has no modelled effect to lose (its
visible application is pure to Why3 as well — the stub's own frame, not this lowering's). A receiver mutator
has no countable spelling: always refused in such a position.

| witness (corpus) | shape | 5a307a33 | after |
|---|---|---|---|
| 2970 (y11) | `ys = [push(c) for y in xs]`, `push` `assigns c.v` | PROVED | refused |
| 2971 (y09) | `(y for y in range(push(c)))` — eager first iterable | PROVED | refused |
| 2972 (y10) | `sum(push(c) for y in xs)` | PROVED | refused |
| 2973 (e08) | `{y: push(c) for y in xs}` | PROVED | refused |
| 2974 (e09) | `{push(c) for y in xs}` | PROVED | refused |
| 2975 | `push(c); [push(c) for y in [1, 2]]` claims `c.v == 1` (CPython 3) | PROVED | refused |
| 2976 | `[out.append(y) for y in xs]` claims `len(out) == 0` (CPython 1) | PROVED | refused |
| 2977 | undeclared-frame `relay(c)` -> `push(c)` in a listcomp | PROVED | refused |
| 2978 | controls: `assigns \nothing` / write-free callee in comprehensions, `xs.count(y)`, a direct `push(c)` | PASS | PASS |

All five `witnesses-r274/` files PROVED at base and are refused after.

**Census + blast radius (measured on the first, stricter draft).** Corpus root/pyref: 0 MOVED / 0 GONE. Mirror:
the strict draft (no visibility excuse, any local write = frame) GONE'd `frontend/Module5_IREmitter` and
`module6_whyml/functions`. Module 5's `_csl_call_expr`/`_csl_mktuple` call `self._csl_to_ir` inside a
comprehension that the bespoke lowering emits CONCRETELY (a `let rec _cc_<k>` loop applying it once per element) —
modelled, hence the application-count test. `functions.rename` (nested, frame undeclared) writes only its fresh
local `new: Dict = {}` — hence the fresh-local refinement. `functions._build_param_list` built its `args_str` with
`" ".join(self._param_type_str(...) for arg in args)`: the generator lowered to `list_comp_refine_string` and the
stub application `self__param_type_str_6` (`writes { _pyobj_state }`) VANISHED — a genuine instance. Repaired at
the SOURCE, live and mirror verbatim: an explicit loop identical in shape to the method branch above it
(behaviour-identical; corpus root/pyref 0 MOVED). Mirror after: 53/53 emitted, 1 MOVED
(`module6_whyml__functions`: the loop replaces `list_comp_refine_string`), `--type-only` clean;
`--fun functionemissionmixin___build_param_list` PROVED; whole-file proof OWED (big file).

RESIDUALS: the application count is a count, not a matching — a lowering that emits one IR call twice could
mask a second, vanished one (none observed). A callee emitted only as `val`s without `writes` (e.g. a
`\trusted` mirror method whose declared `assigns` is not emitted) is excused here; its frame honesty belongs to
the stub (check-trusted-frame-honesty). A write to a `#@ shared` module global by an undeclared-frame callee is
not detected by the body scan (globals are otherwise refused, see the `global` refusal).
