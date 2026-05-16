# agent-splitter

Deterministic call-graph analysis and bottom-up annotation orchestrator. This agent uses **no LLM calls** — it is purely algorithmic.

In `agent-splitter.py`, define a global variable named `AGENT_NAME` with the value `"agent-splitter"`.

## 1. Input

The script accepts these command-line options:

* `--in`: path to the Python program to annotate.
* `--out`: path to the output annotated file.

The script reads `agents-config.json` from `<project-root>/config/`.

## 2. Algorithm

### Step 1: Parse and extract functions

Use Python's `ast` module to extract all top-level functions and class methods. Skip dunder methods (`__init__`, `__str__`, etc.) and `@property` methods — Module5 ignores them.

### Step 2: Build call graph

For each function, walk its AST to find `ast.Call` nodes:

* **Direct calls**: `func(...)` → resolve to a same-file function.
* **Self calls**: `self.method(...)` → resolve within the same class scope.
* External calls (builtins, imports) are ignored.

### Step 3: Detect SCCs (mutual recursion)

Apply Tarjan's strongly-connected-components algorithm:

* SCC with 1 function → no mutual recursion (the common case).
* SCC with 2–3 functions → mutual recursion group, annotated together in one writer call.
* SCC with > 3 functions → too complex; use safe fallback contracts (`#@ requires 1 == 1`, `#@ ensures 1 == 1`).

### Step 4: Topological sort

Tarjan's SCC returns components in reverse topological order — leaf functions (no callees) come first. This is the annotation order.

### Step 5: Invoke writer per function

For each function/SCC in order:

1. Extract the function source text.
2. Collect `#@` contract lines from already-annotated callees as context.
3. Call `agent-writer.py` via subprocess, passing input as JSON on stdin.
4. Store the annotated function and its contracts.

### Step 6: Reassemble

Replace original function text with annotated versions. Non-function code (imports, globals, `if __name__`) is preserved verbatim.

## 3. Fallback

If the writer fails for any function, a safe fallback annotation is generated:

```
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
```

For methods, `assigns` detects `self.*` field mutations.

## 4. Integration

`agent-annotate.py` imports `run_splitter()` directly for multi-function files (> 1 annotatable function). Single-function files use the original monolithic LLM path. All post-processing guards in `agent-annotate.py` run on the reassembled output regardless of which path produced it.
