STATUS: DONE

# Convergence spec — iteration 2 (strmod full-API instance propagation)

**Loop:** `config/skills/pycsl-stdlib-coverage` — "The Convergence Principle" / Step 5 (SPEC PHASE).
**Input gap doc:** `10-2006-convergence-gap-2.md`.
**Scope of this spec:** two precise, separately-reproducible tool facets that block
*constructing* the strmod model's classes (`Template`, `Formatter`) in a formal-test
driver, so the six class-method symbols can be propagated through their REAL instance
form rather than the current module-level proxies / instance-free stopgaps. NO source
is edited in this phase; implementation follows only after coordination sets
`STATUS: APPROVED`.

Both gaps reproduce against the CURRENT committed model `pure_lib/strmod/__init__.py`
(unchanged; it proves standalone — `--no-proof` L3-tc ✓). Confirmed by /tmp probes
(below). They are the two faithful siblings of the already-landed call-arg default fix
(commit 2343c5d) and the str-field record-type fix (07-2333 TP-3): the *field type* of a
`str` field already lowers correctly to Why3 `string` (preamble.py:957-961); only the
*default-value witness* and the *fieldless-class type_decl* remain.

---

## Reproduction evidence (probes; no source touched)

**Gap 2a** — `/tmp/probe_2a.py` (`Template()` + `set_template`):
```
[*] Imported class from 'pure_lib.strmod': Template (record + 4 method stub(s) + 7 helper(s))
[level] L1 ✓  L2 ✓  L3-tc ✗
This expression has type int, but is expected to have type string
```
Emitted `.mlw` (`--keep-mlw`):
```
line 13:  type template = { mutable template: string }      (* field TYPE correct *)
line 15:  let t : template = { template = 0 }                (* default VALUE wrong: int 0 *)
```
So the *only* defect is the record-literal default `0` for the `string`-typed field.

**Gap 2b** — `/tmp/probe_2b.py` (`Formatter()` + `format`):
```
[!] PIPELINE ERROR:
cannot inline call to 'fmt.format': method 'formatter__format' not found.
```
Dependency IR of `pure_lib/strmod/__init__.py` (via `bin/pycsl-ir-dump.py`):
```
type_decls names: ['Template']        # Formatter ABSENT — it has no fields
Formatter funcs: ['formatter__format_field', 'formatter__format']   # methods PRESENT
```
So Gap 2b **reproduces** against the current model: `Formatter` (only methods, no
instance fields) gets NO `type_decl`, so `ir_resolve._resolve_imported_classes`
(`orig not in dep_types` → `continue`) never injects its `formatter__*` method stubs.
**Gap 2b is in scope** (the prompt's "verify it still has an int field" hypothesis is
false — `Formatter.__init__` does not exist; there is no `self._depth`).

---

## Preamble: the two gaps and the shared idea

The shared idea is *faithful, type-correct construction of an imported class instance*.
Constructing `C()` in a driver needs (i) a type-correct record literal for every field,
and (ii) the class's method stubs injected into the importer so a method call lowers
against the emitted `val` contract. Gap 2a breaks (i) for a `str` (or `real`) field;
Gap 2b breaks (ii) for a class with zero fields. Both fixes are byte-additive: they fire
only on shapes ABSENT from the current proving corpus (a `str`/`real` field default
witness; a fieldless-but-method-bearing imported class), so existing emission is
byte-identical.

---

## Gap 2a — planned edit: type-aware record-field default

**Defect:** a `str` record field with no explicit captured default lowers to the int
literal `0` in the constructed record literal `{ template = 0 }`, ill-typed against the
correctly-typed field `template: string`.

**Two cooperating sites (both confirmed by reading current source):**

