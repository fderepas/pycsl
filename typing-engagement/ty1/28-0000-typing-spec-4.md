# 28-0000-typing-spec-4.md — `NoReturn` Implementation Spec (DRAFT → DONE)

**Status:** DONE (core-agent implemented both planes; standing gate green).
**Tier:** TY1 (monomorphic refinements).
**Construct:** `NoReturn` (PEP 484 `-> NoReturn` / `-> typing.NoReturn`).
**Two-plane spec authority:** `typing-engagement/ty1/noreturn-twoplane-spec.md` (APPROVED).
**Global guides honoured:** `typing-global-impl.md` §0/§5 item 2 ("NoReturn × the
non-vacuity gate — the sharpest new TY1 obligation"), §4 (per-construct pipeline +
gates); `docs/typing-global-overview.md` §4.2 (TY1 lowering locus = front-end
normalization + `core_ir_semantic` static-semantics seam + Module 6 lowering).
**Sound expressibility reminder (overview §2.1):** the IR/WhyML lower bound may be
STRICTER than S1, never weaker. `NoReturn` is fully sound — the `false` postcondition
is a genuine proof obligation (the body must raise or diverge), not an unsoundness.
**No-blend reminder (overview §2.3 / NR-D2):** the static-plane `false` postcondition
(§1 of the two-plane spec) and the runtime-plane alias-object/no-enforcement behaviour
(§2) are carried as SEPARATE contracts. The runtime shim must NOT enforce divergence
(NR-R3) — that would blend the planes.

**This is a planning document.** On coordinator APPROVAL, the core-agent implements both
planes and runs the standing gate.

---

## 0. Design summary (one paragraph)

`-> NoReturn` (PEP 484) is **lowered at the front-end normalization seam** to a `false`
postcondition: the function never returns normally (it raises or diverges). The front-end
(`Module5_IREmitter._build_function_ir`) recognizes `NoReturn` (Name) and `typing.NoReturn`
(Attribute) in the return annotation and sets a new optional IR flag `is_noreturn: true`
(IR v1.3, additive — emitted ONLY when true, so every non-NoReturn driver stays
byte-identical). Module 6 (`functions.py:_emit_contracts`) emits `ensures { false }` (NR1).
The static semantics (`core_ir_semantic._check_noreturn`) checks the body supports divergence
(NR2a — no `Return`, at least one `Raise`/diverging construct) and `_check_noreturn_successors`
flags dead code after a NoReturn call (NR3). The non-vacuity gate (`pycsl.py:_run_vacuity_gate`)
EXEMPTS declared-NoReturn functions from the vacuity probe (NR4) — keyed on the IR
`is_noreturn` flag (from the `-> NoReturn` annotation), NOT on the inferred `false`
postcondition. The runtime plane is a thin shim (`src/pycsl_lib/typ/__init__.py`) that provides
the introspectable `NoReturn` alias object and performs NO enforcement (NR-R1–NR-R5).

### 0.1 Why `ensures { false }` and not the `diverges` effect

The two-plane spec §1.0 NR2 notes the `false` postcondition is *equivalent* in meaning to the
`diverges` IR flag, but the two are NOT interchangeable at the WhyML level: `diverges` means
the function may not terminate (infinite loop), while `ensures { false }` means the function
never reaches a normal exit (it may RAISE — which terminates, but exceptionally). A NoReturn
function that always raises is NOT diverging (it terminates via exception) but DOES satisfy
`ensures { false }`. Setting `diverges: true` would be WRONG for a raising body (Why3 rejects
the `diverges` effect on a body with no diverging construct — `_check_diverges` enforces this).
The correct lowering is `ensures { false }` (NR1), which discharges by the ABSENCE of a
normal-exit path. NR2a is a NEW check (not a reuse of `_check_diverges`): it accepts a body
that raises (which `_check_diverges` would reject if `diverges` were set).

### 0.2 What is introduced

- **New optional IR field** `is_noreturn: bool` on `FunctionIR` (IR v1.3, additive). Emitted
  ONLY when `true` → byte-identical for every non-NoReturn driver (verified: 38 conformance
  goldens byte-identical, 38 VERSION-SKEW `1.2 → 1.3`). See §6.
