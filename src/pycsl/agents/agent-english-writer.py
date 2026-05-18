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


def generate(
    function_source: str,
    class_context: str,
    skill_content: str,
    model: str,
    project_directory: str,
) -> str:
    """Generate a plain-English description of a Python function.

    Args:
        function_source: The raw source code of the function.
        class_context: Optional class header + __init__ for method context.
        skill_content: Loaded skill file content with rules and output format.
        model: LLM model name to use.
        project_directory: Base directory for logging.

    Returns:
        A structured English description of the function's semantics.
    """
    parts = []

    if skill_content:
        parts.append(skill_content)

    parts.append(
        "\nAnalyze the following Python function and produce a structured "
        "English description following the rules and format above."
    )

    if class_context:
        parts.append(
            "\n## Class Context\n"
            "This function is a method of the following class:\n\n"
            f"```python\n{class_context}\n```"
        )

    parts.append(f"\n## Function\n\n```python\n{function_source}\n```")

    prompt = "\n".join(parts)

    log(project_directory, AGENT_NAME, "Generating English description\n")

    response = llm_generate(
        prompt=prompt,
        system=_SYSTEM_PROMPT,
        agent_id=AGENT_NAME,
        model=model,
    )

    log(project_directory, AGENT_NAME, f"English description generated ({len(response)} chars)\n")
    return response.strip()
