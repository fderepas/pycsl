# Self-Annotation Global Plan — Appendix: Three-Level Validation Walk-Through

*Companion to `self-annotate-global-plan.md` §9.4.*
*References: `docs/pycsl-concrete-syntax-reference.md` (Layer 1),
`docs/pycsl-static-semantics-reference.md` (Layer 2),
`docs/pycsl-translational-reference.md` (Layer 3).*

---

## §A.1 The Three-Level Validation Loop

Writing a `#@` contract for a PyCSL function involves three independent
validation gates:

```
Write contract
      │
      ▼
 pycsl --no-proof file.py
      │
      ├── ParseError / UnexpectedToken  ──→  Level 1 failure (IS rules)
      ├── PyCSLSemanticError E1–E13     ──→  Level 2 failure (SR rules)
      └── "Success: WhyML written"
                │
                ▼
         why3 prove file.mlw
                │
                ├── "type int does not match type bool"  ──→  Level 3 failure (TR rules)
                ├── "unbound function symbol 'X'"        ──→  Level 3 failure (TR-1/TR-3)
                └── "Valid" / "Unknown" (proof result)
```

**Key property:** `pycsl --no-proof` succeeding does NOT guarantee Level 3
passes. Contracts that clear Levels 1 and 2 can still generate invalid WhyML
that Why3 rejects. The SR-6 / TR-3 trap is the canonical example:
`"key" in d` where `d` is unannotated passes both pycsl gates but fails
Why3 (`in` requires `array int`, but `d` maps to `int`).

The validation loop is: write → `pycsl --no-proof` → `why3 prove`. Each
tool exercises a different layer. Run them in order and fix one level at a
time before proceeding to the next.

---

## §A.2 Level 1 Errors — Parse Failures

Parser errors appear during the pycsl ingestion phase, before `--no-proof`
validation runs. The error message typically names the unexpected token and
its position.

| Pattern | Typical error output | IS rule | Fix |
|---------|---------------------|---------|-----|
| `x is not None` | `UnexpectedToken 'is'` | IS-1 | `x != 0` |
| `\length(\result)` | `UnexpectedToken '\\result'` inside `\length(` | IS-2 | `\result >= 0` or `1 == 1` |
| `\forall i,` | `UnexpectedToken ','` after bound variable | IS-3 | `\forall i;` |
| `\exists x in s;` | `UnexpectedToken 'in'` | IS-4 | `\exists x; 0 <= x and x < n and ...` |
| `\result.field` | `UnexpectedToken '.'` after `\result` | IS-5 | `1 == 1` |
| `\length(self.attr)` | `UnexpectedToken '.'` inside `\length(` | IS-6 | `1 == 1` |
| `True` / `False` / `None` | `UnexpectedToken 'True'` | general | `1 == 1` / `0 == 1` / `0` |
| `%` or `//` inside `#@` | `UnexpectedToken '%'` | general | weaken or `1 == 1` |

**Debugging tip:** The error message includes the line and column. Open the
annotated file, find the `#@` line, and locate the unexpected token at the
reported column. The IS table above maps tokens to the fix directly.

---

## §A.3 Level 2 Errors — Module4 Semantic Errors

These appear as `PyCSLSemanticError` during `pycsl --no-proof`. The error
catalogue is defined in `docs/pycsl-static-semantics-reference.md` §9.

| Code | Message pattern | SR rule | Concrete fix |
|------|-----------------|---------|--------------|
| E1 | `"Invalid use of '\\result' in <context>. It is only allowed in 'ensures'."` | SR-2 | Move `\result` from `requires` / `loop invariant` to `ensures` only |
| E2 | `"Undefined variable '<var>' referenced in contract for <context>."` | SR-1 | Use a parameter name; for nested functions, re-declare closure vars as `Any`-typed locals at the top of the nested function body (SR-5) |
| E3 | `"Assigns region references undefined variable '<arr>' in <context>."` | SR-1 | Use only `self._field` names or parameter names in `assigns` |
| E4 | `"Assigns region on non-list variable '<arr>' (type '<type>') in <context>."` | SR-4 (gap) | `assigns \nothing` or `assigns self._field` (FieldAccess not validated) |
| E5 | `"Undefined variable '<var>' in class invariant for '<class>'."` | SR-3 | Use `self.field` form (FieldAccess excluded from E5 check — this error fires only for bare non-field names) |
| E6 | `"\\valid base '<arr>' is not a list parameter in <context>."` | SR-1 | Ensure the `\valid` base is a `list`-typed parameter |
| E8 | `"Function '<f>': unprotected <action> shared variable '<var>'."` | — | Add `#@ critical <mutex>` before the `with` block |