- **New Module 6 emission**: `ensures { false }` appended to the contract when `is_noreturn`
  is true (NR1). See §3.
- **New static-semantics checks**: `_check_noreturn` (NR2a, per-function) and
  `_check_noreturn_successors` (NR3, module-level). See §4.
- **Vacuity-gate exemption** (NR4): `_run_vacuity_gate` skips functions whose IR carries
  `is_noreturn: true`. See §5.
- **Runtime shim**: `NoReturn` alias object in `src/pycsl_lib/typ/__init__.py`. See §7.

### 0.3 What is NOT introduced

- **No `\trusted`.** The `false` postcondition is a real proof obligation, discharged by the
  body's absence of a normal exit. Sound expressibility is STRICTER than S1 (NR2a's
  conservative rejection of any `Return`), never weaker.
- **No new VC kind.** `ensures { false }` is the SAME goal shape the non-vacuity gate injects
  (`ensures { [@expl:vacprobe] false }`); the gate's NR4 exemption is what distinguishes a
  NoReturn `false` (the spec) from a vacuous `false` (an inconsistent context).
- **No runtime enforcement.** The shim provides the alias object; it does NOT check divergence
  (NR-R3 — the central negative sentence). The static `false` postcondition is NOT discharged
  by the runtime (NR-D2 no-blend).

---

## 1. Static-plane clause mapping (two-plane spec §1 → implementation)

| Clause | Spec text (summary) | Implementation | Discharge |
|--------|---------------------|----------------|-----------|
| **NR1** | `false` postcondition — never returns normally | `functions.py:_emit_contracts` emits `ensures { false }` when `func_is_noreturn` | VC: the body has no normal-exit path (raises/diverges) → `false` vacuously holds |
| **NR2** | equivalent to the `diverges` flag | NOT used (see §0.1 — `ensures { false }` is the correct spelling for a raising body) | n/a |
| **NR2a** | body must support divergence | `core_ir_semantic._check_noreturn`: reject if body has a `Return` OR lacks `Raise`/diverging construct | static error `PYCSL-SEM-NORETURN` (before Why3) |
| **NR3** | dead-code report on the successor | `core_ir_semantic._check_noreturn_successors`: flag any statement after a NoReturn call | static error `PYCSL-SEM-NORETURN` (before Why3) |
| **NR4** | vacuity-gate exemption | `pycsl.py:_run_vacuity_gate` skips functions in the `noreturn_names` set (built from IR `is_noreturn`) | gate skips the probe; a genuinely-vacuous function is still probed |

---

## 2. Front-end normalization (Module 5)

`_build_function_ir` (`Module5_IREmitter.py:2291`) recognizes two surface forms:

- **`-> NoReturn`** — `ast.Name(id="NoReturn")` in `node.returns`.
- **`-> typing.NoReturn`** — `ast.Attribute(value=Name("typing"), attr="NoReturn")`.

On recognition: `is_noreturn = True`, `return_annotation = None` (no return-value type —
the body never reaches a normal exit). The IR dict carries `is_noreturn: True` ONLY when
true (via `**({"is_noreturn": True} if is_noreturn else {})`), so every non-NoReturn
function's IR is byte-identical to the v1.2 emission.

---

## 3. Module 6 lowering (NR1)

`functions.py:_emit_contracts` gains a `func_is_noreturn: bool = False` parameter. When
true, it appends `    ensures { false }` AFTER the user-written ensures (the `false`
postcondition is the NoReturn claim, additional to any explicit contract). The return type
defaults to `unit` (no `Return` statement → `find_return_type` yields `int`, but the body
has no normal exit so the type is irrelevant; Why3 accepts `ensures { false }` with any
return type).

Emission (verified on the 0738 witness):
```
  let f () : unit
    ensures { false }
    raises { Exception }
  =
    raise Exception
```

---

## 4. Static semantics (NR2a + NR3)

### 4.1 NR2a — `_check_noreturn` (per-function, in `run_ir_semantic_checks`)

Two conservative sound conditions (stricter than S1 is permitted):

