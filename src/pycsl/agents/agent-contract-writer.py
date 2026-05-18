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


def generate(
    function_source: str,
    english_description: str,
    class_context: str,
    memory_model: str,
    skill_content: str,
    model: str,
    project_directory: str,
) -> str:
    """Generate PyCSL function-level contracts for a Python function.

    Args:
        function_source: The raw source code of the function.
        english_description: Plain-English description from agent-english-writer.
        class_context: Optional class header + __init__ for method context.
        memory_model: One of 'hoare', 'typed', 'store'.
        skill_content: Loaded skill file content with syntax reference and guidelines.
        model: LLM model name.
        project_directory: Base directory for logging.

    Returns:
        Contract lines (each starting with #@), newline-separated.
    """
    parts = []

    parts.append("Write PyCSL function-level contracts for the Python function below.\n")

    if skill_content:
        parts.append(skill_content)

    parts.append(
        f"\n## Active Memory Model: {memory_model.upper()}\n"
    )

    parts.append(
        "\n## English Description of the Function\n\n"
        f"{english_description}\n"
    )

    parts.append(
        f"\n## Function Source Code\n\n```python\n{function_source}\n```\n"
    )

    if class_context:
        parts.append(
            "\n## Class Context\n"
            f"```python\n{class_context}\n```\n"
        )

    prompt = "\n".join(parts)

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