**Important:** Errors E3 and E4 relate to `assigns` region validation. For
`self._field` assigns targets, FieldAccess is excluded from variable
extraction (SR-4 gap, §10.1 of static semantics reference) — these targets
pass Module4 regardless. E3 fires for non-field, non-parameter names.

**Debugging tip:** The error message includes the function/class name and
usually the clause type (requires, ensures, loop invariant). Navigate to
that function, find the clause, and apply the SR fix from the table.

---

## §A.4 Level 3 Errors — Why3 Type Failures

These appear after `pycsl --no-proof` succeeds, when running `why3 prove`.
They are the hardest failures to diagnose because pycsl reports success.

| Why3 error pattern | TR rule | Cause | Fix |
|--------------------|---------|-------|-----|
| `"type int does not match type bool"` / `"in on int"` | TR-3 | `in`/`not in` on an `int`-typed expression (unannotated param → `int`) | Replace `"key" in d` with `1 == 1` or an arithmetic predicate |
| `"unbound function symbol 'header'"` or similar field | TR-1 | External library type param (e.g., libcst node) mapped to `int`; field access invalid | Use `1 == 1` for all contracts on methods with external-type params |
| `"type array int does not match type int"` | TR-1 | Parameter typed `list[T]` (→ `array int`) used where `int` expected | Check type annotation; use `\length(param)` for length, `param[i]` for elements |
| `"This expression has type (), but is expected to have type int"` | general | `return` inside `if` in `while` loop body | Apply flag + sentinel pattern (see `pycsl-annotate` SKILL.md Example 6) |
| `"unbound variable 'result'"` in body | TR-5 | Local variable named `result` — renamed to `acc` by pipeline | Update loop invariants to use `acc`, not `result` |
| No writes clause in output (not an error) | TR-4 | Hoare model: `assigns` generates no explicit `writes` | Expected behaviour; no fix needed |
| `"syntax error"` in `.mlw` file near reserved word | general | Parameter named `val` or `match` | Rename: `val` → `value`, `match` → `is_match` |

**Key diagnostic for TR-3:** Look at the parameter list of the failing
function. For every parameter that is NOT annotated with `list[T]`, it maps
to `int` in WhyML (TR-1). If any contract expression applies `in`/`not in`
to such a parameter, replace with `1 == 1`.

**Debugging tip:** Run `why3 prove -P alt-ergo file.mlw` and read the error
line number. Open the generated `.mlw` file (use `pycsl --keep-mlw`), find
the reported line, identify the expression that Why3 rejects, and trace back
to the `#@` contract that generated it.

---

## §A.5 Walk-Through: `_handle_while_stmt`

**Source** (`Module6_WhyMLTranspiler.py:1446`):
```python
def _handle_while_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                        local_refs: Set[str], declared_refs: Set[str],
                        indent: str, in_loop: bool) -> str:
```

### Candidate contracts

```python
#@ requires stmt != 0
#@ requires "test" in stmt
#@ assigns self._known_collection_sizes, self._known_collection_elements
#@ assigns self._array_locals, self._dict_locals, self._lambda_locals
#@ assigns self._record_locals, self._has_early_ret
#@ assigns self._abstract_ops, self._havoc_counter, self._in_spec
#@ ensures \result != ""
def _handle_while_stmt(self, stmt, rest, local_refs, declared_refs, indent, in_loop):
```

### Level 1 check

- `stmt != 0`: valid — comparison expression with integer literal.
- `"test" in stmt`: syntactically valid — string literal `in` expression (§3.2.6b of syntax reference).
- `\result != ""`: valid — `\result` in `ensures`, string literal right-hand side.
- All `assigns` targets: valid `self._field` form.

Level 1 **passes**.

### Level 2 check