1. **No `Return`** — `_body_has_return(body)` walks the IR for any `Return` statement (any
   depth). A `Return` is a normal-exit path → `PyCSLSemanticError` (code `PYCSL-SEM-NORETURN`).
   Even a `Return` inside a provably-dead branch is rejected (sound — a dead `Return`
   indicates a logic error).
2. **At least one `Raise` or diverging construct** — if the body has no `Raise`
   (`_body_has_raise`) and no diverging construct (`_body_has_diverging_construct`: `While`/
   `For`/`CriticalSection`/`Call`), it provably falls off the end → rejected.

Why3 provides defense-in-depth: if a normal-exit path slips past this check, the
`ensures { false }` VC fails at proof time.

### 4.2 NR3 — `_check_noreturn_successors` (module-level)

Builds the set of NoReturn function names (`_collect_noreturn_names`), then walks each
function body's statement lists (top-level + nested `If`/`While`/`For`/`Try`/`Match` bodies).
When a statement is a bare-expression `Call` (`{"stmt": "Expr", "value": {"type": "Call",
"func": <name>}}`) to a NoReturn function, the NEXT statement in the same block is flagged as
dead code → `PyCSLSemanticError` (code `PYCSL-SEM-NORETURN`).

---

## 5. The vacuity-gate exemption (NR4) — the load-bearing clause

`_run_vacuity_gate` (`pycsl.py:829`) gains a `noreturn_names: Optional[Set[str]]` parameter.
At the call site (`_gate_vacuity_then_succeed`), the set is built from the IR:

```python
from module6_whyml.identifiers import whyml_ident
_nr_names = {whyml_ident(f["name"]) for f in ir_data["functions"] if f.get("is_noreturn")}
```

In `_probe_one`, the FIRST check is:
```python
if fname in skip:
    return fname, False   # exempt — the `false` post is the SPEC, not a vacuity signal
```

The exemption is keyed on the IR `is_noreturn` flag (which comes from the `-> NoReturn`
annotation), NOT on the inferred `false` postcondition — the latter would exempt every
genuinely-vacuous function, defeating the gate. A genuinely-vacuous function (inconsistent
context, no NoReturn annotation) is still probed and flagged (verified on the
`/tmp/vacuous_witness.py` driver).

---

## 6. IR_VERSION bump (1.2 → 1.3, additive)

- `ir_schema.py`: `IR_VERSION = "1.3"`, `ACCEPTED_IR_VERSIONS = {"1.0", "1.1", "1.2", "1.3"}`.
- `FunctionIR` TypedDict gains `is_noreturn: bool` (optional — `total=False`).
- The field is ABSENT on non-NoReturn functions (emitted only when true) → a `"1.0"`/`"1.1"`/
  `"1.2"` IR without it remains byte-identical and ingestable.
- `docs/ir.md` §2/§5/§10 document the bump and the new field.
- Conformance goldens: 38 core OK / 0 MISMATCH (byte-identical WhyML); 38 frontend OK /
  0 MISMATCH / 38 VERSION-SKEW (`1.2 → 1.3`, content identical). No golden refresh needed.

---

## 7. Runtime shim (NR-R1–NR-R5)

`src/pycsl_lib/typ/__init__.py` gains:
```python
NoReturn = None   # introspectable alias; runtime does not enforce (NR-R3)
```

`NoReturn` is a type marker, not a callable — it appears only in return annotations
(`-> NoReturn`), never as a value. The shim provides the name (introspectable, NR-R1/NR-R2)
with NO enforcement (NR-R3 — the runtime does not enforce divergence; NR-D2 no-blend). The
static plane handles the `false` postcondition (NR1); the runtime plane does nothing.

---

## 8. Docs + annotations

- `test-suite/annotations.md` §12.11 — NoReturn entry (surface, static plane, runtime plane,
  IR_VERSION bump, GT gap, tests).
- `docs/pycsl-concrete-syntax-reference.md` — `Attribute` annotation form (`-> typing.NoReturn`)
  in §11.1; NR2a/NR3 rejection in §11.2.
- `docs/pycsl-static-semantics-reference.md` — τ(NoReturn) = unit in §1.4; §2.5b NoReturn
  body-supports-divergence rule.