1. `src/pycsl/frontend/Module5_IREmitter.py` `_collect_class_fields`, **lines 1403-1409**
   (the `AnnAssign` branch — `Template.template: str = ""` is an `AnnAssign`):
   ```python
   if (stmt.value and isinstance(stmt.value, ast.Constant) and
           isinstance(stmt.value.value, (int, float))):
       field_defaults[stmt.target.attr] = int(stmt.value.value)
   elif stmt.value is not None:
       sz = self._array_init_size(stmt.value)
       if sz is not None:
           field_defaults[stmt.target.attr] = sz
   ```
   A `str` constant default (`""`) is neither int/float nor an array size, so NOTHING is
   stored → `field_defaults` has no `template` entry. (The `ast.Assign` sibling branch at
   lines 1389-1394 has the identical shape and the identical hole; the strmod blocker
   uses the `AnnAssign` path, but the fix should cover both branches symmetrically to
   stay faithful for `self.x = "" ` written without an annotation.)

2. `src/pycsl/module6_whyml/expressions.py` `_call_record_constructor._field_default`,
   **lines 1538-1543**:
   ```python
   ft = field_types.get(fn, "int")
   if ft in ("list", "array"):           return f"(Array.make {…} 0)"
   if ft in ("dict", "set", "frozenset"): return "(const (None: option int))"
   return f"{rec_info['defaults'].get(fn, 0)}"   # <-- str/float/bool fall here -> 0
   ```
   No `str` (nor `real`/`float`/`bool`) branch. The field-type source the fix must
   consult is `field_types` (= `rec_info["field_types"]`, populated in
   `preamble.py:930` from each field's `"type"` tag, which is `"str"`/`"string"` for the
   `template` field). This is the SAME dispatch key already used for the list/dict
   branches.

**Planned fix (the substantive site is `_field_default`):**
- Add, before the int fallback, the type-aware default mirroring
  `expr_ghost_spec_ops.py:74` (`'""' if ptype == "str" else "0"`):
  - `ft in ("str", "string")` → return `'""'` (faithful empty string);
  - `ft in ("real", "float")` → return `"0.0"`;
  - (`bool` stays `0`, already correct under the 0/1 bool model — no change).
- A `str` field WITH an explicit captured default keeps that default; but because the
  field type is `string`, the captured value (if any) must itself be a lowered string
  literal, not an int. The minimal, faithful rule: for a `str`/`real` field, IGNORE the
  int `field_defaults` slot and use the typed witness (`""` / `0.0`). (`Template.template`
  has no captured default, so this is moot for strmod, but it keeps the witness
  type-correct if Module5 later captures a string-literal default.)
- OPTIONAL companion (site 1, `_collect_class_fields`): capture a `str`/`bool`-constant
  default as a *lowered literal* so a non-empty default (e.g. `self.tag: str = "x"`)
  survives. NOT required for strmod (default is `""`); the `_field_default` typed witness
  alone unblocks the strmod driver. Recommend deferring site 1 unless a corpus class
  needs a non-empty str default (none found — see RISKS).

**Trigger condition:** fires only when a constructed record (`C()` / `C(args)`) has a
field whose type tag is `str`/`string`/`real`/`float`. **Byte-additivity:** every record
in the proving corpus today has only int/list/dict/set/array fields (the str-field
record `Template` is NOT currently constructed anywhere that proves — the gap is exactly
that it can't be). So no existing `.mlw` line changes: the new branch is reached only by
the new strmod driver. Gate by full-corpus byte-diff.

---

## Gap 2b — planned edit: fieldless method-bearing class emits a (unit-carrying) record

**Defect:** `Formatter` has no instance fields, so Module5 emits NO `type_decl`
(`visit_ClassDef` guard `if fields or bases:` at **Module5_IREmitter.py:1535** is false),
and the class lowers to an opaque `type formatter = int` alias. `ir_resolve.
_resolve_imported_classes` (**ir_resolve.py:352**, `if orig not in dep_types or local in
existing_types: continue`) keys off the dependency's `type_decls`; with `Formatter`
absent from `dep_types`, the `continue` fires and the `formatter__*` method stubs
(injected at ir_resolve.py:362-371) are never added to the importer's `functions`. The
module-globals inliner then can't find `formatter__format` in its `fmap`.

**Why an empty record won't do:** Why3 rejects `type t = { }` and `{ }` (confirmed:
`why3 prove --type-only` on `type formatter = { }` → *syntax error*). The fieldless
record MUST carry one dummy field. Confirmed type-correct:
```
type formatter = { mutable __unit: int }
let f () : formatter = { __unit = 0 }      (* typechecks OK *)
```