Γ_f for `_handle_while_stmt`:
```
Γ_f = {self, stmt, rest, local_refs, declared_refs, indent, in_loop}
```

- `stmt != 0`: `stmt` ∈ Γ_f ✓
- `"test" in stmt`: `stmt` ∈ Γ_f ✓; string literal always well-formed ✓ (SR-6)
- `\result` in `ensures`: valid (SR-2) ✓
- `assigns self._*`: FieldAccess excluded from validation (SR-4) ✓

Level 2 **passes**.

### Level 3 check

Type mapping (TR-1): `stmt: Dict[str, Any]` — not annotated with `list[T]`.
In WhyML, unannotated parameters default to `int`.

- `stmt != 0` → `!stmt <> 0` in WhyML — valid (`int` comparison).
- `"test" in stmt` → WhyML attempts `in` on `int` → **fails Why3** (TR-3, G6).
- `\result != ""` → `result <> 0` in WhyML — valid for `str`-returning function (TR-2).
- `assigns self._*` in Hoare model → generates no `writes` clause (TR-4, expected).

**Fix:** Remove `"test" in stmt`; `stmt != 0` alone is sufficient:

`"test" in stmt` has no expressible WhyML equivalent while `stmt` is unannotated
(`Dict[str, Any]` → `int`). `stmt != 0` is the weakest valid proxy for "stmt is
a non-empty IR node."

Level 3 **passes after fix**.

### Final validated contract

```python
#@ requires stmt != 0
#@ assigns self._known_collection_sizes, self._known_collection_elements
#@ assigns self._array_locals, self._dict_locals, self._lambda_locals
#@ assigns self._record_locals, self._has_early_ret
#@ assigns self._abstract_ops, self._havoc_counter, self._in_spec
#@ ensures \result != ""
def _handle_while_stmt(self, stmt, rest, local_refs, declared_refs, indent, in_loop):
```

> **Summary:** L1 ✓ · L2 ✓ (SR-1: `stmt` ∈ Γ_f; SR-4: `self._*` assigns pass) · L3 ✓ (TR-1: `stmt != 0`; TR-4: no frame clause; TR-2: `result <> 0`)

---

## §A.6 Walk-Through: `_stmts_to_whyml`

**Source** (`Module6_WhyMLTranspiler.py:2098`):
```python
def _stmts_to_whyml(self, stmts: List[Dict[str, Any]], local_refs: Set[str],
                     declared_refs: Set[str], indent: str, in_loop: bool = False) -> str:
```

### Candidate contracts (from global plan §6.3)

```python
#@ requires stmts != 0
#@ assigns self._array_locals, self._dict_locals, self._lambda_locals
#@ assigns self._abstract_ops, self._in_spec
#@ ensures \result != ""
def _stmts_to_whyml(self, stmts, local_refs, declared_refs, indent, in_loop=False):
```

### Level 1 check

All expressions are syntactically valid. Level 1 **passes**.

### Level 2 check

Γ_f = {self, stmts, local_refs, declared_refs, indent, in_loop}.
- `stmts != 0`: `stmts` ∈ Γ_f ✓
- `assigns self._*`: FieldAccess excluded (SR-4) ✓
- `\result` in `ensures` ✓ (SR-2)

Level 2 **passes**.

### Level 3 check

- `stmts: List[Dict[str, Any]]` → annotated with `list`, maps to `array int` (TR-1).
  `stmts != 0` would mean comparing `array int` to `0` — **type mismatch**.
  Fix: use `\length(stmts) >= 0` or `1 == 1`.
- `assigns self._*` in Hoare model → no `writes` clause emitted (TR-4). This is
  **expected and intentional**: the assigns clause documents what fields are
  modified (design intent) even though the Hoare model does not verify the frame.
- `\result != ""` → `result <> 0` in WhyML — valid (TR-2).

**Fix:** Replace `stmts != 0` with `\length(stmts) >= 0` or `1 == 1`:

```python
#@ requires \length(stmts) >= 0
```

(Note: `\length(stmts) >= 0` is always-true but explicitly valid; use `1 == 1`
if the precondition is purely aspirational.)

