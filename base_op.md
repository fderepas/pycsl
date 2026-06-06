# Plan: Python object/class dunder support in PyCSL (tiered)

## Context

The strings-plan deliberately excluded these 8 dunders as "object/attribute/class machinery, not
string operations". This plan would add them — but a pros/cons weighing showed the 8 dunders have
**very different ROI**, and that bundling them is a mistake:

- **Tier A — construction (`__init__`/`__new__`): high value, low risk.** `C(5)` today silently
  ignores `5` and builds from defaults — a real expressiveness hole affecting *any* class with an
  `__init__(self, x)`. Fixing it is broadly useful and self-contained.
- **Tier B — attribute interception (`__getattribute__`/`__setattr__`/`__delattr__`): medium,
  narrow value; high risk.** Now *soundly modelable* thanks to real strings (route external
  `obj.attr` through the user method with the name as a real string literal). But it touches a
  **core lowering path** every attribute access uses, and there is **no program that fails today**
  for want of it — it would violate the project's demand-driven (Gate-A) discipline.
- **Tier C — lifecycle/reflection (`__dir__`/`__init_subclass__`/`__subclasshook__`): near-zero
  verification value.** Inert hooks / a field count. PyCSL **already** doesn't choke on them
  (they're dropped by the blanket dunder skip), so machinery here proves nothing.

**Decision (this plan):** build **Tier A now**; **gate Tier B** behind a real demand-driver;
**Tier C is recognize-and-document only** (no code). This captures ~80% of the value for ~30% of
the risk/surface, and preserves PyCSL's "every supported thing has teeth" property.

---

## Tier A — Parametrized construction (`__init__` / `__new__`) — BUILD NOW

**Goal:** `C(a, b)` constructs a record whose fields come from the `__init__` body's
`self.x = <expr-over-params>` initialisers with actual args substituted for the formals — so a
test can prove `C(5).x == 5` and `C(a,b)` with `self.y = a+b` discharges `\result == a+b`.

This tier is **self-contained**: it touches only the construction path. It needs **no** routing,
**no** new IR statements, and **no** `_should_skip_method` change (`__init__`/`__new__` are already
skipped-as-methods and used only for field discovery; we extend the *construction* lowering).

**Changes:**
- **Module5 `_collect_class_fields` / `visit_ClassDef`** (Module5_IREmitter.py ~1031-1089,
  1157-1197): onto the record `type_decl`, capture `init_params:[str]` (ordered `__init__` formals
  minus `self`) and `init_body:[{field, value_ir}]` (source-ordered initialisers whose RHS is a
  literal / a param / an expr over params). Also `new_trivial:bool` (`__new__` absent or only
  `return super().__new__(cls)`). Anything outside the flat-initialiser shape → leave `init_body`
  empty and fall back to today's default-witness construction (sound, just less precise).
- **Module6 `_call_record_constructor`** (expressions.py ~916-944): drop the `len(args)==0`
  guard; build the record literal by substituting actual args for `init_params` in each
  `init_body` value via `_expr_to_whyml(..., subst=<param→arg map>)` (subst already threaded,
  e.g. `_handle_binop` 277). Fields not set in `init_body` keep their typed default (`_field_default`).
- **Module3_Weaver** (~251-266, mirroring the `__del__`/UB-7.5 scan): **reject** a non-trivial
  `__new__` (returns a cached/other/singleton instance) with a semantic error + a new UB rule —
  boundary enforced, not faked. A trivial `__new__` is accepted and ignored (construction proceeds
  via `__init__`).
- **Registry** (preamble.py ~561-566): carry `init_params`/`init_body` into
  `self._record_types[Cls]` if the constructor path reads them there rather than from the type_decl.

**Corpus (next free = 0495; conventions: docstring, `# pycsl-flags:`, `_ = 0 # anchor`):**
- `0495.py` — `__init__(self, a, b)` with `self.x=a; self.y=a+b`; construct `C(2,3)`, prove a
  contract over `.x`/`.y` (e.g. `\result == 5`).
- `0496.py` — trivial `__new__` + parametrized `__init__`; `C(5).x == 5` discharges.
- `0497.py` (`# pycsl-expected: FAIL`) — non-trivial `__new__` (returns a cached instance) ⇒
  Module3 rejection; docstring states the allocation-interposition boundary.

---

## Tier B — Attribute interception (`__getattribute__`/`__setattr__`/`__delattr__`) — GATED

**Do not build until a named demand-driver exists:** a concrete Python program that PyCSL
**cannot verify today** *because* attribute interception isn't modeled (analogous to `0471` for
strings). If no such program can be written, defer — the cost is real and the routing perturbs a
core path. Capture the driver as a committed `# pycsl-expected: FAIL` corpus file first; it flips
to PASS exactly when this tier lands.

**Design (retained, sound — for when the gate opens):** real strings make this sound. When a class
*defines* one of these dunders, route the *external* operation through the user method, passing
the attribute name as a real string literal:
- `obj.attr` → `cls__getattribute__ obj "attr"` (hook in expressions.py `_handle_attribute_expr`
  ~1069-1082; external reads are `Attribute` nodes, distinct from in-method `self.x` `FieldGet`).
- `obj.attr = v` → `cls__setattr__ obj "attr" v` (new IR stmt `ExternalSetAttr` from a non-self
  `Attribute` assign target, Module5 `_py_stmt_assign` ~723-755; handler mirrors
  `_handle_fieldassign_stmt` statements.py ~955-1004).
