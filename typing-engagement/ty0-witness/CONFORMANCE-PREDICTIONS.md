# TY0 Witness Conformance Predictions

Produced by the typing-conformance-agent from the S7 transcription sections of
the three reference docs (concrete-syntax §11, static-semantics §11,
translational §T.Ann) **alone**, without reading `VERDICTS.md` or any
`src/pycsl/` source. Predictions were then checked by running pycsl on each
witness driver:

```
source .venv/bin/activate && python3 src/pycsl/pycsl.py --keep-mlw --no-proof <witness>.py
```

The emitted WhyML signature was extracted from the generated `.mlw` file.
Dispositions and WhyML types are predicted from the §T.Ann.2 lowering table
and the §11 / §T.Ann narrative; the `bytes` L3-type-check gap is predicted
from §T.Ann.5.

---

### s01_scalar_int.py
- **Prediction (from spec):** IGNORED — `let f (x: int) : int` (§T.Ann.2 row 1a: `int` is the default `int_type`, so the annotation carries no info; byte-identical to the unannotated baseline)
- **Actual (from run):** IGNORED — `let f (x: int) : int` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

### s02_scalar_bool.py
- **Prediction (from spec):** IGNORED — `let f (x: int) : int` (§T.Ann.2 row 1b / §T.Ann.4: no `bool → bool` arm in `_param_type_str` / `_compute_return_type`; falls through to default `int`)
- **Actual (from run):** IGNORED — `let f (x: int) : int` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

### s03_scalar_float.py
- **Prediction (from spec):** INTERPRETED — `let f (x: real) : real` (§T.Ann.2 row 1c / §T.Ann.3: `float → real`)
- **Actual (from run):** INTERPRETED — `let f (x: real) : real` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

### s04_class_bytes.py
- **Prediction (from spec):** INTERPRETED (L3-tc ✗ — §T.Ann.5 gap) — `let f (x: array int) : array int` (§T.Ann.2 row 2a: `bytes` lowers to `array int`, but the default-model preamble does not import `use array.Array` for a bare-`bytes`-only signature, so L3 type-check fails with `unbound type symbol 'array'`)
- **Actual (from run):** INTERPRETED (L3-tc ✗) — `let f (x: array int) : array int`; L3-tc failed: `unbound type symbol 'array'`
- **Match:** YES

### s05_class_str.py
- **Prediction (from spec):** INTERPRETED — `let f (x: string) : string` (§T.Ann.2 row 2b / §T.Ann.3: `str → string`)
- **Actual (from run):** INTERPRETED — `let f (x: string) : string` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

### s06_container_list.py
- **Prediction (from spec):** INTERPRETED — `let f (x: array int) : array int` (§T.Ann.2 row 3a / §T.Ann.3: bare `list` lowers to `array int` via the `list`/`bytes`/`bytearray` arm)
- **Actual (from run):** INTERPRETED — `let f (x: array int) : array int` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

### s07_container_dict.py
- **Prediction (from spec):** INTERPRETED — `let f (x: map int (option int)) : map int (option int)` (§T.Ann.2 row 3b / §T.Ann.3: `dict → map int (option int)` via the `set`/`dict`/`frozenset` arm)
- **Actual (from run):** INTERPRETED — `let f (x: map int (option int)) : map int (option int)` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

### s08_container_tuple.py
- **Prediction (from spec):** IGNORED — `let f (x: int) : int` (§T.Ann.2 row 3c / §T.Ann.4: no bare-`tuple` arm; falls through to default `int`. Subscripted `Tuple[…]` is handled by a separate refinement path, but the bare form is not.)
- **Actual (from run):** IGNORED — `let f (x: int) : int` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

### s09_none_return.py
- **Prediction (from spec):** IGNORED — `let f (x: int) : int` with body `0` (§T.Ann.2 row 4 / §T.Ann.4 / static-semantics §11.2: `return_annotation == "None"` is captured but only consulted by the `#@ lemma` branch for `unit`; for a non-lemma function the WhyML return type stays `int`, and `return None` lowers to `0`)
- **Actual (from run):** IGNORED — `let f (x: int) : int` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

### s10_stringized_fwd.py
- **Prediction (from spec):** IGNORED — `let f (x: int) : int` (§T.Ann.2 row 5 / §T.Ann.4 / static-semantics §11.3: parameter-side `_m5_get_type_name` has no `ast.Constant` arm → `"Any"` → default `int`; return-side raw string `"Foo"` is captured but no Module 6 arm matches → default `int`. Asymmetric.)
- **Actual (from run):** IGNORED — `let f (x: int) : int` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

### s11_fwd_after_def.py
- **Prediction (from spec):** IGNORED — `let f_after (x: int) : int` (§T.Ann.2 row 6b: a bare Python `class Bar` without `#@ datatype` / record annotation is not registered in `_record_types`; position before/after the function makes no difference — forward-reference resolution is not implemented, GT5 gap)
- **Actual (from run):** IGNORED — `let f_after (x: int) : int` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

### s12_fwd_before_def.py
- **Prediction (from spec):** IGNORED — `let f_before (x: int) : int` (§T.Ann.2 row 6a / static-semantics §11.1 GT5 gap: `Foo` is captured into `symbol_table["x"] = "Foo"` and `return_annotation = "Foo"`, but `Foo` is not in `_record_types` / `_variant_types`; forward position is irrelevant)
- **Actual (from run):** IGNORED — `let f_before (x: int) : int` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

### s13_fwd_undefined.py
- **Prediction (from spec):** IGNORED — `let f (x: int) : int` (§T.Ann.2 row 6c / §T.Ann.4 / static-semantics §11.1 GT5 gap: no name-resolution / forward-reference check on annotations at any pipeline stage; `"Baz"` is silently accepted and lowered to `int`, exit code 0)
- **Actual (from run):** IGNORED — `let f (x: int) : int` (L1 ✓ L2 ✓ L3-tc ✓)
- **Match:** YES

---

## Summary

- **Total witnesses:** 13
- **Matches:** 13
- **Mismatches:** 0

The S7 transcription in the three reference docs is **unambiguous** for all 13
TY0 witness forms: a reader predicting from the §T.Ann.2 lowering table
(plus §T.Ann.5 for the `bytes` L3-tc gap, §11.1/§11.3 of the static-semantics
reference for the GT5 forward-reference gap and the stringized-annotation
asymmetry, and §11.2 for the `bool` / `tuple` / `-> None` no-effect cases)
arrives at the correct disposition and WhyML type for every witness.

No gap doc is required: every disposition (INTERPRETED vs. IGNORED) and every
emitted WhyML type predicted from the written spec matched the actual pycsl
run, including the `bytes` L3-type-check failure (`unbound type symbol
'array'`) which §T.Ann.5 calls out explicitly.
