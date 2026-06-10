# Convergence spec — 10-1732, iteration N=1 (Gaps 2 & 3)

Implementation spec for the two remaining gaps in `10-1732-gap.md`. Gap 1 (`Return_str`) is
already FIXED + committed (89b3f55; demand-driver `0697`… see note) — **out of scope here**.

Gaps **2** and **3** share one missing piece: the **callee/parameter faithful-TYPE is not
threaded into the expression emitter** (`expressions.py`). This spec specifies that shared
threading once, then the per-gap edit that consumes it.

> SPEC PHASE ONLY. No `src/pycsl/` edits are made by this document. The two builder methods
> `_build_method_param_whyml_types_by_name` and `_build_method_return_annotation_map` already
> exist in `functions.py:974-1006` (prior uncommitted scaffolding, +34 lines, currently
> unwired/unconsumed). This spec wires and consumes them.

---

## Shared type-threading (the spine)

The emitter already holds a family of callee-signature maps, all built in
`Module6_WhyMLTranspiler.transpile()` at `Module6_WhyMLTranspiler.py:426-433` from
`funcs_for_maps` (the module functions + mixin pseudo-funcs):

| map | builder | value space | line |
|-----|---------|-------------|------|
| `_module_method_return_types` | `_build_method_return_type_map` (functions.py:574) | **WhyML** type (`"string"`, `"array int"`, `"int"`, …) | 426 |
| `_module_method_param_types` | `_build_method_param_types_map` (functions.py:955) | list of WhyML types, by position | 427 |
| `_module_method_formal_params` | inline dict-comp | ordered formal-param name list | 430 |
| `_module_method_param_defaults` | inline dict-comp | `{param-name → default IR node}` | 432 |

**Decision: no NEW table is required for Gap 2 or Gap 3** — the existing WhyML-typed maps
suffice, but two by-name/by-callee helpers (already written, unwired) make the consumption
clean and avoid disturbing the byte output of the existing maps:

- Gap 2 needs callee-name → return-type. `_module_method_return_types` already supplies a WhyML
  return type; `"string"` is exactly the value `_symtype_to_whyml("str")` and the
  `return_annotation == "str"` path produce (functions.py:876-877, functions.py:370-371). So
  **Gap 2 can read `_module_method_return_types` directly** (value `"string"`). The pre-written
  `_build_method_return_annotation_map` (Python-type valued) is an alternative; this spec uses
  the **WhyML** map already in `transpile()` to add ZERO new wiring for Gap 2.
- Gap 3 needs callee-name → {param-name → WhyML param type}. The positional
  `_module_method_param_types` plus the ordered `_module_method_formal_params` already give this
  by zipping, but the pre-written `_build_method_param_whyml_types_by_name` (functions.py:974)
  returns the by-name dict directly and is keyed exactly how the default-fill loop iterates
  (`for nm in formal_params[len(args):]`). **Wire it** as `self._module_method_param_whyml_types`.

### Wiring edit (the only `transpile()` change)
At `Module6_WhyMLTranspiler.py` after line 433 (next to the sibling maps), add:

```python
self._module_method_param_whyml_types = \
    self._build_method_param_whyml_types_by_name(funcs_for_maps)
```

Byte-additivity: this only populates a new attribute; nothing reads it except the Gap-3 edit,
whose own trigger is additive (below). No existing map changes.

---

## Gap 2 — `len(<call returning str>)` → `str_length_op`

**Planned edit.** `_is_string_expr` (`expressions.py:334`). Add a `Call` case. The IR node the
emitter sees for a call is `{"type": "Call", "func": <name str>, "args": [...]}` — confirmed at
`_handle_call_expr` (`expressions.py:1017-1019`, `func_name = expr["func"]`). There is no
separate `CallExpr` node — the dispatch key is the string `"Call"`.

Insert before the final `return False` (expressions.py:354):

```python
if t == "Call":
    fn = ir.get("func", "")
    return getattr(self, "_module_method_return_types", {}).get(fn) == "string"
```

