# Refactoring Plan: `src/pycsl/Module5_IREmitter.py`

## Context

`Module5_IREmitter.py` (885 lines) is already well-structured: three class-level dispatch
tables (`_CSL_HANDLERS`, `_PY_EXPR_HANDLERS`, `_PY_STMT_HANDLERS`) are in place, no
method exceeds 35 lines, and all public methods carry full type annotations.

Two targeted cleanups remain:

1. `_py_op_to_str` (line 259) rebuilds a 12-entry `ops` dict on every call — it should be
   a class-level constant like the three existing dispatch tables.
2. Five local variables use bare `set` instead of the project-wide `Set[str]` convention.

**Baseline:** 270/274 tests passing (pre-existing failures: 0018, 0019, 0254, 0255).

---

## Diagnostic Summary

| Metric | Value |
|--------|-------|
| Total lines | 885 |
| God methods (>100 lines) | 0 |
| Bare `set` annotations | 5 |
| Inline dict rebuilt per call | 1 (`_py_op_to_str`) |

### `_py_op_to_str` (lines 259–271)

```python
def _py_op_to_str(self, op: ast.operator | ast.cmpop | ast.unaryop) -> str:
    ops = {                           # rebuilt on every call
        ast.Add: "+", ast.Sub: "-", ...   # 12 entries
    }
    return ops.get(type(op), "?")
```

Fix: move to a class-level `_PY_OP_MAP: Dict[type, str]` constant after `_PY_STMT_HANDLERS`.
Method body becomes a one-liner.

### Bare `set` annotations (5 sites)

| Line | Context | Fix |
|------|---------|-----|
| 725 | `param_names: set` (parameter) | `Set[str]` |
| 727 | `result: set = set()` (local) | `Set[str]` |
| 742 | `field_names_seen: set = set()` (local) | `Set[str]` |
| 841 | `array2d: set = set()` (local) | `Set[str]` |
| 851 | `array1d: set = set()` (local) | `Set[str]` |

`Set` is already imported at line 5 — no import change needed.

---

## Phase 0 — Baseline

```bash
source .venv/bin/activate && python3 -c "
import subprocess, os, glob
tests = sorted(glob.glob('test-suite/corpus/pycsl-reference/*.py'))
fails = [os.path.basename(t) for t in tests
         if subprocess.run(['python3', 'src/pycsl/pycsl.py', '--no-proof', t],
                           capture_output=True).returncode != 0]
print('FAILs:', fails); print(f'{len(tests)-len(fails)}/{len(tests)} passed')
"
python3 -m py_compile src/pycsl/Module5_IREmitter.py
```

Expected: `FAILs: ['0018.py', '0019.py', '0254.py', '0255.py']`, 270/274 passed.

---

## Phase 1 — Extract `_py_op_to_str` dict → `_PY_OP_MAP` (15 min)

**Location:** lines 259–271.

**Step 1** — Add class-level constant after `_PY_STMT_HANDLERS` (line ~466):

```python
# Dispatch table: Python AST operator type → operator string
_PY_OP_MAP: Dict[type, str] = {
    ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "div",
    ast.Mod: "%",
    ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
    ast.USub: "-", ast.UAdd: "+", ast.Not: "not",
    ast.In: "in", ast.NotIn: "not in",
    ast.Is: "==", ast.IsNot: "!=",
    ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^",
    ast.LShift: "<<", ast.RShift: ">>", ast.Pow: "**",
}
```

**Step 2** — Replace `_py_op_to_str` body:

```python
def _py_op_to_str(self, op: ast.operator | ast.cmpop | ast.unaryop) -> str:
    return self._PY_OP_MAP.get(type(op), "?")
```

**Verify:**
```bash
python3 -m py_compile src/pycsl/Module5_IREmitter.py
grep -c "ops = {" src/pycsl/Module5_IREmitter.py   # must be 0
```

---

## Phase 2 — Fix bare `set` annotations (15 min)

**Location:** lines 725, 727, 742, 841, 851.

Replace all 5 occurrences of `: set` with `: Set[str]` (using targeted Edit calls for
each site — `replace_all=True` is risky here since bare `: set` could appear in
unrelated contexts).

Sites:
- `_collect_2d_params` param (L725): `param_names: set` → `param_names: Set[str]`
- `_collect_2d_params` local (L727): `result: set = set()` → `result: Set[str] = set()`
- `_collect_class_fields` local (L742): `field_names_seen: set = set()` → `field_names_seen: Set[str] = set()`
- `_build_function_ir` local (L841): `array2d: set = set()` → `array2d: Set[str] = set()`
- `_build_function_ir` local (L851): `array1d: set = set()` → `array1d: Set[str] = set()`

**Verify:**
```bash
python3 -m py_compile src/pycsl/Module5_IREmitter.py
grep -n ": set$\|: set " src/pycsl/Module5_IREmitter.py   # must be 0
```

---

## Execution Order Summary

| Step | Change | Effort | Risk |
|------|--------|--------|------|
| 0 | Establish baseline | 5 min | None |
| 1 | `_PY_OP_MAP` class-level constant | 15 min | None |
| 2 | Fix 5 bare `set` annotations | 15 min | None |

**Do not mix steps.** Each step must pass `py_compile` and the 270/274 baseline
before the next starts.

---

## Critical File

`src/pycsl/Module5_IREmitter.py` — only file modified.

---

## Invariants to Preserve

- `_py_op_to_str` must return `"?"` for unknown operators (same as before).
- `_PY_OP_MAP` is a class-level constant — no `self` reference at definition time.
- Observable output of `PyCSLToJSONEmitter.visit()` must be byte-for-byte identical.

---

## Verification

```bash
# After each phase:
python3 -m py_compile src/pycsl/Module5_IREmitter.py

# After phase 2 (final):
source .venv/bin/activate && python3 -c "
import subprocess, os, glob
tests = sorted(glob.glob('test-suite/corpus/pycsl-reference/*.py'))
fails = [os.path.basename(t) for t in tests
         if subprocess.run(['python3', 'src/pycsl/pycsl.py', '--no-proof', t],
                           capture_output=True).returncode != 0]
print('FAILs:', fails); print(f'{len(tests)-len(fails)}/{len(tests)} passed')
"
```

Expected: `FAILs: ['0018.py', '0019.py', '0254.py', '0255.py']`, 270/274 passed.
