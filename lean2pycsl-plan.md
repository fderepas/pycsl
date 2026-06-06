# `lean2pycsl` — Engineering Plan

A tool that treats a Lean 4 `.lean` file as the *specification source* and
emits PyCSL `#@` annotations onto a hand-ported Python implementation,
then asks PyCSL/Why3/SMT to re-discharge the obligations independently.

Same trust model as `rocq2pycsl`: the Lean proof is **not transported**
into Why3. It is a trusted oracle for *what the contracts should say*.
The SMT recheck replaces refinement.

Targets **Lean 4 + mathlib4**. Lean 3 is deprecated and not supported.

---

## 1. Goals and non-goals

**Goals**

- Given a Lean function `f` and a Python function `f` with matching
  arity, produce a copy of the Python file with PyCSL annotations on `f`
  whose logical content matches the Lean theorems about `f`.
- Discharge those annotations by invoking the PyCSL pipeline as a final
  round-trip check.
- Preserve the user's Python formatting, comments, and unrelated code
  untouched.
- Use Lean's native attribute system (`@[pycsl_spec ...]`) as the
  primary spec-selection mechanism — no comment markers, no fragile
  heuristics.

**Non-goals (v1)**

- Generating loop invariants from inductive Lean proofs.
- Translating Lean proof terms into Why3 proof tasks.
- Supporting theorems stated over arbitrary type classes (e.g.
  `GCDMonoid`); only concrete `Nat`/`Int`/`Bool` developments.
- Higher-order quantification, dependent pattern matching, universe
  polymorphism.
- Generating the Python body.

---

## 2. Architecture

```
lean2pycsl/
├── lean_side/              # NEW — small Lean library
│   ├── PycslExport.lean    # defines @[pycsl_spec] attribute
│   └── lakefile.lean       # builds as a Lean dependency
├── extractor/              # Phase 1: get IR out of Lean
│   ├── runner.py           # invokes `lake env lean --run export.lean`
│   ├── json_parser.py      # reads Lean's JSON output
│   └── selector.py         # filters by attribute / config
├── ir/                     # IR: identical to rocq2pycsl
│   ├── nodes.py
│   └── pretty.py
├── translator/             # Phase 2: IR -> PyCSL expression strings
│   ├── lean.py             # the main rewriter
│   ├── opmap.py            # Lean operator -> PyCSL operator
│   ├── divides.py
│   ├── typeclass.py        # detect/reject type-class-polymorphic theorems
│   └── names.py
├── emitter/                # Phase 3: rewrite the Python source
│   ├── locator.py          # libcst-based def finder
│   ├── annotator.py
│   └── checker.py
├── config/
│   ├── schema.py
│   └── load.py
├── cli.py
└── tests/
    ├── golden/
    └── unit/
```

**Data flow** (note how much simpler this is than the SerAPI version):

```
.lean file ─┐
            ├─> Lean script ─> JSON ─> IR ─> PyCSL expr strings ──┐
attribute ──┘                                                     │
   tag                                                            ▼
                              .py file ──> libcst tree ──> annotated .py
                                                                  │
                                                                  ▼
                                                                pycsl
                                                                  │
                                                                  ▼
                                                         verification report
```

The crucial architectural difference vs. `rocq2pycsl`: extraction happens
**inside Lean**, not via an external protocol. We write a Lean 4 script
that iterates through all declarations carrying `@[pycsl_spec]` and
dumps their elaborated types as JSON. The Python tool then reads JSON.

---

## 3. Phase plan with milestones

### Phase 0 — Scaffold (1 day)

- Project layout, `pyproject.toml` (Python), `lakefile.lean` (Lean).
- Dependencies: `libcst`, `typer`, `tomli`, `pytest` (Python);
  Lean 4 toolchain (system).
- Smoke test: build the Lean side via `lake build`, invoke it on a
  trivial `.lean` file, get JSON back.

