# 32-1700-typing-spec-8.md — `Protocol` Implementation Spec (DONE, graduated)

**Status:** DONE — graduated to Normative. Coordinator EDITORIAL APPROVED; core-agent
implemented both planes; Gate B (standing gate) GREEN; Gate C (conformance) GREEN
(see `typing-engagement/ty2/conformance_proto/GATE-C-RESULTS.md` — the GT7 no-blend
keystone P5 PASSES).
**Tier:** TY2 (aggregates and interfaces).
**Construct:** `Protocol` (PEP 544) + `@runtime_checkable` + `#@ conforms_to`.
**Two-plane spec authority:** `typing-engagement/ty2/protocol-twoplane-spec.md` (Gate A APPROVED).
**Global guides honoured:** `typing-global-impl.md` §0 (no-blend), §4 (per-construct pipeline + gates),
§5 (TY2: "Protocol -> a contract interface, conformance as per-method behavioural refinement").
The core-agent hard rule: `Protocol` is a contract interface, conformance as per-method behavioural
refinement. NO `\trusted`. The GT7 no-blend trap (the canonical `@runtime_checkable`
presence-vs-conformance split) is the keystone — see §3.

**This is a planning document. No `src/pycsl/` file is modified by this DRAFT.** On
coordinator APPROVAL, the core-agent implements both planes and runs the standing gate.

---

## 0. Design summary (one paragraph)

A `class P(Protocol)` declaration is recognized at the `visit_ClassDef` seam by
`_is_protocol_class` (bare head name `Protocol` or dotted `typing.Protocol` in `node.bases`). It
synthesizes (a) a marker record `type_decl` with `is_protocol: True` (a plain record carrying the
protocol's method contracts as its ONLY state — the protocol has no instance fields, so the record
is the interface anchor), and (b) emits each protocol member `def m(self, ...) -> R: ...` as a
function IR node with `abstract: True` (the EXISTING `csl_abstract`/`abstract` IR flag — a bodyless
`val` defined by its contract alone, an uninterpreted op that is SOUND and NOT `\trusted`). The
member's `#@ ensures/requires/assigns` contract is the **refinement target**. Conformance is
declared explicitly via a new `#@ conforms_to P` class directive (a TY2 scope restriction —
divergence-by-strictness: PEP 544 conformance is structural/implicit, but PyCSL requires the
directive so conformance is a discharged per-method VC, not a whole-program structural search). For
each member `m` of `P` that `C` provides, the front-end populates the EXISTING `overrides` IR list
with `{"sub_method": "C__m", "base_method": "P__m", "sub_type": "c", "base_type": "p"}`. The
EXISTING `--check-behavioral-subtyping` flag then emits one refinement goal per member
(`_render_refinement_goal` in `functions.py:816`):
`forall self: C, .... ((pre_P -> pre_C) /\ (post_C -> post_P))` — the per-method behavioural-
refinement VC (P2/P4). The runtime shim for `@runtime_checkable` is a thin identity
(`ensures \result == val`) that performs NO signature/contract/presence check beyond the identity
(R3–R7). NO new IR node (reuses `abstract` flag + `overrides` list + the existing refinement-goal
emitter); NO IR_VERSION bump; NO `\trusted`. Byte-identical for non-Protocol drivers (the
`_is_protocol_class` check is a pure base-name test that fires only when `Protocol` is a base).

---

## 1. Normalization rule (front-end: `src/pycsl/frontend/`)

### 1.1 Surface forms to recognize

Per the two-plane spec §1.0 (P1, P1a, P1b):

