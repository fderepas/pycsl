"""
agent-english-writer.py — Step 1 of the 3-agent annotation pipeline.

Reads a Python function and produces a plain-English description of:
- What the function computes
- What properties hold on the return value
- Edge cases and preconditions
- What variables are mutated

This agent has NO knowledge of PyCSL. Its output is consumed by
agent-contract-writer.py which translates it into formal contracts.
"""

from llm_client import llm_generate, log

AGENT_NAME = "agent-english-writer"

_SYSTEM_PROMPT = """\
You are a senior software engineer performing code review. Your job is to \
describe what a Python function does in precise, mathematical English. \
You are NOT writing code — only English prose."""

_PROMPT_TEMPLATE = """\
Analyze the following Python function and produce a structured English description.

## Rules
- Be precise and mathematical — use phrases like "the return value is always ≥ 0" \
or "the sum of all three counters equals len(values)".
- Describe the return value type and what each component means (for tuples, describe each element).
- List any preconditions the caller must satisfy (e.g., "values must be a list of integers").
- List any variables that are mutated (instance attributes via self, global state, list parameters).
- If the function has loops, describe what quantity changes each iteration and why it terminates.
- Do NOT mention any annotation language, contracts, or formal verification.
- Keep it concise — aim for 5–15 lines.

## Format
Return your answer in this exact format:

DESCRIPTION: <what the function does>
RETURN VALUE: <type and properties of the return value>
PRECONDITIONS: <what must be true before calling, or "None">
MUTATIONS: <what state is modified, or "None">
LOOP PROPERTIES: <for each loop: what changes, what is preserved, why it terminates — or "No loops">
{class_context_section}
## Function

```python
{function_source}
```"""


def generate(
    function_source: str,
    class_context: str,
    model: str,
    project_directory: str,
) -> str:
    """Generate a plain-English description of a Python function.

    Args:
        function_source: The raw source code of the function.
        class_context: Optional class header + __init__ for method context.
        model: LLM model name to use.
        project_directory: Base directory for logging.

    Returns:
        A structured English description of the function's semantics.
    """
    class_section = ""
    if class_context:
        class_section = (
            "\n## Class Context\n"
            "This function is a method of the following class:\n\n"
            f"```python\n{class_context}\n```\n"
        )

    prompt = _PROMPT_TEMPLATE.format(
        function_source=function_source,
        class_context_section=class_section,
    )

    log(project_directory, AGENT_NAME, "Generating English description\n")

    response = llm_generate(
        prompt=prompt,
        system=_SYSTEM_PROMPT,
        agent_id=AGENT_NAME,
        model=model,
    )

    log(project_directory, AGENT_NAME, f"English description generated ({len(response)} chars)\n")
    return response.strip()