- `del obj.attr` → `cls__delattr__ obj "attr"` (new IR stmt `ExternalDelAttr`, replacing the
  current no-op `Pass` Module5 ~849-850, only when the class defines `__delattr__`).

Lift `_should_skip_method` (Module5 ~1200-1209) to an **allow-list** emitting only these three (+
still skipping everything else). Method bodies are verified: `name:str` is typed `string`
(functions.py 134-139) so `if name == "x"` uses the sound `str_eq_op` bridge; `self.x` stays
direct record access. **Anti-recursion firewall:** a `self._in_dunder_of == C` flag suppresses
re-routing inside `C`'s own dunder bodies (the `FieldGet`/`Attribute` split already makes `self.x`
safe structurally); `super().__getattribute__/__setattr__(self,"x")` maps to the **primitive**
(direct record access) — the documented `object`-base escape hatch. Emit `\abstract`, never
`\trusted`. `__setattr__` must re-establish the class invariant (the Why3 obligation = the
negative test). Liskov refinement (functions.py ~314-373) applies for free on overrides.

**Corpus when built:** `0498` `__getattribute__` (external `o.x` == field), `0499` `__setattr__`
(preserves invariant), `0500` `__delattr__` (resets field); negatives `0501`
invariant-breaking `__setattr__` (FAIL) and a dynamic non-literal name (opaque, FAIL).

**Extra diligence:** because Tier B perturbs the core attribute path, run the full sweep AND a
targeted adversarial review (soundness of routing/super/anti-recursion) before committing.

---

## Tier C — Lifecycle/reflection (`__dir__`/`__init_subclass__`/`__subclasshook__`) — DOC ONLY

**No code.** PyCSL already drops these via the blanket dunder skip, so a class defining them
already compiles and proves. Deliverables:
- One **smoke test** (`# normal expected-PASS`): a generic class that *defines* all three and still
  constructs + verifies its real contracts — proving they're inert, not breaking.
- A **doc note** (static-semantics + `pycsl-annotate/SKILL.md`): these are *recognized but inert*
  — `__dir__` contents/order, subclass-registration side effects, and ABC/`__subclasshook__`
  virtual-subclass semantics are out of model. If a future need arises, `__dir__` could gain an
  abstract `val` with `ensures len(result) == #fields` — deferred until demanded.

---

## Soundness & out-of-scope (documented, not faked)

Applies across tiers; prefer documented opaqueness / `\abstract` over `\trusted` (0-trusted
policy). NOT modeled: re-entrant/recursive lookup (in-dunder access is the primitive); descriptors
/ `__get__` / `__set_name__` / slots; MRO / multi-level `super()` / cooperative MI
(`super().__getattribute__` maps only to the `object` primitive; `_apply_inheritance` is
single-level); metaclasses / `type.__call__` / `tp_alloc` (non-trivial `__new__` rejected);
**non-literal dynamic attribute names** (`getattr(o, runtime_str)` stays opaque `getattr_<cls>`,
name hashed); attribute *removal* (records have fixed shape — `__delattr__` re-assigns, post-del
`hasattr` opaque); `__init__` with control-flow/method-calls/`*args` (falls back to default-witness
construction).

## Verification

Per file (mandatory `PYTHONHASHSEED=0`):
`PYTHONHASHSEED=0 .venv/bin/python src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0495.py`
(PASS for positives; semantic-error / UNPROVEN for `# pycsl-expected: FAIL`). Full-corpus
regression sweep after Tier A (the strings-plan `/tmp/proof_sweep.sh` pattern: honor
`# pycsl-flags:`/`# pycsl-expected:`, 120s timeout, classify regressions vs now-pass, diff against
the committed baseline). Docs: add the `__new__`-rejection UB rule to the UB catalog
(`config/skills/pycsl-ub-catalog/SKILL.md`, referenced at Weaver 266) and the Tier-C inert-hooks
note; run `bin/doc-coherency.py --check` green.

## Critical files

**Tier A (now):**
- `src/pycsl/Module5_IREmitter.py` — `init_params`/`init_body`/`new_trivial` capture
  (`_collect_class_fields` ~1031-1089, `visit_ClassDef` ~1157-1197).
- `src/pycsl/module6_whyml/expressions.py` — parametrized `_call_record_constructor` (~916-944,
  reuse `_expr_to_whyml(..., subst=...)`).
- `src/pycsl/Module3_Weaver.py` — non-trivial `__new__` rejection (~251-266).
- `src/pycsl/module6_whyml/preamble.py` — `_record_types` registry (~561-566, if construction
  reads init data there); `test-suite/corpus/pycsl-reference/0495–0497.py`.

**Tier B (gated, when a driver exists):** `Module5_IREmitter.py` (`_should_skip_method` allow-list
~1200-1209, ExternalSet/Del IR at `_py_stmt_assign` ~723-755 / `_py_stmt_delete` ~849-850);
`module6_whyml/expressions.py` (`_handle_attribute_expr` routing ~1069-1082, `str_eq_op` ~307-315);
`module6_whyml/statements.py` (new ExternalSetAttr/DelAttr handlers); `module6_whyml/functions.py`
(`_in_dunder_of` flag, abstract-val ~254-260, Liskov ~314-373); ir_schema.py (new IR statements).

**Tier C (doc only):** one smoke test + doc surfaces above. No code.
