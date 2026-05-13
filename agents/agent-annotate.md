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

The `skill-annotate` path is resolved relative to the script directory unless it is already absolute.

## 2. Skill prompt

The prompt must include the contents of `<skill-annotate>` followed by the input Python program.

The skill file ends with:

```python
...

# TASK

Analyze the following Python code and output the fully annotated PyCSL version. Output ONLY the valid Python code.
```

The model must be instructed to output only the annotated Python code in markdown code fences:

```
Just output the python code between "```python" and "```".
```

## 3. Output file

The script must create missing output directories automatically and write the generated annotated code to `<out>`.

## 4. Library to use

The script must import:

```python
from llm_client import llm_generate, log
```

It should use `log(...)` for errors and call `llm_generate(agent_id=model, prompt=prompt)` to generate the annotated code.

## 5. Memory model context

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

## 6. Post-processing guards for memory model annotations

After LLM generation, the script applies the following normalisation guards before writing output:

* **`\assigns arr[..n]` → `\assigns arr[0..n]`**: Fills in missing start index `0` for range assigns.
* **`\valid arr, n` → `\valid(arr, n)`**: Adds parentheses if LLM omits them.
* **`\separated a, na, b, nb` → `\separated(a, na, b, nb)`**: Adds parentheses if LLM omits them.
* **`#@ label L` blank-line collapse**: Removes any blank lines between a `#@ label` annotation and the labeled Python statement so Module1 can associate them by line number.

