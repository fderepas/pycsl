---
name: refactor-python-god-methods
description: Worked examples of splitting large Python functions into focused helpers. Covers the parse-args + run-pipeline + run-proofs pattern, multi-branch dispatch extraction, and nested-if chain cleanup. Use when Section 2 of the main skill applies.
---

# God Method Split Patterns

Each pattern below shows a before/after for a common god-method shape. Adapt to your codebase.

---

## Pattern 1: CLI `main()` split

`main()` functions commonly accumulate arg parsing, orchestration, output, and cleanup.

### Before (all mixed together, 200+ lines):
```python
def main():
    parser = argparse.ArgumentParser(...)
    parser.add_argument("file", ...)
    parser.add_argument("--prover", ...)
    # ... 20 more add_argument calls ...
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"[!] File not found: {args.file}")
        sys.exit(1)

    with open(args.file) as f:
        source = f.read()

    # 50 lines of pipeline execution
    ingestor = Module1(source)
    ...
    transpiler = Module6(ir)
    mlw = transpiler.transpile()

    # 80 lines of proof invocation
    why3_result = subprocess.run(["why3", "prove", ...])
    ...
```

### After (three focused helpers):
```python
def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(...)
    parser.add_argument("file", ...)
    parser.add_argument("--prover", ...)
    return parser.parse_args()


def _run_pipeline(source_code: str, memory_model: str, args: argparse.Namespace) -> str:
    """Run Modules 1–6. Returns WhyML code string."""
    ingestor = Module1(source_code)
    ...
    return transpiler.transpile()


def _run_proofs(mlw_code: str, mlw_filename: str, provers: List[str],
                args: argparse.Namespace) -> None:
    """Invoke Why3 and handle results."""
    why3_result = subprocess.run(["why3", "prove", ...])
    ...


def main() -> None:
    args = _parse_args()
    if not os.path.exists(args.file):
        print(f"[!] File not found: {args.file}")
        sys.exit(1)
    with open(args.file) as f:
        source = f.read()
    memory_model = args.memory_model or "hoare"
    provers = [args.prover] if args.prover else DEFAULT_PROVERS
    try:
        mlw = _run_pipeline(source, memory_model, args)
    except ProjectError as e:
        print(f"[!] {e}")
        sys.exit(1)
    _run_proofs(mlw, f"{base}.mlw", provers, args)
```

**Key:** `main()` is now a 20-line orchestrator. Each helper is independently testable.

---

## Pattern 2: Multi-branch `if/elif` dispatch

A function with three top-level branches (e.g., handling three import styles) should be split into three helpers.

### Before (one 130-line function with nested branches):
```python
def _resolve_imports(ast, main_file, ir_data, deep=False):
    imports = _extract_imports(ast)
    for local, original, module, level, is_module in imports:
        if is_module:
            # 40 lines handling "import mod" / "import mod as alias"
            ...
        elif local == "*":
            # 35 lines handling "from mod import *"
            ...
        else:
            # 45 lines handling "from mod import name"
            ...
```

### After (thin orchestrator + three focused handlers):
```python
def _resolve_imports(ast: _ast.AST, main_file: str, ir_data: Dict[str, Any],
                     deep: bool = False, cache: Optional[Dict] = None,
                     processing_set: Optional[Set[str]] = None) -> Set[str]:
    imports = _extract_imports(ast)
    direct = [(l, o, m, v) for l, o, m, v, is_mod in imports if not is_mod and l != "*"]
    wildcards = [(m, v) for l, o, m, v, is_mod in imports if l == "*"]
    module_imports = [(l, o, m, v) for l, o, m, v, is_mod in imports if is_mod]
    cache = cache or {}
    processing_set = processing_set or set()
    names: Set[str] = set()
    names |= _resolve_direct_imports(direct, ..., cache, processing_set)
    names |= _resolve_wildcard_imports(wildcards, ..., cache, processing_set)
    names |= _resolve_module_imports(module_imports, ..., cache, processing_set)
    return names


def _resolve_direct_imports(direct_imports: List[Any], all_calls: Set[str],
                              main_file: str, ir_data: Dict[str, Any],
                              deep: bool, cache: Dict, processing_set: Set[str]) -> Set[str]:
    """Handle `from mod import name` imports."""
    ...


def _resolve_wildcard_imports(...) -> Set[str]:
    """Handle `from mod import *` imports."""
    ...


def _resolve_module_imports(...) -> Set[str]:
    """Handle `import mod` / `import mod as alias` imports."""
    ...
```

---

## Pattern 3: Large expression/statement visitor

A 600-line `_expr_to_whyml()` method with 40+ `if isinstance(node, ...)` branches should be split by node category.

### Strategy:
```python
# Before: one giant method
def _expr_to_whyml(self, node: dict) -> str:
    if node["type"] == "BinOp":
        # 90 lines
    elif node["type"] == "Call":
        # 180 lines
    elif node["type"] == "ArrayAccess":
        # 55 lines
    elif ...  # 37 more branches

# After: dispatch to handlers
def _expr_to_whyml(self, node: dict) -> str:
    t = node["type"]
    if t == "BinOp":
        return self._handle_binop(node)
    if t == "Call":
        return self._handle_call_expr(node)
    if t == "ArrayAccess":
        return self._handle_array_access(node)
    ...

def _handle_binop(self, node: dict) -> str:
    """Emit WhyML for binary operations (+, -, *, /, comparison, boolean)."""
    ...

def _handle_call_expr(self, node: dict) -> str:
    """Emit WhyML for function calls, method calls, and built-ins."""
    ...

def _handle_array_access(self, node: dict) -> str:
    """Emit WhyML for array indexing, with bounds-check model awareness."""
    ...
```

**Extraction heuristic:** group branches by the first word of the comment above them. If comments say "handle binops", "handle calls", "handle subscripts", those are your natural groups.

---

## Pattern 4: Pipeline of string transforms

A function that applies 30+ sequential string transformations (guards) is hard to debug because there's no visibility into which transform changed what.

### Before (implicit sequential mutation):
```python
def main():
    code = llm_response
    code = _fix_missing_contracts(code)
    code = _fix_ensures_1_eq_1(code)
    code = _fix_loop_invariants(code)
    # ... 25 more lines
```

### After (explicit `GuardPipeline` class):
```python
class GuardPipeline:
    """Composable str→str transform pipeline."""

    def __init__(self, code: str) -> None:
        self.code = code
        self._log: List[str] = []

    def apply(self, name: str, transform: Callable[[str], str]) -> GuardPipeline:
        try:
            self.code = transform(self.code)
            self._log.append(f"[OK] {name}")
        except Exception as e:
            self._log.append(f"[ERR] {name}: {e}")
        return self   # enables chaining


def main():
    pipeline = GuardPipeline(llm_response)
    (pipeline
        .apply("fix-missing-contracts", _fix_missing_contracts)
        .apply("fix-ensures-placeholder", _fix_ensures_1_eq_1)
        .apply("fix-loop-invariants", _fix_loop_invariants))
    code = pipeline.code
```

**Benefits:** each transform is independently testable with `transform(input)`, errors don't kill the whole pipeline, and the log shows exactly which guards ran.

---

## Rules summary

| Rule | Rationale |
|------|-----------|
| Orchestrator calls helpers; helpers don't call each other | Prevents hidden ordering dependencies |
| Each helper does one thing; name needs no "and" | Forces real separation of concerns |
| Helper signature makes data flow explicit | No hidden state shared via `self` or globals |
| Orchestrator stays ≤ 25 lines | Forces you to extract everything non-trivial |
| Group by phase, not by implementation detail | Phases survive refactoring; details don't |