**Planned fix — two coordinated edits:**

1. `Module5_IREmitter.py` `visit_ClassDef`, **line 1535**: relax the guard so a class
   that has METHODS (any `ast.FunctionDef` other than skipped dunders/properties) but no
   fields and no bases STILL emits a `type_decl` of `"kind": "record"`. Mark it (e.g.
   `"synthetic_unit": True` or simply `fields == []`) so Module6 knows to inject the unit
   field. (`method_names` is already computed at lines 1501-1503, so the
   "has methods" test is local.)

2. `src/pycsl/module6_whyml/preamble.py` record emission, **line 970**
   (`out.append(f"  type {type_name} = {{ {'; '.join(field_strs)} }}")`): when
   `field_strs` is empty, emit a single synthetic unit field
   `mutable {label}__unit: int` so the type is `type formatter = { mutable formatter__unit: int }`
   rather than the syntactically-illegal `{ }`. Correspondingly, in
   `expressions.py` `_call_record_constructor` (the `field_inits` join at lines 1565-1568),
   a fieldless record's `rec_info["fields"]` is empty → it would emit `{ }` (illegal);
   the constructor must emit the matching `{ formatter__unit = 0 }`. Cleanest: register
   the synthetic field in `_record_types[name]["fields"]` (preamble.py:927-935) so BOTH
   the type decl AND the constructor see it uniformly, and no special-casing leaks into
   the constructor.

   The synthetic field name must be `_field_label`-safe and collision-free
   (`__unit`/`formatter__unit` — no Python field can be named with the mangled class
   prefix, so safe).

After both edits, `Formatter` appears in the dependency `type_decls`; ir_resolve.py:352
no longer `continue`s; the `formatter__*` stubs are injected (the existing path at
362-371 needs NO change); and `Formatter()` construction lowers to
`{ formatter__unit = 0 }`, with `fmt.format(f)` resolving to the injected
`val formatter__format`.

**Sub-issue noted in the gap doc** (`#@ no_inline` on a trusted imported method routing
to the `val`): NOT required for this fix. `Formatter.format` and `Formatter.substitute`
are `#@ \trusted` → emitted as abstract `val`s with no body; the importer's inliner must
route the call to the injected `val` rather than attempting to inline a (nonexistent)
body. Once the stub IS injected (the present fix), the call resolves to the `val`'s
contract. If the inliner still tries to inline a trusted (bodyless) method and fails,
that is a follow-on (route trusted imported methods to their `val`), to be flagged at
implementation time — out of scope for THIS spec unless it surfaces during re-prove.

**Trigger condition:** fires only for a class with methods but zero instance fields and
zero bases. **Byte-additivity:** no such class exists in the proving corpus today
(`Formatter` is precisely the shape that currently fails). Every existing class has at
least one field or a base, so the `if fields or bases:` path is unchanged and the
`{ ... }` type decl for non-empty records is byte-identical (the synthetic-unit branch is
reached only when `field_strs == []`). Gate by full-corpus byte-diff.

---

## Re-prove plan: proxy → real instance-method theorems

Target: `pure_lib_test/formal_strmod.py`. After both fixes, construct `Template()` /
`Formatter()` in the driver and assert each method's REAL promise through the actual
instance, replacing the module-twin proxies and the instance-free stopgaps.

