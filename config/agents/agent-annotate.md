Act as an expert Python developer. Write a Python script named `agent-annotate.py` that annotates a Python program with PyCSL contracts and returns the annotated source code as plain Python text.

In `agent-annotate.py`, define a global variable named `AGENT_NAME` with the value `"agent-annotate"`.

## 1. Input

The script must accept these command-line options:

* `--in`: path to the Python program to annotate.
* `--out`: path to the output file that will contain the annotated program.

The script must read `agents-config.json` from the same directory as `agent-annotate.py`. The config must provide:

* `model`
* `project-directory`
* `skill-annotate`
* `memory-model` (optional, defaults to `"hoare"`)
* `rag-index` (optional, path to RAG skill index)
* `rag-top-k` (optional, defaults to `10`)

The `skill-annotate` path is resolved relative to the script directory unless it is already absolute.

## 2. Two-agent split architecture

For **multi-function files** (> 1 annotatable function), `agent-annotate.py` delegates to:

1. **`agent-splitter.py`** — deterministic call-graph analysis. Parses with `ast`, builds call graph, detects mutual recursion via Tarjan's SCC, topological-sorts from leaf to root, then invokes the writer per function.
2. **`agent-writer.py`** — single-function LLM annotator. Receives one function + callee contracts as context, produces annotated output.

For **single-function files**, the original monolithic LLM call is used directly.

Both paths produce `generated_code`, which then passes through all post-processing guards.

## 3. Skill prompt

The prompt must include the contents of `<skill-annotate>` (via RAG or full file) followed by the input Python program.

The model must be instructed to output only the annotated Python code in markdown code fences:

```
Just output the python code between "```python" and "```".
```

## 4. Output file

The script must create missing output directories automatically and write the generated annotated code to `<out>`.

## 5. Library to use

The script must import:

```python
from llm_client import llm_generate, log
```

It should use `log(...)` for errors and call `llm_generate(agent_id=model, prompt=prompt)` to generate the annotated code.

## 6. Memory model context

The script reads `"memory-model"` from `agents-config.json` (defaults to `"hoare"` if absent).
It logs the active model with `log(...)` before LLM invocation.

The memory model name is injected into the prompt as a clearly labeled section:

```
# ACTIVE MEMORY MODEL: HOARE
The pipeline is configured to use the `hoare` memory model. ...
```

This tells the LLM which predicates and syntax to use:

| Model   | Allowed predicates | Array parameter shape |
|---------|-------------------|----------------------|
| `hoare` | `\assigns \nothing` or `\assigns var` | `arr: list` → `array int` |
| `typed` | `\valid(arr, n)`, `\separated(a, na, b, nb)`, `\assigns arr[lo..hi]`, `\old(arr[i])`, `#@ label L`, `\at(arr[i], L)` | `arr: list` → `(arr: loc) (arr_len: int)` |
| `store` | Same as `typed` | Same as `typed` |

## 7. Post-processing guards for memory model annotations

After LLM generation, the script applies the following normalisation guards before writing output:

* **`\assigns arr[..n]` → `\assigns arr[0..n]`**: Fills in missing start index `0` for range assigns.
* **`\valid arr, n` → `\valid(arr, n)`**: Adds parentheses if LLM omits them.
* **`\separated a, na, b, nb` → `\separated(a, na, b, nb)`**: Adds parentheses if LLM omits them.
* **`#@ label L` blank-line collapse**: Removes any blank lines between a `#@ label` annotation and the labeled Python statement so Module1 can associate them by line number.
* Plus ~40 additional guards for recursion detection, reserved keyword renaming, loop invariant strengthening/weakening, etc.