| Surface | AST shape (post-`pure_ast`) | Disposition |
|---|---|---|
| `class P(Protocol): ...` | `ClassDef(name="P", bases=[Name("Protocol")], body=[FunctionDef(m), ...])` | recognize as protocol; emit marker record `is_protocol: True`; emit each member `m` as `abstract: True` function IR |
| `class P(Protocol): ...` (dotted) | `bases=[Attribute(value=Name("typing"), attr="Protocol")]` | same — recognize the attribute tail `Protocol` |
| `@runtime_checkable\nclass P(Protocol): ...` | `ClassDef(decorator_list=[Name("runtime_checkable")], bases=[Name("Protocol")])` | same — `@runtime_checkable` is a RUNTIME-plane marker (P1b); the static plane IGNORES it (it gates the runtime shim, §3) |
| `class C(Protocol)` member `def m(self, ...) -> R: ...` | `FunctionDef(name="m", body=[Expr(Constant(Ellipsis))])` | emit as `abstract: True` function (bodyless `val` with contract) — the refinement target |
| `#@ conforms_to P`<br>`class C: def m(self, ...) -> R: ...` | `ClassDef(name="C", csl_conforms_to=["P"])` | populate `overrides` with `(C__m, P__m)` per shared member name (§1.3) |
| `class C(P): ...` (regular subclass, NOT conforms_to) | `ClassDef(bases=[Name("P")])` where `P` is a Protocol | byte-identical fallback — a subclass of a protocol is NOT a conformance declaration (PEP 544 distinguishes explicit subclassing from structural conformance; PyCSL's TY2 scope treats `C(P)` as inheritance-as-usual if P is a record, OR byte-identical fallback if P is a protocol-record — the protocol record has no fields, so inheritance merge is a no-op) |

`Protocol` is recognized by the bare head name in `bases` (the import-rewriting in
`import_classifier.py` already canonicalizes `from typing import Protocol`).

### 1.2 Canonical IR form

The protocol's marker record (a pure interface anchor — no fields):

```
{ "kind": "record", "name": "P",
  "fields": [], "class_invariants": [], "field_defaults": {},
  "has_hash": False, "has_eq": False, "is_unhashable": False,
  "constants": {}, "bases": [],
  "init_params": [], "init_body": [], "init_ensures": [],
  "is_mixin": False, "compose_from": [],
  "is_protocol": True }
```

Each protocol member is a standard function IR node with `abstract: True` (the EXISTING flag — no
new IR field). NO new top-level IR node, NO new field beyond the `is_protocol: True` boolean on the
record (a record-level flag, same shape as `is_typeddict: True` / `is_namedtuple: True`):

```
{ "name": "P__m",                  # the member, namespaced under the protocol record
  "kind": "method", "self_type": "P",
  "contracts": {
    "requires": [...],            # the member's #@ requires (the refinement target's pre)
    "ensures": [...],             # the member's #@ ensures (the refinement target's post)
    "assigns": [...] },
  "body": [],                     # bodyless — abstract: True emits a `val`, not a `let`
  "abstract": True,               # the EXISTING flag (Module5: csl_abstract / IR "abstract")
  ... }
```

The conformance declaration populates the EXISTING `overrides` IR list (the same list
`apply_inheritance` populates for subclass overrides):

```
program_ir["overrides"] = [
  {"sub_method": "C__m", "base_method": "P__m",
   "sub_type": "c", "base_type": "p"},     # one entry per shared member name
  ...
]
```

NO IR schema change beyond the record-level `is_protocol: True` boolean. The `abstract` flag and
the `overrides` list are EXISTING IR shapes. **IR_VERSION stays at 1.3** (the `is_protocol` flag is
a record-level boolean in the same class as `is_typeddict`/`is_namedtuple`, which did NOT bump the
version — additive record flags are not a wire-format change).

### 1.3 Normalization steps (in order)

1. **`_is_protocol_class(node)`** — in `visit_ClassDef` (`Module5_IREmitter.py:1906`), BEFORE
   `_collect_class_fields`, check `_is_protocol_class(node)`: True iff any `b` in `node.bases` is
   `Name(id=="Protocol")` or `Attribute(attr=="Protocol")`. Byte-identical for non-Protocol classes
   (pure base-name test).

2. **`_emit_protocol_interface(node)`** — if True:
   - emit the marker record (`is_protocol: True`, empty fields, no bases);
   - set `self._current_class = node.name`;
   - for each `FunctionDef m` in `node.body` (a protocol member): build the function IR via
     `_build_function_ir(node=m)`, set `func_ir["abstract"] = True`, set `func_ir["kind"] =
     "method"`, `func_ir["self_type"] = node.name`, and append to `program_ir["functions"]`. The
     member's body is `...`/`pass` (PEP 544 convention) — it is NOT lowered (an abstract `val`
     emits no body). A member with a real body is STILL abstract (the protocol member's body is
     never executed; PEP 544 treats it as a default that conforming classes may override — for the
     TY2 scope, all members are abstract);
   - record the protocol's member names in `self._protocols[node.name] = {m1, m2, ...}` for the
     conformance pass;
   - `generic_visit(node)`; `self._current_class = None`; RETURN.