**Trigger condition.** Fires only when the argument is a `Call` node whose callee name resolves
in `_module_method_return_types` to the WhyML type `"string"`. That value is produced exactly
when the callee is a module function declared `-> str` (functions.py:370-371) or whose body
returns a string (find_return_type→`"string"`). Any other callee (int/list/unknown) is absent
or non-`"string"` → returns `False` → unchanged opaque/`iter_length` path.

**Why byte-additive.** `_is_string_expr` previously returned `False` for every `Call` node (no
case existed). The new case only ever flips `False → True` for `len`-of-a-str-returning-call;
every other call still returns `False`. The downstream effect in `_handle_len_call`
(expressions.py:616-628) is: such a call now routes to `String.length` (spec) /
`str_length_op` (body) instead of falling to `iter_length` (expressions.py:643) or the
`X_len` fallback (expressions.py:645). No corpus driver today writes `len(g(s))` with `g`
returning `str` (the strmod workaround bound the result to a local first), so no existing
emission changes — confirmed by the 60-driver/os/conformance byte gates below.

---

## Gap 3 — omitted defaulted non-`int` param filled at its faithful type

**Planned edit.** The call-arg default-fill loop, `expressions.py:1088-1099`. Today an omitted
trailing param is filled by lowering its default IR (`self._expr_to_whyml(defaults[nm], …)`,
expressions.py:1092). A `None` default has IR `{"type": "None"}` (Module5_IREmitter.py:363,
780, 785) which lowers to int `0` — applied verbatim to a `string` param → type mismatch.

Reuse the type-aware dispatch pattern from `expr_ghost_spec_ops.py:74`
(`default = '""' if ptype == "str" else "0"`), but keyed on the param's **WhyML** type via the
newly-wired by-name map. Replace the fill in the `if nm in defaults:` branch
(expressions.py:1091-1093) with:

```python
if nm in defaults:
    dflt_ir = defaults[nm]
    pwt = getattr(self, "_module_method_param_whyml_types", {}).get(
        func_name, {}).get(nm, "int")
    if dflt_ir.get("type") == "None" and pwt != "int":
        # A `None` default on a non-int param is the int-model sentinel `0`;
        # fill the param's FAITHFUL zero instead (no-more-int).
        filled = {"string": '""', "real": "0.0"}.get(pwt, "0")
    else:
        filled = self._expr_to_whyml(dflt_ir, local_refs, invariant_ctx, subst)
    args = args + [filled]
```

**Trigger condition.** Fires only when (a) the call passes fewer args than the callee arity AND
(b) the omitted param's default IR is `{"type": "None"}` AND (c) the param's WhyML type is
non-`int` (`string`/`real`). A REAL typed default — `sep: str = " "` → default IR
`{"type":"String","value":" "}`, or a numeric default — does NOT have `type == "None"`, so it
falls to the unchanged `else` branch and lowers to its real value (`" "`). An omitted `int`
param with a `None` default keeps `0` (condition (c) fails). So a genuine string default is
preserved while only the `None`-on-`str`/`real` case is corrected.

**Why byte-additive.** The only behavioural change is `0 → ""` (resp. `0.0`) for an omitted
`None`-defaulted non-`int` param. Today that case emits ill-typed WhyML (the gap), so no
PROVING corpus driver exercises it (strmod worked around it by passing `sep` explicitly). All
existing fills are either int params (unchanged) or real typed defaults (unchanged `else`
branch). Map types: only `"string"` and `"real"` are handled; any future non-int param type
not in the dict falls back to `"0"` (status-quo, flagged as a follow-on, not a regression).

---

## Test drivers

Next free numbers: `0697` and `0698` (corpus tops out at `0696`).

> Note: `0696.py` is the Gap-1 `Return_str` demand-driver (already committed). If the Gap-1
> commit (89b3f55) instead reserved `0697`, shift these to the next two free numbers; verify
> with `ls test-suite/corpus/pycsl-reference/ | sort | tail` at implementation time.