- `docs/pycsl-translational-reference.md` — §T.14.8 NoReturn lowering.
- `docs/ir.md` §2/§5/§10 — IR_VERSION 1.3, `is_noreturn` field.
- Reference tests: 0738 (NR1/NR2a witness), 0739 (NR2a negative), 0740 (NR3 negative),
  0741 (NR4 vacuity exemption).

---

## 9. Standing gate (run + results)

| # | Gate | Command | Result |
|---|------|---------|--------|
| 1 | os proof | `python3 src/pycsl/pycsl.py src/pycsl_lib/os/__init__.py` | **SUCCESS** |
| 2 | formal test | `python3 src/pycsl/pycsl.py src/pycsl_lib_test/formal_os_pure.py` | **SUCCESS** |
| 3 | doc-coherency | `python3 bin/doc-coherency.py --check` | **green** |
| 4 | NoReturn witness | `def f() -> NoReturn: raise Exception()` → `ensures { false }` | **VCs discharge** |
| 5 | Vacuity exemption | `pycsl --check-vacuity <noreturn_witness>` | **PASSES (exempted)** |
| 6 | Genuinely-vacuous flagged | `requires x>0 /\ x<=-1` (no NoReturn) `--check-vacuity` | **FAILS (flagged)** |
| 7 | NR3 unreachable successor | `f(); return 1` (f is NoReturn) | **reported as dead** |
| 8 | NR2a normal-return rejected | `def f() -> NoReturn: return 1` | **rejected (PYCSL-SEM-NORETURN)** |
| 9 | IR conformance (core) | `bin/core-only-conformance.py` | **38 OK / 0 MISMATCH** |
| 10 | IR conformance (frontend) | `bin/frontend-only-conformance.py` | **38 OK / 0 MISMATCH / 38 VERSION-SKEW** |

---

## 10. Files changed

**Source:**
- `src/pycsl/ir_schema.py` — IR_VERSION 1.2 → 1.3, ACCEPTED_IR_VERSIONS + "1.3", `is_noreturn` field.
- `src/pycsl/frontend/Module5_IREmitter.py` — recognize `-> NoReturn` / `-> typing.NoReturn`, set `is_noreturn`.
- `src/pycsl/module6_whyml/functions.py` — emit `ensures { false }` when `is_noreturn` (NR1).
- `src/pycsl/core_ir_semantic.py` — `_check_noreturn` (NR2a), `_check_noreturn_successors` (NR3).
- `src/pycsl/pycsl.py` — NR4 vacuity-gate exemption (`noreturn_names` skip-set).
- `src/pycsl_lib/typ/__init__.py` — `NoReturn` alias shim.

**Docs:**
- `test-suite/annotations.md` — §12.11 NoReturn.
- `docs/pycsl-concrete-syntax-reference.md` — §11.1 Attribute form, §11.2 NR2a/NR3 rejections.
- `docs/pycsl-static-semantics-reference.md` — τ(NoReturn), §2.5b.
- `docs/pycsl-translational-reference.md` — §T.14.8.
- `docs/ir.md` — §2/§5/§10 IR_VERSION 1.3 + `is_noreturn`.

**Tests:**
- `test-suite/corpus/pycsl-reference/0738.py` — NR1/NR2a witness.
- `test-suite/corpus/pycsl-reference/0739.py` — NR2a negative.
- `test-suite/corpus/pycsl-reference/0740.py` — NR3 negative.
- `test-suite/corpus/pycsl-reference/0741.py` — NR4 vacuity exemption.

---

## 11. Gap docs

**No gap.** `NoReturn` is SOUND: the `false` postcondition is a genuine proof obligation
(the body must raise or diverge — NR2a enforces this statically, and Why3 provides
defense-in-depth via the `ensures { false }` VC). No GT gap is tagged (the two-plane spec §4
confirms full soundness). The NR4 vacuity-gate exemption is a gate-precision concern
(prevents a false POSITIVE — flagging a faithful NoReturn function), not a soundness gap.

**NR2a strictness note:** the conservative rejection of any `Return` statement (even in a
provably-dead branch) is stricter than S1 (PEP 484 does not require this). This is the
permitted "stricter than S1, never weaker" direction. A future refinement could perform
precise reachability analysis to accept a `Return` inside a dead branch, but no driver
demands it today.
