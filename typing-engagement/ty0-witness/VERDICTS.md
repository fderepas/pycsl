# TY0 Witness Verdicts — S7 (PyCSL front-end annotation behavior)

Witnesses run with: `source .venv/bin/activate && python3 src/pycsl/pycsl.py --keep-mlw --no-proof <witness>.py`
Memory model: default (`hoare`). Disposition key:
- **INTERPRETED** — the annotation lowers to a concrete WhyML type distinct from the unannotated default (`int`).
- **IGNORED** — annotation present in source but pycsl drops it silently: emitted WhyML signature is byte-identical to the unannotated baseline (`let f (x: int) : int`), no error raised.
- **REJECTED** — pycsl raises a parse/semantic error on the annotation form.

Baseline (no annotation): `def f(x): return x` → `let f (x: int) : int` (see `/tmp/opencode/t_base.py`).

---

### 1. Scalar annotations

#### 1a. `int`
- **Witness file:** s01_scalar_int.py
- **Source:** `def f(x: int) -> int`
- **Disposition:** IGNORED
- **Evidence:** Emitted `let f (x: int) : int` — byte-identical to the unannotated baseline. `int` is the default `int_type`, so the annotation carries no information at the WhyML layer. (The annotation IS captured into `return_annotation`/`symbol_table` as `"int"`, but the consumers' default branch already emits `int`, so no observable effect.)
- **S7 file:line cite:** `src/pycsl/frontend/Module5_IREmitter.py:1757-1801` (return_annotation capture), `:1693` (arg symbol_table capture); `src/pycsl/module6_whyml/functions.py:52` (default `int_type` fallback).

#### 1b. `bool`
- **Witness file:** s02_scalar_bool.py
- **Source:** `def f(x: bool) -> bool`
- **Disposition:** IGNORED  *(SURPRISE — see below)*
- **Evidence:** Emitted `let f (x: int) : int`. `bool` is not in any of the recognized-type branches in `_param_type_str` / `_compute_return_type` (no `bool → bool` mapping), so it falls through to the default `int`. pycsl models Python `bool` as `int` with no distinct type.
- **S7 file:line cite:** `src/pycsl/module6_whyml/functions.py:13-52` (`_param_type_str` has no `bool` arm), `:514-544` (`_compute_return_type` has no `bool` arm).

#### 1c. `float`
- **Witness file:** s03_scalar_float.py
- **Source:** `def f(x: float) -> float`
- **Disposition:** INTERPRETED
- **Evidence:** Emitted `let f (x: real) : real`. `float` annotation lowers to WhyML `real` (no-more-int Stage D).
- **S7 file:line cite:** `src/pycsl/module6_whyml/functions.py:38-40` (param), `:534-535` (return).

---

### 2. Known class names

#### 2a. `bytes`
- **Witness file:** s04_class_bytes.py
- **Source:** `def f(x: bytes) -> bytes`
- **Disposition:** INTERPRETED  *(SURPRISE — see below)*
- **Evidence:** Emitted `let f (x: array int) : array int`, BUT the generated WhyML does **not type-check** under the default `hoare` memory model:
  ```
  File "s04_class_bytes.mlw", line 6, characters 12-17: unbound type symbol 'array'
  ```
  The `array` WhyML theory is not imported in the preamble for this signature shape. So the annotation IS lowered to a concrete type, but the resulting module is broken in the default model. (Likely only sound under the `typed`/`store` memory models which import `array`, or in real programs that also emit array locals triggering the import.)
- **S7 file:line cite:** `src/pycsl/module6_whyml/functions.py:29-33` (param), `:522-524` (return); preamble import gap in `src/pycsl/module6_whyml/preamble.py`.

#### 2b. `str`
- **Witness file:** s05_class_str.py
- **Source:** `def f(x: str) -> str`
- **Disposition:** INTERPRETED
- **Evidence:** Emitted `let f (x: string) : string`. `str` annotation lowers to WhyML `string` (strings-plan Stage 1, value-semantic Why3 `string.String`).
- **S7 file:line cite:** `src/pycsl/module6_whyml/functions.py:34-37` (param), `:532-533` (return).

---

### 3. Container shapes

#### 3a. `list`
- **Witness file:** s06_container_list.py
- **Source:** `def f(x: list) -> list`
- **Disposition:** INTERPRETED
- **Evidence:** Emitted `let f (x: array int) : array int`. Bare `list` lowers to WhyML `array int`.
- **S7 file:line cite:** `src/pycsl/module6_whyml/functions.py:29` (param, `symtype in ("list", "bytes", "bytearray")`), `:522-524` (return).

#### 3b. `dict`
- **Witness file:** s07_container_dict.py
- **Source:** `def f(x: dict) -> dict`
- **Disposition:** INTERPRETED
- **Evidence:** Emitted `let f (x: map int (option int)) : map int (option int)`. Bare `dict` lowers to WhyML `map int (option int)`.
- **S7 file:line cite:** `src/pycsl/module6_whyml/functions.py:27-28` (param, `symtype in ("set", "dict", "frozenset")`), `:530-531` (return).

#### 3c. `tuple`
- **Witness file:** s08_container_tuple.py
- **Source:** `def f(x: tuple) -> tuple`
- **Disposition:** IGNORED  *(SURPRISE — see below)*
- **Evidence:** Emitted `let f (x: int) : int` — identical to baseline. `tuple` is not in any recognized-type branch; falls through to default `int`. (Subscripted `Tuple[int, int]` IS handled via the tuple-return refinement path in `_refine_tuple_return_type`, but the bare `tuple` annotation is not.)
- **S7 file:line cite:** `src/pycsl/module6_whyml/functions.py:13-52` (no `tuple` arm in `_param_type_str`), `:514-544` (no bare-`tuple` arm in `_compute_return_type`).

---

### 4. None return

#### 4. `-> None`
- **Witness file:** s09_none_return.py
- **Source:** `def f(x: int) -> None: return None`
- **Disposition:** IGNORED  *(SURPRISE — see below)*
- **Evidence:** Emitted `let f (x: int) : int` with body `0`. The `-> None` annotation is captured into `return_annotation == "None"` and IS consulted for `#@ lemma` ghost discipline (lemma → `unit`), but for a **non-lemma** function it has no effect on the WhyML return type, which stays `int` (and `return None` is emitted as `0`). So for regular functions, `-> None` does not produce a `unit`-typed WhyML function.
- **S7 file:line cite:** `src/pycsl/frontend/Module5_IREmitter.py:1761-1762` (captures `"None"` into `return_annotation`); `src/pycsl/module6_whyml/functions.py:521-544` (only `lemma` branch consults it for `unit`, `:556-559`); `src/pycsl/core_ir_semantic.py:763-765` (lemma ghost-discipline comment).

---

### 5. Stringized annotations (forward refs)

#### 5. `def f(x: "Foo") -> "Foo"` (Foo defined later)
- **Witness file:** s10_stringized_fwd.py
- **Source:** `def f(x: "Foo") -> "Foo"`
- **Disposition:** IGNORED
- **Evidence:** Emitted `let f (x: int) : int`. Stringized annotations are `ast.Constant` (str), which is handled for return only via `str(node.returns.value)` → `return_annotation = "Foo"` (a class name that no consumer recognizes, so falls through). For **parameters**, `_m5_get_type_name` only handles `ast.Name` and `ast.Subscript` — it has no `ast.Constant` arm, so `arg.annotation` of `"Foo"` returns `"Any"`, and `"Any"` falls through `_param_type_str` to default `int`. The annotation is silently dropped on both sides.
- **S7 file:line cite:** `src/pycsl/frontend/Module5_IREmitter.py:1607-1632` (`_m5_get_type_name` has no `ast.Constant` arm — stringized param annotations never reach `symbol_table` as a class name); `:1761-1762` (return_annotation captures the raw string `"Foo"`, but no Module6 arm matches it).

---

### 6. Forward-reference resolution order

#### 6a. Class defined AFTER the function
- **Witness file:** s12_fwd_before_def.py
- **Source:** `def f_before(x: Foo) -> Foo` with `class Foo` defined below.
- **Disposition:** IGNORED
- **Evidence:** Emitted `let f_before (x: int) : int`. `Foo` is captured into `symbol_table["x"] = "Foo"` and `return_annotation = "Foo"`, but `Foo` is not in `_record_types` / `_variant_types` (no `#@ datatype` / record decl), so `_param_type_str` falls through to default `int`. The forward position is irrelevant — pycsl does not resolve class-name annotations to record/variant types unless they are declared via PyCSL type directives. No error.

#### 6b. Class defined BEFORE the function
- **Witness file:** s11_fwd_after_def.py
- **Source:** `def f_after(x: Bar) -> Bar` with `class Bar` defined above.
- **Disposition:** IGNORED
- **Evidence:** Emitted `let f_after (x: int) : int`. Same as 6a: a bare Python `class Bar` (without `#@ datatype` / record annotation) is not registered in `_record_types`, so the `Bar` annotation has no effect. Position (before/after) makes no difference to pycsl.

#### 6c. UNDEFINED name
- **Witness file:** s13_fwd_undefined.py
- **Source:** `def f(x: "Baz") -> "Baz"` (stringized), `Baz` never defined.
- **Disposition:** IGNORED  *(SURPRISE — see below)*
- **Evidence:** Emitted `let f (x: int) : int`, L3-tc ✓. pycsl does **not** reject undefined names in annotations — neither the stringized form nor (by parity) the bare-name form. The annotation is silently dropped to default `int`. There is no name-resolution / forward-reference check on annotations at any pipeline stage.
- **S7 file:line cite:** No check exists — `_m5_get_type_name` (`Module5_IREmitter.py:1607-1632`) returns whatever `ast.Name.id` it sees without validating against any symbol table; `core_ir_semantic.py` has no annotation-name-resolution pass.

---

## SURPRISES (gap-doc notes — recorded, NOT fixed)

1. **`bool` is silently `int`** (s02). Assumption was that scalars are interpreted; `bool` is dropped without distinction. No `bool` arm in `_param_type_str` / `_compute_return_type`.
2. **`bytes` emits `array int` but the default-model preamble does not import `array`** (s04). The annotation is "interpreted" but produces a WhyML module that fails L3 type-check in isolation. Likely an unintended consequence of the `bytes → array int` mapping being added without a matching preamble import for the bare-`bytes`-only case.
3. **`tuple` annotation is silently `int`** (s08). Bare `tuple` has no recognized-type arm even though subscripted `Tuple[int, int]` is partially handled by the tuple-return refinement path. Asymmetric.
4. **`-> None` is IGNORED for non-lemma functions** (s09). Captured into `return_annotation` but only consulted by the `lemma` branch — a regular function with `-> None` still emits return type `int` and `return None` becomes `0`. So `-> None` does not actually constrain the WhyML return type outside ghost discipline.
5. **Undefined annotation names are NOT rejected** (s13). pycsl performs no name-resolution check on annotations — `x: "Baz"` with `Baz` never defined silently becomes `int`, exit 0. This contradicts the assumption that an UNDEFINED name would be REJECTED.
6. **Stringized param annotations are dropped at the front-end** (s10). `_m5_get_type_name` has no `ast.Constant` arm, so `x: "Foo"` records `arg_type = "Any"` for the parameter (return side does capture the string, but it then matches no Module6 arm). Asymmetric between param and return.

---

## Summary table

| # | Form | Source line | Disposition | WhyML emitted |
|---|------|-------------|-------------|---------------|
| 1a | scalar `int` | `def f(x: int) -> int` | IGNORED | `(x: int) : int` (= baseline) |
| 1b | scalar `bool` | `def f(x: bool) -> bool` | IGNORED | `(x: int) : int` |
| 1c | scalar `float` | `def f(x: float) -> float` | INTERPRETED | `(x: real) : real` |
| 2a | class `bytes` | `def f(x: bytes) -> bytes` | INTERPRETED (L3-tc ✗) | `(x: array int) : array int` |
| 2b | class `str` | `def f(x: str) -> str` | INTERPRETED | `(x: string) : string` |
| 3a | container `list` | `def f(x: list) -> list` | INTERPRETED | `(x: array int) : array int` |
| 3b | container `dict` | `def f(x: dict) -> dict` | INTERPRETED | `(x: map int (option int)) : map int (option int)` |
| 3c | container `tuple` | `def f(x: tuple) -> tuple` | IGNORED | `(x: int) : int` |
| 4 | `-> None` | `def f(x: int) -> None` | IGNORED | `(x: int) : int`, body `0` |
| 5 | stringized fwd-ref | `def f(x: "Foo") -> "Foo"` | IGNORED | `(x: int) : int` |
| 6a | bare name, class AFTER | `def f_before(x: Foo) -> Foo` | IGNORED | `(x: int) : int` |
| 6b | bare name, class BEFORE | `def f_after(x: Bar) -> Bar` | IGNORED | `(x: int) : int` |
| 6c | UNDEFINED name | `def f(x: "Baz") -> "Baz"` | IGNORED | `(x: int) : int` |

**No form was REJECTED.** Every annotation form pycsl does not specifically handle is silently dropped to the default `int` / `int`-typed body, with no diagnostic. Only `float`, `str`, `bytes`, `list`, `dict` (and the `set`/`frozenset` siblings not probed here) lower to a distinct concrete WhyML type.