3. **`#@ conforms_to P` directive** — add a new class-level directive `ConformsToDecl` to
   `Module2_Parser` (parallel to `ComposeFromDecl`):
   - grammar rule: `conforms_to_decl: "conforms_to" CNAME ("," CNAME)*` (a class may conform to
     multiple protocols);
   - transformer: `def conforms_to_decl(self, *names) -> ConformsToDecl: return
     ConformsToDecl([str(n) for n in names])`;
   - add `conforms_to_decl` to the `class_level_directive` alternatives;
   - in `Module3_Weaver.visit_ClassDef`: harvest `ConformsToDecl` onto `node.csl_conforms_to =
     list(c.protocols)`.

4. **Conformance `overrides` population** — in `visit_ClassDef`, AFTER `_build_function_ir` for a
   NON-protocol class carrying `csl_conforms_to`:
   - for each protocol name `P` in `csl_conforms_to`:
     - look up `self._protocols.get(P)` (the set of member names); if `P` is not a known protocol
       (not in `_protocols`), raise `PyCSLSemanticError` ("class C declares conforms_to P but P is
       not a recognized Protocol class") — this is a static error (P3: a conformance declaration
       against a non-protocol is meaningless);
     - for each member name `m` in `P`'s members: find the conforming class's method `C__m` (the
       conforming class's own method, namespaced `C__m`); if `C` does NOT provide `m`, raise
       `PyCSLSemanticError` ("class C declares conforms_to P but does not provide member m") — this
       is the P3 non-conformance rejection (a class missing a member fails conformance);
     - append `{"sub_method": "C__m", "base_method": "P__m", "sub_type": "c", "base_type": "p"}`
       to `program_ir["overrides"]`.
   - The conformance VC is discharged ONLY when `--check-behavioral-subtyping` is passed (the
     existing flag that gates `_emit_subtyping_goals`). This mirrors the existing inheritance-
     override refinement: the VC is opt-in via the flag, but the `overrides` IR list is always
     populated (so `--soundness-report` can report the conformance relationship even when the VC is
     not run).

### 1.4 Front-end files that change (on APPROVAL)

| File | Change |
|---|---|
| `src/pycsl/frontend/Module5_IREmitter.py` | add `_protocols: Dict[str, Set[str]]` init; `_is_protocol_class`; `_emit_protocol_interface`; conformance-`overrides` population in `visit_ClassDef`. The existing `_build_function_ir` is NOT modified (byte-identical for non-Protocol). |
| `src/pycsl/frontend/Module2_Parser.py` | add `ConformsToDecl` dataclass; `conforms_to_decl` grammar rule + transformer; add to `class_level_directive` alternatives. |
| `src/pycsl/frontend/Module3_Weaver.py` | harvest `ConformsToDecl` onto `node.csl_conforms_to` in `visit_ClassDef`. |
| `src/pycsl/core_ir_semantic.py` | NO change. The `overrides` list is consumed by Module 6's `--check-behavioral-subtyping`; no new semantic check. |

### 1.5 CSL contract placement (protocol member `#@ ensures`)

A protocol member's `#@ ensures Q` / `#@ requires R` precedes the `def` (the standard CSL
contract-placement convention). The canonical protocol member form is:

```python
class Drawable(Protocol):
    #@ ensures \result >= 0
    def draw(self) -> int: ...
```

### 1.6 Conformance declaration placement

`#@ conforms_to P` precedes the `class` statement (a class-level directive, like `#@ mixin` /
`#@ compose_from`):

```python
#@ conforms_to Drawable
class Square:
    #@ ensures \result >= 0
    def draw(self) -> int:
        return 1
```

### 1.7 TY2 scope restriction (divergence-by-strictness)

PEP 544 conformance is STRUCTURAL and IMPLICIT (any class with matching methods conforms, no
declaration required). PyCSL's TY2 scope requires an EXPLICIT `#@ conforms_to P` directive. This is
a legitimate divergence-by-strictness (§0: the static lower bound may be stricter than S1): an
implicit structural search would require whole-program analysis (every class against every
protocol), which is outside PyCSL's per-module verification model. The explicit directive makes
conformance a discharged per-method VC (P2/P4) within the module. The conformance subset (§5) uses
explicit `conforms_to` declarations.

---

## 2. Lowering table entry (Module 6: `src/pycsl/module6_whyml/`)

### 2.1 The lowering

The protocol member's `abstract: True` flag lowers through the EXISTING `_emit_function` path
(`functions.py:620`): `func_abstract = func.get("abstract", False)` → `emit_as_val = func_trusted
or func_abstract` → a bodyless `val` with the contract is emitted (the EXISTING abstract-method
emission, `functions.py:653-654`). NO new Module 6 code for the member.

