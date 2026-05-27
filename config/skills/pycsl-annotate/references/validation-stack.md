# Three-Level Validation Stack

Every `#@` contract expression must clear three independent gates before it
is accepted end-to-end:

```
Level 1 — Concrete syntax      (Module2_Parser.py)
Level 2 — Static semantics     (Module4_SemanticAnalyzer.py)
Level 3 — WhyML generation     (Module6_WhyMLTranspiler.py + why3)
```

- Failing **Level 1** → parse error; `pycsl` exits before running `--no-proof`.
- Failing **Level 2** → Module4 error E1–E5 during `pycsl --no-proof`.
- Failing **Level 3** → Why3 type error *after* `pycsl --no-proof` succeeds.

Level 3 failures are the most dangerous: `pycsl --no-proof` reports success,
but Why3 rejects the generated `.mlw` file. The SR-6 / TR-3 trap is the
canonical example: `"key" in d` passes both Level 1 and Level 2, but fails
Level 3 when `d` is an unannotated parameter (→ `int` in WhyML).

---

## Level 1 — Syntax Failures (IS rules)

Consult `docs/pycsl-concrete-syntax-reference.md` for the full grammar.

| ID | Forbidden form | Replace with |
|----|----------------|--------------|
| IS-1 | `x is not None` | `x != 0` |
| IS-2 | `\length(\result)` | `\result >= 0` or `True` |
| IS-3 | `\forall i,` (comma separator) | `\forall i;` (semicolon) |
| IS-4 | `\exists x in s;` (collection range) | `\exists x; 0 <= x and x < n and ...` |
| IS-5 | `\result.field` (field access on result) | `True` |
| IS-6 | `\length(self.field)` (dot inside `\length`) | `True` |

---

## Level 2 — Static Semantics Failures (SR rules)

Consult `docs/pycsl-static-semantics-reference.md` for the judgement Γ ⊢ A : ok.

| ID | Rule | Consequence |
|----|------|-------------|
| SR-1 | All variables in `requires`/`ensures`/`loop invariant` must be in Γ_f = params ∪ annotated locals ∪ ghost vars | E2 unbound variable error |
| SR-2 | `\result` valid only in `ensures` | E1 if used in `requires` or `loop invariant` |
| SR-3 | Class invariant: `self.field` is `FieldAccess` → excluded from E5 scope check | `@dataclass` classes safe; weaving line-number mismatch is the only remaining blocker |
| SR-4 | `assigns self._*` targets: `FieldAccess` NOT validated against Γ_c | No false positives — all `#@ assigns self._*` clauses pass Module4 |
| SR-5 | Nested function closure vars not collected into Γ_f by `_build_function_scope` | Re-declare closure vars as `Any`-typed locals inside the nested function body |
| SR-6 | `"key" in d` with string literal passes Module4 (§3.2.6b) | Does NOT guarantee valid WhyML — see TR-3 below |

---

## Level 3 — Translational / WhyML Failures (TR rules)

Consult `docs/pycsl-translational-reference.md` for the full T : AnnotatedPython → WhyML mapping.

**These failures PASS Module4 but FAIL Why3.**

| ID | Rule | Effect on contracts |
|----|------|---------------------|
| TR-1 | Unannotated params → `int` in WhyML (§T.2.2); `str` → `int`; `list[T]` → `array int` | Use arithmetic predicates only on unannotated params (`>= 0`, `!= 0`, `> x`) |
| TR-2 | String literals → `hash(s) % 2^31`; `hash("") = 0` (§T.6.1) | `\result != ""` → `(result <> 0)` in WhyML — valid for `str`-returning functions |
| TR-3 | `in`/`not in` valid ONLY for `list[T]`-typed params (→ `array int`); unannotated param → `int`; `in` on `int` fails Why3 (G6, §T.11.1) | **Never** use `"key" in d` when `d` is unannotated; use `d != 0` or `True` |
| TR-4 | `assigns` in Hoare model (default) produces NO explicit `writes`/frame clause in WhyML (§T.9.1) | `#@ assigns self._*` is accepted, weaved, passes Module4 — but generates no proof obligation |
| TR-5 | `\result` → `result` identifier in WhyML `ensures` clause (§T.6.5) | Valid only in `ensures`; translates cleanly |
| TR-6 | `\trusted` → Why3 `val` declaration (§T.10) — no proof obligation | Use for external/stdlib functions; body not checked |
| TR-7 | `#@ proof <rocq\|lean> <q>` → Why3 `axiom pycsl_axiom_<target>` in module preamble (§T.2.10) — imports a Rocq or Lean theorem as a Why3 axiom that Alt-Ergo/Z3 may use. When both `rocq` and `lean` directives cite the same `pycsl_target`, the **"Rocq + Lean as Cross-Validated Spec Sources"** pattern applies: `proof2why3 cross-check` verifies the canonical forms agree before emission. | The supported escape hatch when SMT cannot discharge a fact unaided (Euclidean identities, divisibility, etc.). Strictly stronger than `\trusted`: two independent proof kernels must agree on the statement. Worked example: `0342.py` (GCD). |

---

## Practical Decision Checklist

Before writing any `#@` expression, answer these questions in order:

1. **Level 1** — Is this expression in the PyCSL grammar?
   - Check IS-1…IS-6 for the most common syntax traps.
   - Run `pycsl --no-proof file.py` and fix any `ParseError`.

2. **Level 2** — Are all variables in scope? Is `\result` only in `ensures`?
   - Check SR-1 (scope) and SR-2 (`\result` placement).
   - Module4 error codes E1–E5 tell you which rule fired.

3. **Level 3** — Will the generated WhyML pass Why3?
   - TR-3: does any `in`/`not in` operand lack a `list[T]` type annotation? → Replace with `True`.
   - TR-1: are arithmetic comparisons (`!= 0`, `>= 0`) used for unannotated params?
   - TR-2: for `str`-returning functions, is `\result != ""` the intended check? → Valid.
   - TR-4: for Hoare model (`assigns`), is the lack of a `writes` clause expected? → Yes.

---

## Quick Reference

| Pattern | Fails at | Canonical replacement |
|---------|----------|-----------------------|
| `x is not None` | L1 / IS-1 | `x != 0` |
| `\length(\result)` | L1 / IS-2 | `\result >= 0` or `True` |
| `\forall i,` | L1 / IS-3 | `\forall i;` |
| `\result` in `requires` | L2 / E1+SR-2 | Move clause to `ensures` |
| Unbound local `x` in contract | L2 / E2+SR-1 | Use parameter name; re-declare as annotated local |
| `"key" in d` (unannotated `d`) | L3 / TR-3 | `True` |
| `\result != ""` (str-returning) | — valid | Keep; → `(result <> 0)` in WhyML |
| `in` on unannotated param | L3 / TR-3 | `param != 0` or `True` |
| `assigns self._*` (Hoare model) | — valid (no WhyML output) | Keep; TR-4 expected behaviour |
| SMT times out on lemma needed by spec | — | `#@ proof rocq <q>` + `#@ proof lean <q>` (TR-7, "Rocq + Lean as Cross-Validated Spec Sources") — but only if the cited theorem actually exists in `*.proofs/{rocq,lean}/` and `proof2why3 cross-check` reconciles |
