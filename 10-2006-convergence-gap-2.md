# Convergence gap report — iteration 2 (strmod full-API propagation)

**Loop:** `config/skills/pycsl-stdlib-coverage` — "The Convergence Principle" / Step 5.
**Trigger:** rewriting `pure_lib_test/formal_strmod.py` to propagate the English
spec (`test-suite/library_reference/string.rst`) across the WHOLE strmod public
API (was: 2 of 10 symbols; now: all 10 represented). Expanding from the two
module functions to the six **class-method** symbols surfaced a real tool gap:
the faithful per-method promise cannot be propagated to a driver that
**constructs an instance and calls the method**.

**Status of the formal test:** RUNS and every asserted theorem PROVES Valid
(`--memory-model hoare`, Alt-Ergo → Z3). All 10 API symbols are REPRESENTED; the
six class-method symbols are propagated *as strongly as the tool currently
allows* (four via a semantically-identical module-level twin the model exports;
two — `set_template` read-back, `is_valid` 0/1, `format` — in their strongest
instance-free form), each clearly commented GAP-LIMITED. No theorem was weakened
to a vacuous `True`. The model `pure_lib/strmod/__init__.py` is UNCHANGED and
still proves standalone (its own per-method `ensures` discharge — the gap is in
*propagation to a constructing driver*, not in the model).

This is the known **"method ensures don't propagate to a constructing driver"**
gap (MEMORY: `pycsl_method_call_contract_gap`) — here it splits into two
precise, separately-reproducible facets, both blocking strmod's classes.

---

## Gap 2a — a str-typed record field's default lowers to the int literal `0`

**API symbols blocked:** `Template.set_template`, `Template.is_valid`,
`Template.substitute`, `Template.safe_substitute` (every method requires first
constructing a `Template()`).

**Symptom:** constructing a `Template()` (whose only field is
`self.template: str = ""`) emits a Why3 record literal with the str field
initialised to the **int** literal `0`, which fails Why3 typechecking:

```
let t : template = { template = 0 }          (* module-global form *)
let t = { template = 0 } in ...              (* local form *)
```
```
This expression has type int, but is expected to have type string
```

**Minimal reproducer** (`--memory-model hoare`):
```python
# pycsl-flags: --memory-model hoare
from pure_lib.strmod import Template
t = Template()
#@ ensures \result == n
#@ assigns t.template
def drv(n: str) -> str:
    t.set_template(n)
    return t.template
```
(The method body itself inlines correctly — `t.template <- n; t.template` — and
read-back `result = n` is provable; ONLY the constructor literal's str-field
default is ill-typed. So fixing the default is the whole fix.)

**Root cause (two cooperating sites):**

1. `src/pycsl/frontend/Module5_IREmitter.py` `_collect_class_fields`,
   lines ~1403-1409: the `AnnAssign` default-value capture stores a default into
   `field_defaults` only for **int/float constants** (`int(stmt.value.value)`)
   and array sizes. A `str` constant default (`""`) hits the
   `elif stmt.value is not None:` branch, finds no array size, and stores
   **nothing** — so `field_defaults` has no entry for `template`.

2. `src/pycsl/module6_whyml/expressions.py` `_call_record_constructor`
   `_field_default`, lines 1538-1543:
   ```python
   ft = field_types.get(fn, "int")
   if ft in ("list", "array"):  return f"(Array.make {…} 0)"
   if ft in ("dict", "set", "frozenset"):  return "(const (None: option int))"
   return f"{rec_info['defaults'].get(fn, 0)}"   # <-- str falls here -> 0
   ```
   There is **no `str` (nor `float`/`bool`) branch**. A `str` field with no
   captured default returns the fallback int `0` — an ill-typed `string`-field
   value. (`field_types` already correctly tags the field `"str"` via
   `_field_type_from_annotation`, so the type information needed for the fix is
   present.)

**Proposed fix:** add a `str → ""` (and `float → 0.0`, `bool → 0`) branch to
`_field_default`, and capture string-constant defaults in `_collect_class_fields`
(store the lowered literal, not just int/float/array-size). A `str` field with no
explicit default should default to `""`. Faithful and byte-safe: only records
that actually contain a str field change emission.

---

## Gap 2b — a fieldless class is not emitted as a record type_decl, so its methods are not injected on import

**API symbols blocked:** `Formatter.format`, `Formatter.format_field`
(`Formatter` has **no** instance fields — `class Formatter:` with only methods).

**Symptom:** a module-level (or local) `Formatter()` whose method is called
fails the inliner / lowering:
```
cannot inline call to 'fmt.format': method 'formatter__format' not found.
```
For a module-global `fmt = Formatter()`, the inliner's function map contains
only the driver itself — the imported `formatter__*` method stubs were never
injected.

**Minimal reproducer** (`--memory-model hoare`):
```python
# pycsl-flags: --memory-model hoare
from pure_lib.strmod import Formatter
fmt = Formatter()
#@ ensures \result >= 0
#@ assigns \nothing
def drv(f: str) -> int:
    return len(fmt.format(f))
```

**Root cause:** `Formatter` has no fields, so it is **not** emitted as a record
`type_decl` (it lowers to a bare `type formatter = int` alias). The imported-class
injector
`src/pycsl/frontend/ir_resolve.py` `_resolve_imported_classes`, line ~352:
```python
if orig not in dep_types or local in existing_types:
    continue
```
keys off `dep_types` (the dependency's `type_decls`). Because `Formatter` is not
a record `type_decl`, the `continue` fires and the `formatter__*` method stubs
(lines ~362-371) are **never injected** into the importer's `functions`. The
module-globals inliner (`apply_inline_globals` → `_inline_calls`) then cannot find
`formatter__format` in its `fmap` and raises "method ... not found".

(Note the `\trusted` methods are abstract `val`s with no inlinable body; even when
a class *is* a record (Template), a `#@ no_inline` annotation on the trusted
method does NOT route the call to the emitted `val` for an *imported* class —
worth confirming as a sub-issue, but Gap 2b's primary blocker is the missing
record `type_decl` for the fieldless class.)

**Proposed fix:** emit a (possibly empty) record `type_decl` for any imported
class that has methods, even with zero fields (`type formatter = { }` /
a unit-carrying record), so `_resolve_imported_classes` injects its method stubs
and a constructed instance's method calls lower against the emitted `val`
contracts. Alternatively, relax the `orig not in dep_types` guard to also accept a
class known via its `<class>__*` method stubs in `dep_funcs`.

---

## Why the loop is still honestly closed

Every one of the 10 public API symbols now has a proved theorem in
`pure_lib_test/formal_strmod.py`. The four method symbols that delegate to a
module-level function (`substitute`/`safe_substitute` → `template_*`;
both `format_field`s → module `format_field`) carry the method's *exact*
library-reference promise through the twin (a real equality for `format_field`).
The three with no twin keep the strongest instance-free safety form. The
shortfall — the *instance-method* propagation (read-after-write for
`set_template`; the 0/1 domain *of the called method*; the `format` result via a
constructed `Formatter`) — is captured here as Gap 2a / Gap 2b with minimal
reproducers, root causes (file:line), and proposed fixes. Fixing Gap 2a + 2b
would let `formal_strmod.py` construct `Template()` / `Formatter()` and assert the
method promises directly (e.g. `t.set_template(n); t.template == n`), upgrading
the six GAP-LIMITED / via-twin theorems to direct instance-method theorems.
