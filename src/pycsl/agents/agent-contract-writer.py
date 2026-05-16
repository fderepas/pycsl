"""
agent-contract-writer.py — Step 2 of the 3-agent annotation pipeline.

Receives a Python function + plain-English description (from agent-english-writer)
and writes PyCSL function-level contracts:
  - #@ requires <expr>
  - #@ ensures <expr>
  - #@ assigns <targets>

Does NOT write loop invariants or loop variants — that is step 3.
"""

import re

from llm_client import llm_generate, log

AGENT_NAME = "agent-contract-writer"

_SYSTEM_PROMPT = """\
You are a formal verification engineer specializing in Design-by-Contract. \
Your job is to write function-level contracts (preconditions, postconditions, \
frame conditions) for Python functions. You write ONLY contracts, not loop \
invariants."""

_PROMPT_TEMPLATE = """\
Write PyCSL function-level contracts for the Python function below.

## PyCSL Contract Syntax (complete reference)

Place contracts as `#@` comments immediately before the `def` keyword, with NO blank lines \
between the last `#@` line and `def`.

- `#@ requires <expr>` — Precondition. What must be true before the function runs.
- `#@ ensures <expr>` — Postcondition. What is guaranteed after it returns. \
Use `\\result` for the return value. For tuples use `\\result[0]`, `\\result[1]`, etc.
- `#@ assigns <var1, var2> | \\nothing` — Frame condition. What mutable state is modified. \
Use `\\nothing` for pure functions. For methods use `self.<field>`.

### Allowed in expressions
- Arithmetic: `+`, `-`, `*`, `//` (integer division)
- Comparisons: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Boolean: `and`, `or`, `not`
- Implication: `==>`, `<==>`
- Array length: `len(arr)`
- Old values: `\\old(var)` (value before function ran)
- Result: `\\result` or `\\result[i]`

### FORBIDDEN in expressions
- NO `/` (use `//`), NO `%` (use mod function), NO `**`
- NO string literals, NO float literals
- NO function calls except `len()`
- NO list comprehensions, NO ternary expressions
- NO `in`, `not in` operators

### Guidelines for strong contracts
- **Capture the function's purpose.** If it counts items, ensure `\\result >= 0` and `\\result <= len(input)`. \
If it returns a tuple of counters that partition an input, ensure they sum to the input length.
- **Use `1 == 1` ONLY as last resort** when no provable property exists (e.g., sum of arbitrary signed integers).
- **Preconditions**: state what the caller must guarantee. If any input works, use `#@ requires 1 == 1`.
- **`assigns`**: list `self.<field>` for methods that modify instance state. Use `\\nothing` for pure functions.
{memory_model_section}
## English Description of the Function

{english_description}

## Function Source Code

```python
{function_source}
```
{class_context_section}
## Output Format

Output ONLY the contract lines (each starting with `#@`), one per line. \
Do NOT output the function body, do NOT output ```python fences, do NOT add commentary. \
Example output:

#@ requires n >= 0
#@ ensures \\result >= 0
#@ ensures \\result <= n
#@ assigns \\nothing"""


def generate(
    function_source: str,
    english_description: str,
    class_context: str,
    memory_model: str,
    model: str,
    project_directory: str,
) -> str:
    """Generate PyCSL function-level contracts for a Python function.

    Args:
        function_source: The raw source code of the function.
        english_description: Plain-English description from agent-english-writer.
        class_context: Optional class header + __init__ for method context.
        memory_model: One of 'hoare', 'typed', 'store'.
        model: LLM model name.
        project_directory: Base directory for logging.

    Returns:
        Contract lines (each starting with #@), newline-separated.
    """
    _model_notes = {
        "hoare": (
            "\n### Active Memory Model: HOARE\n"
            "Value-semantic arrays. No `\\valid`, `\\separated`, or `\\assigns arr[lo..hi]`. "
            "Use `#@ assigns \\nothing` for pure functions.\n"
        ),
        "typed": (
            "\n### Active Memory Model: TYPED\n"
            "Heap-allocated arrays (`loc` type). Use `\\valid(arr, n)`, "
            "`\\separated(a, na, b, nb)`, `\\assigns arr[0..n]`, `\\old(arr[i])`.\n"
        ),
        "store": (
            "\n### Active Memory Model: STORE\n"
            "Same as typed. Use `\\valid`, `\\separated`, `\\assigns arr[0..n]`, `\\old(arr[i])`.\n"
        ),
    }

    class_section = ""
    if class_context:
        class_section = (
            "\n## Class Context\n"
            f"```python\n{class_context}\n```\n"
        )

    prompt = _PROMPT_TEMPLATE.format(
        function_source=function_source,
        english_description=english_description,
        class_context_section=class_section,
        memory_model_section=_model_notes.get(memory_model, _model_notes["hoare"]),
    )

    log(project_directory, AGENT_NAME, "Generating function contracts\n")

    response = llm_generate(
        prompt=prompt,
        system=_SYSTEM_PROMPT,
        agent_id=AGENT_NAME,
        model=model,
    )

    # Extract only #@ lines from the response
    contracts = _extract_contract_lines(response)
    log(project_directory, AGENT_NAME,
        f"Generated {len(contracts.splitlines())} contract lines\n")
    return contracts


def _extract_contract_lines(response: str) -> str:
    """Extract only lines starting with #@ from the LLM response."""
    lines = []
    for line in response.splitlines():
        stripped = line.strip()
        if stripped.startswith("#@"):
            lines.append(stripped)

    if not lines:
        # Fallback: try extracting from code block
        match = re.search(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
        if match:
            for line in match.group(1).splitlines():
                stripped = line.strip()
                if stripped.startswith("#@"):
                    lines.append(stripped)

    # Ensure minimum required contracts
    has_requires = any("requires" in l for l in lines)
    has_ensures = any("ensures" in l for l in lines)
    has_assigns = any("assigns" in l for l in lines)

    if not has_requires:
        lines.insert(0, "#@ requires 1 == 1")
    if not has_ensures:
        lines.append("#@ ensures 1 == 1")
    if not has_assigns:
        lines.append("#@ assigns \\nothing")

    return "\n".join(lines)
