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
    module_brief: str = "",
    callee_contracts: str = "",
    callee_sources: str = "",
    catalog_seed: str = "",
    formal_model_hint: str = "",
) -> str:
    """Generate a plain-English description of a Python function.

    Args:
        function_source: The raw source code of the function.
        class_context: Optional class header + __init__ for method context.
        skill_content: Loaded skill file content with rules and output format.
        model: LLM model name to use.
        project_directory: Base directory for logging.
        module_brief: Optional module-level architectural brief.
        callee_contracts: Optional contracts of called functions.
        callee_sources: Optional source snippets of called functions.
        catalog_seed: Optional pre-generated description to refine.
        formal_model_hint: Optional formal model context from catalog.

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

    if module_brief:
        parts.append(
            "\n## Module Context\n"
            "This function belongs to the following module:\n\n"
            f"{module_brief}"
        )

    if class_context:
        parts.append(
            "\n## Class Context\n"
            "This function is a method of the following class:\n\n"
            f"```python\n{class_context}\n```"
        )

    if callee_contracts:
        parts.append(
            "\n## Callee Contracts\n"
            "The following functions are called by this function and have "
            "already been annotated with formal contracts:\n\n"
            f"{callee_contracts}"
        )

    if callee_sources:
        parts.append(
            "\n## Callee Source Code\n"
            "Source snippets of key called functions:\n\n"
            f"{callee_sources}"
        )

    if catalog_seed:
        parts.append(
            "\n## Pre-generated Description (seed)\n"
            "A previous analysis generated the following description. "
            "Refine and improve it based on the actual source code.\n\n"
            f"{catalog_seed}"
        )

    if formal_model_hint:
        parts.append(
            "\n## Formal Model Context\n"
            "A previous analysis identified the following formal model "
            "correspondence. Incorporate this into your description if "
            "applicable:\n\n"
            f"{formal_model_hint}"
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