**TR-4 note:** The multiple `assigns self._*` lines are correct and should be
kept. They document which fields may change — a design commitment — even though
the Hoare model emits no corresponding `writes` clause. Why3 will not fail on
the absence of a `writes` clause; it simply applies no frame restriction.

Level 3 **passes after fix**.

### Final validated contract

```python
#@ requires \length(stmts) >= 0
#@ assigns self._known_collection_sizes, self._known_collection_elements
#@ assigns self._array_locals, self._dict_locals, self._lambda_locals
#@ assigns self._record_locals, self._has_early_ret
#@ assigns self._abstract_ops, self._havoc_counter
#@ ensures \result != ""
def _stmts_to_whyml(self, stmts, local_refs, declared_refs, indent, in_loop=False):
```

> **Summary:** L1 ✓ · L2 ✓ (SR-4: all `self._*` assigns pass) · L3 ✓ (TR-1: `\length(stmts)` valid for `list`-typed param; TR-4: no frame clause; TR-2: `result <> 0`)

---

## §A.7 Quick Reference Card

For each common contract pattern: which level may reject it, and the canonical
replacement. Patterns marked "— valid" pass all three levels.

| Pattern | Fails at | Replacement |
|---------|----------|-------------|
| `x is not None` | L1 / IS-1 | `x != 0` |
| `\length(\result)` | L1 / IS-2 | `\result >= 0` or `1 == 1` |
| `\forall i,` (comma) | L1 / IS-3 | `\forall i;` (semicolon) |
| `\exists x in s;` | L1 / IS-4 | `\exists x; 0 <= x and x < n and cond` |
| `\result.field` | L1 / IS-5 | `1 == 1` |
| `\length(self.attr)` | L1 / IS-6 | `1 == 1` |
| `True` / `False` / `None` | L1 | `1 == 1` / `0 == 1` / `0` |
| `\result` in `requires` | L2 / E1+SR-2 | Move to `ensures` |
| Bare non-param name | L2 / E2+SR-1 | Use a parameter name; re-declare closure var |
| `"key" in d` (unannotated `d`) | L3 / TR-3 | `d != 0` or `1 == 1` |
| `"key" in d` (`d: list[T]`) | — valid | Keep (→ `in (array int)`) |
| `\result != ""` (str-returning) | — valid | Keep (→ `result <> 0`) |
| `list_param != 0` | L3 / TR-1 | `\length(list_param) >= 0` or `1 == 1` |
| `in` on unannotated param | L3 / TR-3 | `param != 0` or `1 == 1` |
| `assigns self._*` (Hoare) | — valid (no WhyML frame) | Keep; TR-4 is expected behaviour |
| Local var named `result` in body | L3 (renamed) | Use `acc` in all loop invariants |
| Param named `val` | L3 (reserved word) | Rename to `value` |
| Param named `match` | L3 (reserved word) | Rename to `is_match` |
| Aspirational `1 == 1` | — valid | Keep; note intent in inline comment (`# aspirational: ...`) |

---

## §A.8 Integration with the Six-Step Annotation Process (§9.4)

The six-step process in §9.4 of the global plan focuses on *what* to write.
Apply the three-level check at step 6 ("Run `pycsl --no-proof` and fix any
parse errors") as follows:

```
Step 6 expanded:

6a. Run: pycsl --no-proof src/self-annotate/rocq/<file>.py
    ├─ Fix any Level 1 ParseErrors (IS-1…IS-6 table above, §A.2)
    └─ Fix any Level 2 E1–E13 errors (SR-1…SR-6 table above, §A.3)

6b. Run: pycsl --keep-mlw --no-proof src/self-annotate/rocq/<file>.py
    Then: why3 prove <file>.mlw -P alt-ergo
    └─ Fix any Level 3 Why3 type errors (TR-1…TR-6 table above, §A.4)

6c. Repeat 6a–6b until both tools report no errors.
```

**Why3 is the final arbiter.** Do not mark a function's contract as "done"
until step 6b passes clean. Level 1 + Level 2 success is necessary but not
sufficient.

**Authoritative IS/SR/TR checklist:** `config/skills/pycsl-annotate/references/validation-stack.md`
contains the complete rule tables and the four-question decision checklist to apply
before writing any `#@` expression. Load the `pycsl-annotate` skill at the start
of each annotation session to have these rules in context.