| # | API symbol | current theorem | current stance | upgraded theorem (real instance) |
|---|---|---|---|---|
| 5 | `Template.set_template` | `formal_strmod_set_template_readback` | GAP-LIMITED (`len(n) >= 0`) | construct `t = Template()`, `t.set_template(n)`, assert `t.template == n` (read-after-write, the model's own `ensures`) |
| 6 | `Template.is_valid` | `formal_strmod_is_valid_bool` | GAP-LIMITED (const witness `1`) | `t = Template(); r = t.is_valid()`, assert `r == 0 or r == 1` through the called method's `ensures` |
| 7 | `Template.substitute` | `formal_strmod_substitute_str` | via module twin | `t = Template(); ...`, assert `\str_length(t.substitute(m)) >= 0` via the injected `val template__substitute` |
| 8 | `Template.safe_substitute` | `formal_strmod_safe_substitute_str` | via module twin | as #7 with `safe_substitute` |
| 9 | `Formatter.format_field` | `formal_strmod_formatter_format_field` | via module twin | `fmt = Formatter()`, assert `spec == "" ==> fmt.format_field(v, spec) == v` via injected `val formatter__format_field` |
| 10 | `Formatter.format` | `formal_strmod_formatter_format_str` | GAP-LIMITED (`len(fmt) >= 0`) | `fmt = Formatter()`, assert `\str_length(fmt.format(s)) >= 0` via injected `val formatter__format` |

Symbols 1-4 (module functions `capwords`, `template_substitute`,
`template_safe_substitute`, `format_field`) are already real and unchanged. The model
`pure_lib/strmod/__init__.py` stays UNCHANGED — it already proves each method standalone;
the upgrade is purely on the *driver* side (propagation to a constructing test).

Each upgraded theorem must keep the SOUND-ONLY discipline already in the file: no
postcondition that is false on real strings (the dropped `\result == template + mapping`
etc. stay dropped). The upgraded theorems assert exactly the method's own `ensures`.

---

## Gate plan (Convergence Step 5)

1. **Full-corpus byte-diff IDENTICAL** — `bin/extraction-byte-diff*.sh` over the whole
   reference corpus: every existing `.mlw` byte-for-byte unchanged (both fixes are
   additive; new branches reached only by str/real-field defaults resp. fieldless
   classes, absent from the corpus).
2. **Conformance 38/38** — `bin/run-conformance.sh` (both corpora, currently 38/38 each).
3. **os byte-identical** — re-emit the `os` model/demos; no change (no str-field record
   construction, no fieldless method-bearing class there).
4. **strmod model still proves** — `pycsl --no-proof pure_lib/strmod/__init__.py`
   (L3-tc ✓) and the full proof run unchanged (model file untouched).
5. **Upgraded `formal_strmod` proves** — all 10 theorems Valid under `--memory-model
   hoare` (Alt-Ergo → Z3); the six method theorems now via REAL instances (#5-#10 above),
   none weakened to `True`.
6. **Doc-coherency green** — `bin/doc-coherency.py --check` (no new directive introduced,
   so expected no-op, but run as the standard leading gate).
7. **Language audit (if any clause surface touched)** — none expected; both edits are
   lowering/emission, not new `#@` syntax. Skill `pycsl-audit-pycsl-language` not
   triggered.

A new reference-corpus driver SHOULD be added under
`test-suite/corpus/pycsl-reference/` exercising (a) constructing a str-field record and
reading the field back, and (b) constructing a fieldless method-bearing imported class
and calling a method — per MEMORY `feedback_reference_corpus` (new-feature plans add to
the reference corpus). The two /tmp probes are the seeds.

---

## RISKS / open questions for the coordination agent

1. **Synthetic-unit field naming & uniformity (Gap 2b).** The cleanest implementation
   registers the synthetic `__unit` field in `_record_types[...]["fields"]` so the type
   decl, the constructor literal, AND any field-access machinery all agree. Decision
   needed: register it as a real field (uniform, but the field then appears in
   `_record_types` and could theoretically be referenced) vs. special-case only the two
   emission sites (preamble type-decl + constructor literal). Recommend the registered
   route for uniformity; flag for your judgment.

2. **Does emitting a fieldless class as a record perturb other class drivers?** Verified
   NO existing corpus class is fieldless-with-methods (the guard `if fields or bases:`
   currently drops exactly such classes; the only known instance is `Formatter`, which
   today FAILS). The synthetic-unit branch is reached only when `field_strs == []`, so
   non-empty records are byte-identical. Mixin composers (`is_mixin`, Module5:1506-1534)
   already get fields merged when stateful and otherwise intentionally stay opaque
   `type c = int`; the new guard must NOT capture method-less mixins — restrict it to
   "has at least one non-dunder/non-property method AND not is_mixin" to avoid
   reintroducing a record for a pure-mixin composer. **Open question for you:** confirm
   the guard's exact predicate (has-methods AND not-mixin AND no-fields-no-bases) so a
   stateless mixin composer is not accidentally promoted to a record.

3. **Is there a corpus class with a non-empty str field default (Gap 2a)?** Grep of the
   corpus found none that is *constructed* (the str-field record case is exactly the
   blocked one). The `_field_default` typed-witness change therefore changes no existing
   byte. If the coordination agent wants the non-empty-default capture (site 1) too, that
   is a strictly larger but still additive change — recommend deferring it (strmod only
   needs the empty-string witness).

4. **Trusted imported method routing (Gap 2b sub-issue).** `Formatter.format` /
   `Template.substitute` are `#@ \trusted` (abstract `val`). The fix injects the stub;
   the open risk is whether the importer's inliner attempts to inline a bodyless trusted
   method and fails (the gap doc flags this as "worth confirming"). If re-prove (#9 gate)
   surfaces it, a follow-on edit routes trusted imported method calls to the injected
   `val` instead of inlining. Flag, do not pre-implement.

5. **`Template.is_valid` returns `bool`/0-1 through a real instance.** The upgraded #6
   theorem calls the method and asserts `r == 0 or r == 1`. Confirm the bool model lowers
   the imported `val template__is_valid` return as `int` (the dependency IR shows
   `val template__is_valid (self: template) : int` — consistent), so the 0/1 domain
   propagates. Low risk; noted for completeness.

---

*No source files were modified in producing this spec. The probes live only in /tmp.*

---

## COORDINATION APPROVAL (editorial rulings; STATUS set to APPROVED above)

The plan is sound; approved with the following rulings — one binding guard, two deferrals:

- **R1 (synthetic-unit field):** APPROVED — register the synthetic `__unit` field in
  `_record_types[...]["fields"]` (the uniform route: type-decl + constructor agree, no special-casing).
- **R2 (fieldless-class promotion guard) — BINDING:** the new record-promotion guard MUST be exactly
  *"has ≥1 non-dunder / non-property method AND `not is_mixin` AND no fields AND no bases"*. It MUST NOT
  capture mixin composers — stateless mixins intentionally stay opaque `type c = int`, and the
  mixin-composition machinery depends on that. If the byte-diff shows ANY class/mixin change beyond
  `Formatter`, the guard is too broad — NARROW it (never widen to absorb a diff).
- **R3 (Gap 2a site 1 — non-empty str-default capture):** DEFERRED — implement ONLY the `_field_default`
  typed witness (`""` for str, `0.0` for real). strmod needs only the empty-string witness; the Module5
  capture site is a follow-on if a corpus class later needs a non-empty str/real field default.
- **R4 (trusted imported method routing):** DEFERRED — do NOT pre-implement. If the re-prove (gate #5)
  shows the inliner trying to inline a bodyless `#@ \trusted` method and failing, STOP and write
  `DD-HHMM-convergence-gap-3.md` (the loop continues honestly) rather than hacking a route in here.
- **R5 (is_valid 0/1):** proceed — low risk; the dependency IR confirms an `int` return.
- **Reference corpus:** APPROVED + REQUIRED — add the two reference-corpus drivers (a str-field record
  read-back; a fieldless method-bearing class construct+call) per the new-feature corpus rule.

**Acceptance bar:** full-corpus byte-diff IDENTICAL (especially NO class/mixin change beyond the new
shapes), conformance 38/38, os byte-identical, the strmod *model* byte-identical and still proving, the
upgraded `formal_strmod` (all six method theorems via REAL constructed `Template()`/`Formatter()` instances,
none weakened to `True`) proving, doc-coherency green. On success, set this doc's `STATUS: DONE`.