### `0697.py` — Gap 2 (`len` of a str-returning call → `str_length_op`)
A local helper `g(s: str) -> str` returning a string, and a caller that takes `len(g(s))`
*directly* (no intermediate local — the exact shape the strmod workaround avoided):

```python
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def g(s: str) -> str:
    return s

#@ requires \str_length(s) >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def caller(s: str) -> int:
    return len(g(s))          # MUST route to str_length_op (not iter_length)
```

EXPECT: PROVES. `\result >= 0` discharges from the `result = String.length s` ensures carried
by `str_length_op` (expressions.py:625-627). The docstring must state it is the Gap-2
demand-driver and that before the fix `len(g(s))` routed to the opaque `iter_length`.

### `0698.py` — Gap 3 (omitted str default fills `""`)
A helper with a defaulted `str` param, called with the arg omitted:

```python
# pycsl-flags: --memory-model hoare
_ = 0
#@ requires \str_length(s) >= 0
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def h(s: str, sep: str = None) -> str:
    return s                  # body ignores sep; the point is the call-site fill type

#@ requires \str_length(s) >= 0
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def use(s: str) -> str:
    return h(s)               # sep omitted -> filled "" (string), NOT int 0
```

EXPECT: PROVES (type-checks; before the fix `h s 0` applied int `0` to a `string` param →
mismatch). Docstring states it is the Gap-3 demand-driver. (If `h` must be a `\trusted`
imported stub to faithfully mirror the `capwords` case, an `import`-based variant is acceptable
— see RISK R3 on imported-stub return/param-type availability; the local-function form above is
the minimal, self-contained probe and is preferred for the gate.)

---

## Gate plan

Run via `bin/run-reference-tests.sh`; the explicit gates:

1. **doc-coherency** (`bin/doc-coherency.py --check`) — GREEN. No new `#@` directive is added,
   so no `annotations.md`/README/reference parity work is needed. (Confirm still green; the
   change is emitter-internal.)
2. **Conformance 38/38** (`bin/run-conformance.sh`) — unchanged.
3. **60-driver byte-diff** (`bin/extraction-byte-diff.sh` / `.py`) — **IDENTICAL**. Both edits
   are additive: Gap 2 flips `_is_string_expr` only for `len`-of-a-str-returning-`Call`; Gap 3
   changes the fill only for an omitted `None`-defaulted non-`int` param. Neither shape occurs
   in the existing 60 drivers (the strmod model worked around both). Expect a clean byte-diff.
4. **os byte-identical** — `os` has no `len(<str-returning call>)` and no omitted non-int
   defaults at call sites; assert the emitted WhyML for the `os` model is unchanged.
5. **strmod still PROVES** — `pure_lib/strmod/` (the source of these gaps) must still prove; its
   workarounds remain valid (the fix is strictly more permissive, never more restrictive).
6. **New drivers `0697`/`0698` PROVE** — added to `test-suite/corpus/pycsl-reference/`; both
   discharge under the reference run.

Acceptance: gates 1-5 unchanged/green AND gate 6 proves. If any of 3/4 shows a diff, the trigger
mis-fired (see RISKS) — do not widen the condition to absorb it; narrow the trigger instead.

---

## RISKS / open questions (for coordination-agent judgment before approval)

- **R1 — Gap-2 Call case mis-fire.** The new `_is_string_expr` `Call` arm keys on
  `_module_method_return_types[fn] == "string"`. A module function whose body *returns* a string
  but is annotated otherwise, OR a same-named shadow, could be mis-typed. Mitigation: the map
  value `"string"` is only produced for a `-> str` annotation or a string-returning body
  (functions.py:370-371, 574-595), which is precisely the intended trigger. Lookup MISS (callee
  not a module function — e.g. a builtin or unresolved name) returns `None != "string"` → safe
  `False`. **Open question for you:** is keying on the WhyML map (value `"string"`) preferable to
  the pre-written Python-`return_annotation` map (value `"str"`)? The WhyML map adds zero wiring
  and already lives in `transpile()`; the annotation map would also catch a `-> str` that some
  path normalized differently. I recommend the WhyML map (fewer moving parts). Your call.