The conformance refinement goal lowers through the EXISTING `_emit_subtyping_goals` path
(`functions.py:794`): for each `overrides` entry, `_render_refinement_goal` emits
`goal <C__m>_refines_<p> : forall self: C, .... ((pre_P -> pre_C) /\ (post_C -> post_P))`. NO new
Module 6 code — the existing refinement-goal emitter is reused verbatim. The `assigns` refinement
(`assigns(C.m) ⊆ assigns(P.m)`) is NOT separately checked by the existing emitter (it checks pre
weakening + post strengthening); for the TY2 scope this is acceptable because a protocol member's
`assigns` is typically `\nothing` (a pure query) or matches the conforming method's. A future
enhancement could add the frame-refinement check.

### 2.2 Per-clause VC mapping (the load-bearing part)

| Clause | Static obligation | VC / mechanism |
|---|---|---|
| **P1** (protocol declaration) | `class P(Protocol)` synthesizes a contract interface | The marker record + `abstract` member functions. NO separate VC; the interface is the collection of member `val` decls. |
| **P1a** (members) | each member carries a contract (the refinement target) | Each member's `#@ ensures/requires` is emitted as the `val`'s spec. NO separate VC (the spec is assumed for the abstract `val` — this is the `abstract` flag's semantics: a sound uninterpreted op with a contract, NOT `\trusted`). |
| **P1b** (`@runtime_checkable` ignored statically) | the decorator has no static effect | The front-end does NOT consult `@runtime_checkable` for any static judgment. NO VC. |
| **P2** (per-method behavioural refinement, load-bearing) | `C conforms to P` iff each `P.m` is refined by `C.m` | One refinement goal per member, emitted by `_render_refinement_goal` under `--check-behavioral-subtyping`: `forall self: C, .... ((pre_P -> pre_C) /\ (post_C -> post_P))`. This IS the per-method contract-refinement VC (P2). |
| **P3** (non-conformance rejected) | a class missing a member or with a non-refining contract fails | (a) Missing member: a static error raised at front-end (§1.3 step 4 — `C` does not provide `m`). (b) Non-refining contract: the refinement goal is UNPROVABLE (Why3/SMT fails to discharge `pre_P -> pre_C` or `post_C -> post_P`), so verification FAILS. |
| **P4** (conformance is a per-method VC, NOT presence) | the conformance VC must NOT be discharged by any runtime presence check | The refinement goal is a WhyML FORMULA over the two contracts (discharged by SMT from the contract specs), NOT a runtime `hasattr`/`isinstance` check. The runtime shim (§3) performs NO signature check — it CANNOT discharge the refinement VC. NO-BLEND by construction. |
| **P5** (no-blend, static side) | the static conformance VC is independent of the runtime presence check | The refinement goal is a spec formula; the runtime `isinstance` (R3) is a `hasattr` loop. They are different WhyML terms — the runtime check cannot satisfy the static VC. The keystone no-blend witness (§5) is a class with method presence (passes runtime isinstance) but a non-refining contract (fails the static refinement goal). |

### 2.3 The lowering seam (concrete file changes)

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/functions.py` | **No change.** The existing `_emit_function` (`:620`) handles `abstract: True` (bodyless `val`); the existing `_emit_subtyping_goals` (`:794`) + `_render_refinement_goal` (`:816`) emit the per-member refinement goal from `overrides`. |
| `src/pycsl/module6_whyml/expressions.py` | **No change.** |
| `src/pycsl/core_ir_semantic.py` | **No change.** |

---

## 3. Shim contract (runtime plane: `src/pycsl_lib/typ/__init__.py`)

Per the two-plane spec §2 (R1–R7) and the no-blend rule (D1/D3), the runtime shim exposes
`@runtime_checkable` as an identity that performs **NO validation** — NO signature check, NO
contract check, NO attribute-type check. The real runtime `runtime_checkable(cls)` (S4) returns
`cls` unchanged after setting `_is_runtime_protocol = True` and installing the `hasattr`-loop
`__instancecheck__`; the shim models this as identity.

### 3.1 Shim surface

```python
# In src/pycsl_lib/typ/__init__.py — runtime_checkable decorator, Shimmed (R1–R7).

#@ ensures \result == val
def runtime_checkable(cls, val) -> int:
    return val
```

(The `-> int` return tag and `val` parameter are the existing PyCSL convention for opaque
runtime objects — the same convention `cast`/`Union`/`Literal`/`Final`/`TypedDict`/`NamedTuple`/
`overload` use. The WhyML model is `int`-typed and the runtime object is opaque to the verifier;
this is the established Modelled-for-identity pattern. The `val` parameter carries the identity
postcondition. The real runtime `runtime_checkable(cls)` returns `cls` after installing the
presence-only `__instancecheck__` (S4); the shim models this as identity — it performs NO
signature/contract/presence check (R4/R6).)

### 3.2 Contract discharges each R-clause

| R-clause | How the shim honours it |
|---|---|
| R1 (plain class) | The shim does not modify the class object — a `class P(Protocol)` is a plain class at runtime; the shim's identity models `runtime_checkable` returning `cls` unchanged. |
| R2 (no isinstance by default) | A non-`@runtime_checkable` protocol's `isinstance` raising `TypeError` is runtime behaviour outside the verified surface; the shim does not model it. |
| R3 (runtime_checkable isinstance is PRESENCE-ONLY) | The shim's `#@ ensures \result == val` carries ONLY the identity postcondition. It does NOT model the `hasattr` loop (that would require modelling runtime attribute presence — outside the TY2 scope). The shim performs NO signature check — a shim that DID check signatures would be unfaithful (R4). |
| R4 (no validation in the shim) | The shim performs NO check on whether an object conforms to the protocol's full signature. A shim that DID check would be unfaithful in exactly the way an over-strong axiom is (D1). |
| R5 (isinstance result is a plain bool) | Not modelled in the TY2 scope (a `hasattr` loop over runtime attributes is outside the verified surface). |
| R6 (no static conformance at runtime) | The runtime does NOT perform the static conformance check (P2). The shim's identity postcondition cannot discharge any refinement VC. |
| R7 (the protocol class is a plain class) | The runtime plane of a protocol class (beyond `@runtime_checkable`) is the plain-class plane; the shim's only job is the decorator object. |

### 3.3 Why the runtime shim does NOT discharge any static clause

This is the GT7 no-blend rule (D1) made concrete: the shim's `ensures \result == val` is
SATISFIED by every value regardless of type or conformance. The static clauses P2/P4 are
discharged by Why3/SMT over the refinement goal `((pre_P -> pre_C) /\ (post_C -> post_P))` (§2.2),
which is a formula over the two method contracts — invisible to the shim. A conformance-agent
authoring the S5 subset from the two-plane spec + the shim surface alone cannot reverse-engineer
the lowering — the independence-based Gate C (c) holds. The keystone: a class with method
PRESENCE (passes a runtime `hasattr` check) but a NON-refining contract FAILS the static
refinement goal — the runtime presence cannot rescue the static conformance.

---

## 4. Classification (`--soundness-report`)

Per the two-plane spec §4, the classification is **dual** (both planes, separately):

| Plane | Classification | Tag |
|---|---|---|
| Static | **Interpreted** | the `Protocol` class is consumed by the static plane and lowered to a contract interface (marker record + `abstract` member `val`s); conformance `C conforms to P` is checked per-method as a refinement goal over `overrides` (per §2.2) |
| Runtime | **Shimmed** | the runtime meaning is the plain-class behaviour plus, when `@runtime_checkable`, the presence-only `isinstance` (a `hasattr` loop), no enforcement (per §3) |

### 4.1 GT gap codes tagged for `Protocol`

- **GT7** (THIS IS the canonical GT7 trap, not an analogue) — D1 documents the
  `@runtime_checkable` presence-vs-conformance divergence: the static P2/P4 per-method
  contract-refinement obligation must NOT be discharged by any runtime `isinstance`/`hasattr`
  presence check (R3 is attribute presence, a value check, NOT the contract-refinement type
  judgment). Tagged in the report as a `no_blend_protocol_presence` note.
- **GT8** — the S5 conformance subset for `Protocol` is the conformance-agent's standing
  artifact (NOT this DRAFT's deliverable). Each clause P2–P5 above names the S5 case shape it
  commits to.

No other GT gap is tagged for `Protocol` at TY2. Generic protocols (`Protocol[T]`) are TY3.

---

## 5. Standing gate plan (total additivity)

Per `typing-global-impl.md` §4 Gate B and the core-agent's hard rules:

### 5.1 Byte-identical emission for unaffected drivers

- The `_is_protocol_class` check is a pure base-name test: for any class that does NOT list
  `Protocol` as a base, `visit_ClassDef` proceeds exactly as before. Every non-Protocol driver
  produces byte-identical IR and byte-identical WhyML.
- The `_protocols` dict is empty for every module that has no `class P(Protocol)`; the
  conformance-`overrides` population is a no-op for classes without `csl_conforms_to`.
- The `conforms_to_decl` grammar rule is additive: a `#@ conforms_to` directive is recognized
  ONLY when the keyword is present; every existing `#@` directive is unaffected.
- The corpus byte-diff gate (`bin/byte-diff-sweep.sh`) MUST remain green for every non-Protocol
  driver. A byte-diff on an unaffected driver is a regression.

### 5.2 `os` proof + `formal_<name>` suite re-confirmed

- The `os` library (now fully green) does NOT use `Protocol`/`@runtime_checkable`/`conforms_to`
  in its verified surface — confirm by `rg 'Protocol|runtime_checkable|conforms_to'
  src/pycsl_lib/os/` before claiming additivity. (Expected: zero matches in verified code; any
  match is a comment-only reference.)
- The `formal_<name>` suite (json, re, warnings, …) is re-run; every previously-green formal
  test MUST remain green.

### 5.3 IR-conformance corpora

- **No IR_VERSION bump.** The `Protocol` construct reuses the EXISTING `abstract` function flag
  + the EXISTING `overrides` IR list, and adds a record-level `is_protocol: True` boolean (same
  shape as `is_typeddict`/`is_namedtuple`, which did NOT bump the version). NO new IR node, NO
  new wire-format field. The IR schema is unchanged; `IR_VERSION` stays at `1.3`;
  `ACCEPTED_IR_VERSIONS` is unchanged. The IR-conformance corpora (core + front-end `*.ir.json` /
  `*.expected.mlw`) MUST remain green unchanged for every non-Protocol driver.

### 5.4 doc-coherency green

- `test-suite/annotations.md`: add the canonical entry for the `Protocol` + `@runtime_checkable` +
  `#@ conforms_to` annotation surface (citing S2 PEP 544). Per `pycsl-doc-coherency` skill, the
  entry must also appear in `docs/pycsl-concrete-syntax-reference.md`,
  `docs/pycsl-static-semantics-reference.md`, `docs/pycsl-translational-reference.md`, and a
  `config/skills/` skill (`pycsl-annotate`). `bin/doc-coherency.py --check` MUST remain green.

### 5.5 Non-vacuity gate

- The conformance refinement goal (P2 — `((pre_P -> pre_C) /\ (post_C -> post_P))`) is a real
  Why3 goal. `--check-vacuity` MUST be green on it. A false-twin (an impossible `post_C` under
  `pre_P`) MUST FAIL — confirming the refinement goal is non-vacuous. The protocol member's
  `abstract` `val` is exempt from vacuity (it is a spec, not a body VC — the same exemption
  `abstract`/`trusted` already enjoy).

---

## 6. NoReturn × vacuity gate

**N/A for `Protocol`.** The NoReturn × vacuity interaction is owned by the `NoReturn` construct's
spec. `Protocol` does not interact with the vacuity gate in the NoReturn-specific way. (A protocol
member annotated `-> NoReturn` would be an abstract `val` with `ensures { false }` — a legitimate
spec, not a vacuity signal — but the TY2 conformance subset does not exercise this combination.)

---

## 7. Deliverable checklist (on APPROVAL)

- [ ] Front-end: `_protocols` init, `_is_protocol_class`, `_emit_protocol_interface`,
      conformance-`overrides` population in `Module5_IREmitter.py`.
- [ ] Parser: `ConformsToDecl` + `conforms_to_decl` grammar rule + transformer in
      `Module2_Parser.py`.
- [ ] Weaver: harvest `ConformsToDecl` onto `node.csl_conforms_to` in `Module3_Weaver.py`.
- [ ] Module 6: NO change (reuses `abstract` emission + `overrides` refinement-goal emitter).
- [ ] `core_ir_semantic.py`: NO change.
- [ ] `src/pycsl_lib/typ/__init__.py`: `runtime_checkable` shim annotated with identity
      `ensures \result == val`.
- [ ] `test-suite/annotations.md` (§12.15) + three reference docs;
      doc-coherency green.
- [ ] `--soundness-report`: `Protocol` classified Interpreted (static) /
      Shimmed (runtime), GT7 `no_blend_protocol_presence` note documented.
- [ ] Standing gate: corpus byte-diff green for non-Protocol drivers;
      `os` proof SUCCESS; formal suite SUCCESS; NO IR_VERSION bump;
      `--check-vacuity` green on the conformance refinement goals.
- [ ] NO conformance-suite or shim-faithfulness-driver edits beyond the
      conformance-agent's own artifacts.