### Phase 1 — Lean extraction (3–4 days)

Goal: given a `.lean` file with `@[pycsl_spec]` tags, return a JSON list
of `{name, statement, kind, ...}` entries.

Substeps:

1. **Define the attribute** in `PycslExport.lean`:

   ```lean
   import Lean
   open Lean

   syntax (name := pycslSpec) "pycsl_spec" ident : attr

   initialize pycslSpecExt :
     PersistentEnvExtension (Name × Name) (Name × Name) (Array (Name × Name)) ←
     registerPersistentEnvExtension { ... }

   initialize registerBuiltinAttribute {
     name := `pycslSpec
     descr := "Marks a theorem as a PyCSL spec for function <ident>"
     add := fun decl stx kind => do
       let funName ← match stx with
         | `(attr| pycsl_spec $name) => pure name.getId
         | _ => throwError "invalid syntax"
       modifyEnv (pycslSpecExt.addEntry · (funName, decl))
   }
   ```

2. **Write the export command** that dumps every tagged decl's type:

   ```lean
   open Lean Elab Command in
   elab "#pycsl_export" : command => do
     let env ← getEnv
     let entries := pycslSpecExt.getState env
     let out : Array Json ← entries.mapM fun (funName, thmName) => do
       let info ← getConstInfo thmName
       return Json.mkObj [
         ("function", funName.toString),
         ("theorem", thmName.toString),
         ("type", ← ppExpr info.type |>.run' |>.toString),
         ("type_json", toJson info.type)  -- structured form
       ]
     IO.println (Json.arr out).pretty
   ```

3. **Run it from the Python side** via
   `lake env lean --run lean_side/Export.lean`.

4. **Parse the JSON** into the IR. Lean's `Expr` representation in
   JSON is verbose but mechanical; the Python `json_parser.py` walks it.

5. Anything outside the supported subset becomes
   `IR.Unsupported(reason, raw_expr)`.

Deliverable: `extractor.load("Euclid.lean")` returns the IR for the
`@[pycsl_spec]`-tagged theorems.

### Phase 2 — IR → PyCSL translation (1 week)

Same shape as `rocq2pycsl` Phase 2, with these Lean-specific concerns:

1. **Strip instance arguments.** Lean elaborates `gcd_dvd_left` as
   `∀ {inst : Decidable ...} (a b : Nat), gcd a b ∣ a` or similar.
   The instance binders (`{...}`) are not user-visible and must be
   stripped before translation.
2. **Strip implicit binders** that are not the function's parameters.
   The function's *explicit* parameter list determines what gets
   absorbed into PyCSL parameter scope.
3. **Reject type-class quantification.** A theorem like
   `∀ [GCDMonoid α] (a b : α), gcd a b ∣ a` is too abstract: we don't
   know how to translate `GCDMonoid` operations into Python. Surface
   a clear error and ask the user to either provide a concrete
   instance or supply a manual contract.