- **R2 — Imported-stub return type for Gap 2.** The motivating case (`len(capwords(s))`) is an
  **imported `\trusted` stub**. Whether `_module_method_return_types` is populated for an
  *imported* function (vs a local one) depends on whether imported stubs are included in
  `funcs_for_maps` at `Module6_WhyMLTranspiler.py:425`. The `0697` driver uses a LOCAL function
  to keep the gate self-contained, so the core fix is provable regardless. **Open question:** do
  you want the spec to also REQUIRE an imported-stub variant in the corpus (proving the original
  `capwords` shape end-to-end)? That needs confirming the import path feeds the return-type map;
  it may surface a second, smaller threading gap. I left it as an optional `0698` variant note.

- **R3 — Gap-3 param-type coverage.** The fill dict handles `"string"→""` and `"real"→"0.0"`
  only; any other non-int WhyML param type (record/variant/`array int`/map) with a `None`
  default + omission falls back to int `0` (status quo, still ill-typed for those — but no worse
  than today, and no corpus case exercises it). **Open question:** acceptable to scope this
  iteration to `str`/`real` (the no-more-int scalars the gap names), deferring record/array
  default-fill to a follow-on? I recommend yes.

- **R4 — `None` is the only sentinel handled.** Gap 3 triggers on default IR `{"type":"None"}`.
  A non-`None` int-literal default on a `str` param (e.g. an authoring error `sep: str = 0`)
  would still fill `0`. That is a malformed program; PyCSL is not obligated to repair it, and the
  type-checker will reject it. Flagging only — no action proposed.

- **R5 — Driver numbering.** `0696` is taken; `0697`/`0698` assumed free. Re-confirm at
  implementation time (the Gap-1 commit may already hold `0697`).

---

## APPROVAL — coordination agent (day 10, 18:5x)

**Status: APPROVED, with one binding requirement (R2).** Risk rulings:

- **R1 — APPROVED as recommended.** Key Gap 2 on the existing WhyML `_module_method_return_types`
  (value `"string"`); zero new wiring, already in `transpile()`. Do NOT add the Python-annotation map.
- **R2 — APPROVED WITH BINDING REQUIREMENT: the fix MUST cover the IMPORTED case.** The whole reason
  this gap exists is the strmod scenario `len(capwords(s))` / `capwords(s)` where `capwords` is an
  **imported** `\trusted` stub; the formal driver `pure_lib_test/formal_strmod.py` will call it imported.
  A local-only fix does NOT unblock strmod's natural re-prove, so it is insufficient. The implementation
  MUST: (a) verify `_module_method_return_types` and `_module_method_param_whyml_types` are populated for
  IMPORTED functions (whether imported stubs enter `funcs_for_maps` at Module6:425); (b) if they are not,
  thread the imported callee's return/param types so the fix applies; (c) add an IMPORTED-stub driver
  (in addition to the local `0697`/`0698`) proving the real `capwords`-shaped `len(<imported str call>)`
  and an omitted str-default on an imported function. If threading imports turns out to be a substantial
  SEPARATE gap, do NOT ship a local-only fix silently — surface it as a new gap (write
  `DD-HHMM-convergence-gap-2.md`) and report, so the loop continues honestly.
- **R3 — APPROVED as recommended.** Scope this iteration to `str`/`real` faithful zeros; record/array/map
  `None`-default fill stays `0` (no worse than today) — note it as a follow-on in the fill code.
- **R4 — noted, no action** (a non-`None` int default on a str param is a malformed program; the
  type-checker rejecting it is correct).
- **R5 — re-confirm `0697`/`0698` free at implementation time** (`ls … | sort | tail`).

Gate discipline unchanged: 60-driver/os byte-IDENTICAL, conformance 38/38, strmod still proves, the new
drivers prove, doc-coherency green. The imported-case requirement (R2) is the acceptance bar — proceed to
implementation.
