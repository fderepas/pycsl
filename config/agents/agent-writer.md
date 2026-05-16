# agent-writer

Single-function LLM annotator. Receives one function (or small mutual-recursion group) and produces PyCSL contract annotations.

In `agent-writer.py`, define a global variable named `AGENT_NAME` with the value `"agent-writer"`.

## 1. Input

The script accepts these command-line options:

* `--memory-model`: one of `hoare`, `typed`, `store` (default: `hoare`).
* `--config`: path to `agents-config.json`.

Input data is read from **stdin** as a JSON object:

```json
{
  "function_source": "def foo(n: int) -> int:\n    ...",
  "callee_contracts": "# Contracts for bar:\n#@ requires n >= 0\n#@ ensures \\result >= 0",
  "class_context": "class MyClass:\n    def __init__(self):\n        self._value = 0"
}
```

* `function_source` (required): the raw Python function to annotate.
* `callee_contracts` (optional): `#@` contract lines of already-annotated callees. The writer uses these to write tighter invariants — e.g., if `bar` guarantees `\result >= 0`, the caller's loop invariant can assert `acc >= 0` after calling `bar`.
* `class_context` (optional): class definition header and `__init__` body, provided when the function is a class method.

## 2. Output

The annotated function is written to **stdout** as plain Python text (no JSON wrapping, no markdown fences).

## 3. Skill loading

The writer loads the pycsl-annotate skill via:

1. **RAG retrieval** (if `rag-index` is configured and the index file exists): retrieves the most relevant skill chunks for the function being annotated.
2. **Full skill file** (fallback): loads the entire `skill-annotate` file.

## 4. Prompt structure

```
<skill content or RAG chunks>

# ACTIVE MEMORY MODEL: HOARE
...

# TASK
You are annotating a SINGLE function (not a whole file).
Output ONLY the annotated function with `#@` contract comments.
...

# CALLEE CONTRACTS (already verified)
...

# CLASS CONTEXT
...

# FUNCTION TO ANNOTATE
def foo(n: int) -> int:
    ...
```

## 5. Post-processing

The writer applies **minimal** post-processing (just markdown fence extraction). The heavy post-processing guards (recursion detection, reserved-keyword renaming, loop invariant strengthening, etc.) are applied by `agent-annotate.py` on the reassembled output.

## 6. Error handling

On LLM failure, the writer exits with a non-zero status code and error on stderr. The splitter catches this and applies a safe fallback annotation for that function.
