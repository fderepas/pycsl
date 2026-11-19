# OPEN ROUTE #473 — A LOCAL EMPTY LIST PASSED TO A CALLEE IS THE 1024-ELEMENT PLACEHOLDER (discharges `len(c) >= 1`)
**Status: REPAIRED (executor e473, driver run #3; see REPAIR below), Severity 1.** Found by executor lv5 (driver run #3, 2026-10-29) while building a conversion control;
driver-reproduced on main a9eac4a08 (`scratchpad/rt38/driver-repro-r473.txt`): `c = []` and `c: List[int] = []` then
`g(c)` with `g` requiring `len(c) >= 1` PROVE (rc=0 Verification SUCCESS); CPython IndexError. (`c = list()` already FAILS.)
Witnesses `witnesses-r473/` (2): `r473_local_empty_list_to_callee.py`, `r473b_annotated_empty_list.py`.

```
#473 `c = []; return g(c)` is emitted `let c = (Array.make 1024 0) in g c`: the empty-list PLACEHOLDER (routes #195 /
     #196 / #225 family; #195 / #196 closed only the DIRECT `f([])` argument form). Inside the function `len(c)` is tracked
     locally (a control `n = len(c)` with `ensures \result == 1024` does not prove), but the ARRAY handed across the call is
     the 1024-element placeholder, so the callee's length precondition is discharged against 1024.
  REPAIR (proposed, structural): an empty list literal must never be materialised as a fixed-size placeholder where it
  can reach a callee / a field / a return / a container: either emit a length-0 array (or the resizable-list model) or
  refuse passing such a value across a boundary; census every `Array.make 1024` placeholder site.
```

## REPAIR (executor e473, driver run #3, 2026-10-29, off main 1f3aa3081)

**Faithful value, no refusal, no mirror move.** Inline in `_run_pipeline` (`src/pycsl/pycsl.py`, block "ROUTE #473",
after #159 / gen #31 and before #269; the mirror twin of `_run_pipeline` is `\trusted`, no new def in a mirrored file, no
axiom). An empty list literal is emitted as the genuinely EMPTY array `(Array.make 0 0)` -- #196's own value for the
direct argument -- wherever the IR attributes the placeholder text to it:

- a function whose IR body holds an empty `ArrayLit` and NO producer of a real 1024-element list (`[v] * 1024`,
  `bytearray(1024)` / `bytes(1024)`, a constructor whose record declaration carries `1024`, an unknown capitalised
  callee): every unquoted `(Array.make 1024 0)` of its body;
- a function holding both: each `let X = [ref] (Array.make 1024 0)` / `X := (Array.make 1024 0)` of a local every IR
  assignment of which is `[]`; and the remaining placeholders too when every producer is the whole value of an
  assignment to a local whose assignments are all real lists AND the text names exactly that many placeholders by such
  locals (consistency check). A constructor's record default is never attributable.

Kept as it was: a binding with an `X_len` sidecar (gen #31's capacity), a local with a length-changing surface
(`append`/`extend`/`insert`/`remove`/`pop`/`clear`, `AugAssign`), a real-list local, string literals
(`"(Array.make 1024 0)"` inside the mirrors' own code). 0 is the faithful length and the least one, so no obligation
gets easier; CPython's `\result == 0` now proves (7391, 7393, 7395: FAILED at base).

CENSUS (`getting-better/systematic-soundness-r3/e473/placeholder-census.tsv`, probes `witnesses-r473/probes/`, 54
files proved at base and candidate): the placeholder escaped through a CALL ARGUMENT (direct, alias, sibling method /
R167 assertion, keyword, on a branch, bound result, in a function that also holds a real 1024 list, a callee's length
`ensures`) and through the function's OWN `len` for `list([])` -- 11 probes PROVED at base, all FAIL now. FIELD STORE
(local and direct), RETURN in a tuple / on a branch, CONTAINER, IFEXP: FAILED at base (L3-tc `iter_length` over an
array field; opaque `materialize`; erased `any int`); now carry the faithful value. YIELD, CLOSURE, DEFAULT, GLOBAL,
callee append, local in-place mutators: REFUSED upstream (unchanged).

Witnesses 7380-7389, 7396 (all 11 PROVED at base 1f3aa3081, all FAIL now); controls 7391-7395 PROVED now (7392 a real
1024-element list, 7394 the local size fold: PROVED at base too; 7391 / 7393 / 7395 are CPython's own answers, FAILED
at base because the callee saw 1024).

## RESIDUALS
- A direct `[]` (not a local) in a function that also constructs a record with a 1024-element default, or holds a real
  1024-list producer in a direct position, keeps the placeholder: every such position measured fail-closed at base
  (field store: L3-tc; direct call argument: #196; final return: gen #31), but it is not the faithful value.
- `xs[0:0] = [1]` on an empty local fails by #157's width assertion (CPython succeeds): completeness gap, base too.
- A field's length (`len(o.xs)` after `o.xs = c`) is an L3 type error (`val iter_length (x: int)` over an array field):
  a pre-existing fail-closed gap; controls cannot exercise the field position until it is modelled.