4. **Translate `Nat` quantification** to `int >= 0` constraints (same
   as Rocq's `nat`).
5. **Detect `\result`** the same way as in `rocq2pycsl`: after
   parameter absorption, each application of the function symbol to
   the absorbed parameters becomes `\result`.

Deliverable: `translator.render(theorem_ir, mapping)` produces correct
PyCSL strings for the corpus in §9.

### Phase 3 — Python rewriter (4–5 days)

**Identical to `rocq2pycsl` Phase 3.** The Python side is unchanged.
This entire phase can be shared between the two tools — extract it as a
common library `pycsl_emit`.

### Phase 4 — Verification round-trip (2 days)

**Identical to `rocq2pycsl` Phase 4.** Shared with the common library.

### Phase 5 — Configuration and UX (2 days)

Smaller than Rocq's because the attribute system carries most of the
spec-selection burden. The TOML config only needs:

- Identifier remapping (Lean's `a`, `b` may be Python's `x`, `y`).
- Divides translation style (`operational` vs `exists`).
- pycsl invocation flags.
- Optional: list of additional theorems to include even without the
  `@[pycsl_spec]` tag (escape hatch).

### Phase 6 — Test corpus (parallel from Phase 2)

Same corpus as `rocq2pycsl` §9, plus:

- A test that confirms `@[pycsl_spec]` tagging works correctly when
  multiple theorems mention the same function.
- A test that confirms theorems with type-class parameters are
  rejected with a clear error.
- A test using a definition with `termination_by` to confirm the
  `\variant` extraction.

---

## 4. The IR

**Identical to `rocq2pycsl` §4.** Shared with the common library.

---

## 5. Translation rules

### 5.1 Logical and arithmetic operators

| Lean (Unicode) | Lean (ASCII) | PyCSL |
|---|---|---|
| `∀ x : T, P` | `forall x : T, P` | `\forall x; P` |
| `∃ x : T, P` | `exists x : T, P` | `\exists x; P` |
| `P → Q` | `P -> Q` | `P ==> Q` (when `P : Prop`) |
| `P ∧ Q` | `P /\ Q` | `P and Q` |
| `P ∨ Q` | `P \/ Q` | `P or Q` |
| `¬P` | `Not P` | `not P` |
| `P ↔ Q` | `P <-> Q` | `P <==> Q` |
| `True`, `False` | `True`, `False` | `True`, `False` |
| `a = b` | `a = b` | `a == b` |
| `a ≠ b` | `a ≠ b` | `a != b` |
| `a ≤ b`, `a < b`, etc. | `a <= b`, `a < b` | same |
| `a + b`, `a - b`, `a * b` | same | same |
| `a / b` (for `Nat`) | same | `a // b` |
| `a % b` | same | `a % b` |
| `f a b` (pure) | same | `f(a, b)` |
| `a ∣ b` (divides) | `a ∣ b` (no ASCII) | `b % a == 0` (see §5.2) |

**Win vs Rocq plan:** Lean's `a % b` and Python's `a % b` are
syntactically identical. No translation needed beyond confirming the
arguments are integers.

### 5.2 Divisibility

Lean's `a ∣ b` is defined as `∃ c, b = a * c` — same as Coq. The
same trade-off applies: operational form (`b % a == 0`) is what SMT
prefers; existential is more faithful. Apply the same guarded
translation as `rocq2pycsl` §5.2.

**Watch out:** Lean's `∣` is Unicode (U+2223), distinct from regular
pipe `|`. The Lean `Expr` JSON encodes it as `HDvd.hDvd a b` or
`Dvd.dvd a b`. Detect both forms.

### 5.3 Quantifier scoping

Same as `rocq2pycsl` §5.3: outer `∀` binders matching the target
function's explicit parameter list are absorbed into PyCSL parameter
scope.

**Lean-specific subtlety:** Lean's elaborated `Expr` will have
*implicit* binders interleaved with explicit ones. Strip implicit and
instance-implicit binders before binder absorption. If after stripping
the explicit binder list doesn't match the function's parameter list
in order and type, error out — don't try to be clever.

### 5.4 `\result`

Same as `rocq2pycsl` §5.4.

### 5.5 Variant

Lean's termination machinery:

- `termination_by f a b => <expr>` — extract `<expr>` (with `a`, `b`
  substituted in scope) and emit `#@ \variant <expr>`.
- Structural recursion (no `termination_by`): no variant needed; PyCSL
  will infer termination from the recursion pattern, or the user supplies
  one manually.
- `decreasing_by` provides the proof and is ignored by the tool —
  Why3 will re-prove decrease independently.
- `partial def` (no termination check) → emit `#@ \diverges`.

### 5.6 Purity

For v1, any `def` (not `partial def`) without effect monads (`IO`,
`StateM`, etc.) is treated as pure: emit `#@ assigns \nothing`. Monadic
defs are unsupported.

### 5.7 Type-class arguments

Theorems carrying `[Inst : SomeClass α]` parameters are rejected unless:

- The instance can be specialized to a concrete type the tool knows
  (e.g. `Nat`, `Int`), AND
- The user provides a config entry mapping the class operations to
  PyCSL/Python expressions.

This is the most likely source of friction with mathlib4-stated theorems.
Most "interesting" mathlib theorems are stated over generic algebraic
structures, not concrete `Nat`/`Int`. Users will frequently need to
either:

- Find or prove a concrete `Nat`-specialized version of the theorem, or
- Write the theorem statement concretely in their own file with the
  `@[pycsl_spec]` tag.

---

## 6. Configuration

`lean2pycsl.toml`:

```toml
[input]
lean    = "Proofs/Euclid.lean"
python  = "src/euclid.py"
output  = "src/euclid.annotated.py"

[lean]
lake_project = "."             # path to lakefile.lean
imports      = ["Mathlib.Data.Nat.GCD.Basic"]

[functions.gcd]
python_name      = "gcd"
arg_map          = { a = "a", b = "b" }
divides_style    = "operational"
# spec_theorems intentionally omitted: discovered via @[pycsl_spec gcd]

[functions.gcd.extra_specs]
# escape hatch for theorems lacking the attribute
include = ["Nat.gcd_comm"]

[pycsl]
extra_flags = ["--memory-model", "hoare"]
prover      = "Alt-Ergo,2.6.2,"
```

Selection precedence:

1. `@[pycsl_spec gcd]` attribute in Lean source (primary).
2. `[functions.gcd.extra_specs].include` in TOML (escape hatch).
3. **No heuristic mode.** Mathlib is too large; a heuristic would sweep
   in too many unrelated lemmas.

---

## 7. Worked example: GCD

Input `Euclid.lean`:

```lean
import Mathlib.Data.Nat.Basic
import PycslExport

namespace Euclid

def gcd : Nat → Nat → Nat
  | a, 0     => a
  | a, b + 1 => gcd (b + 1) (a % (b + 1))
termination_by _ b => b
decreasing_by simp_wf; exact Nat.mod_lt _ (Nat.succ_pos _)

@[pycsl_spec gcd]
theorem gcd_dvd_left : ∀ a b, gcd a b ∣ a := by sorry

@[pycsl_spec gcd]
theorem gcd_dvd_right : ∀ a b, gcd a b ∣ b := by sorry

@[pycsl_spec gcd]
theorem gcd_greatest : ∀ a b d, d ∣ a → d ∣ b → d ∣ gcd a b := by sorry

end Euclid
```

Input `euclid.py`:

```python
def gcd(a: int, b: int) -> int:
    if b == 0:
        return a
    return gcd(b, a % b)
```

Config:

```toml
[input]
lean   = "Euclid.lean"
python = "euclid.py"
output = "euclid.annotated.py"
```

Expected output:

```python
#@ requires a >= 0 and b >= 0
#@ ensures a % \result == 0
#@ ensures b % \result == 0
#@ ensures \forall d; (a % d == 0 and b % d == 0) ==> \result % d == 0
#@ assigns \nothing
#@ \variant b
def gcd(a: int, b: int) -> int:
    if b == 0:
        return a
    return gcd(b, a % b)
```

Notes on what happened:

- The `@[pycsl_spec gcd]` attribute on three theorems told the tool
  exactly what to translate. No heuristic, no config-side listing.
- `Nat` quantifiers produced the `requires a >= 0 and b >= 0`
  precondition automatically.
- `∀ a b, gcd a b ∣ a`: outer binders absorbed; `gcd a b` became
  `\result`; `_ ∣ a` translated via §5.2 to `a % \result == 0`.
- `termination_by _ b => b` produced `#@ \variant b`.
- `def` without effects produced `#@ assigns \nothing`.

The round-trip then invokes `pycsl euclid.annotated.py` and confirms
each obligation discharges.

---

## 8. Known limitations and explicit scope cuts (v1)

- **Type-class-polymorphic theorems.** Most mathlib theorems. User must
  specialize.
- **Inductive types in specs beyond `Nat`/`Int`/`Bool`.** Same as Rocq
  plan.
- **Higher-order quantification.** Rejected.
- **Dependent pattern matching.** Rejected.
- **Macros and custom syntax.** Lean 4 makes custom syntax very easy
  for users to add; the tool reads only the elaborated form, but
  user-defined notations that don't desugar to first-order content
  will be rejected.
- **`partial def` bodies** are accepted but produce `#@ \diverges` —
  PyCSL won't try to prove termination.
- **Loop invariants.** Not generated; user adds by hand on iterative
  Python forms.
- **Concurrency.** Out of scope.

---

## 9. Testing strategy

Same corpus as `rocq2pycsl` §9. Add Lean-specific tests:

- `@[pycsl_spec]` discovery across multiple files in a lake project.
- Rejection of type-class-quantified theorems with a clear error.
- `termination_by` extraction in both simple (`=> b`) and tupled
  (`=> (a, b)`) forms.
- A test using `partial def` to confirm `\diverges` emission.
- A test with Unicode (`∀`, `∣`, `≤`) and ASCII alternatives in the
  same file.

---

## 10. Open design questions

1. **Should the tool ship as a Lake dependency or a standalone Python
   package?** Lake dependency is more idiomatic for Lean users; standalone
   Python is easier to install for users who don't already have a Lake
   project. Probably both: the Lean side is a Lake dep, the Python
   side is `pip install lean2pycsl`.
2. **How to handle mathlib4's polymorphic specs?** Long-term, build a
   small "concretization" library: pre-proven `Nat`-specialized versions
   of common mathlib theorems, tagged with `@[pycsl_spec]`. Ship as part
   of the tool.
3. **Lean version pinning?** Lean 4 evolves quickly but the metaprogramming
   APIs are increasingly stable. Pin to a recent toolchain version and
   document upgrade paths.
4. **Should the tool also be invocable as a Lean command?**
   `#pycsl_emit "euclid.py"` from inside Lean would feel native. Worth
   exploring for v2.

---

## 11. Estimated effort

Assuming familiarity with Lean 4 metaprogramming and libcst:

- Phase 0: 1 day
- Phase 1 (Lean extraction): 3–4 days (faster than Rocq's SerAPI path)
- Phase 2 (translation): 1 week (similar to Rocq, plus type-class handling)
- Phase 3 (rewriter): 4–5 days (shared with `rocq2pycsl`)
- Phase 4 (verification round-trip): 2 days (shared)
- Phase 5 (UX): 2 days (smaller than Rocq's)
- Phase 6 (testing): +3 days dedicated

Total: ~3 weeks to a working v1.

If `pycsl_emit` (the Python rewriter + verification round-trip) is
already built from `rocq2pycsl`, subtract 1 week — share the common
backend. Net: ~2 weeks for the Lean-specific work.

---

## 12. References to consult during implementation

- **Lean 4 metaprogramming**: *Metaprogramming in Lean 4* (the
  community book), <https://leanprover-community.github.io/lean4-metaprogramming-book/>.
- **Lean 4 elaboration internals**: Ullrich, S., *An Extensible
  Theorem Proving Frontend* (PhD thesis, KIT, 2023).
- **Mathlib4**: <https://leanprover-community.github.io/mathlib4_docs/>.
- **PyCSL annotation language**: working reference document.
- **libcst**: <https://libcst.readthedocs.io>.
- **Why3**: Bobot, Filliâtre, Marché, Paskevich, *Let's verify this
  with Why3*, STTT 17(6), 2014.
- **Lean 4 attribute system reference**: Lean source,
  `Lean.Elab.Attribute`.
- **JSON for Lean expressions**: `Lean.Json` module documentation.
