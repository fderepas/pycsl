"""
agent-invariant-writer.py — Step 3 of the 3-agent annotation pipeline.

Receives a Python function + function-level contracts (from agent-contract-writer)
+ callee contracts (from the splitter) and produces the fully annotated function:
  - Inserts the contracts before the def line
  - Adds #@ loop invariant and #@ loop variant to every loop
  - Rewrites for loops to while loops where needed for PyCSL
  - Adds PEP 484 type hints
"""

import re
import sys
from pathlib import Path

from llm_client import llm_generate, log

AGENT_NAME = "agent-invariant-writer"

_SYSTEM_PROMPT = """\
You are a formal verification engineer. Your job is to take a Python function \
that already has function-level contracts (#@ requires, #@ ensures, #@ assigns) \
and add loop invariants and loop variants so the function can be proved correct \
by SMT solvers via WhyML. In concurrent mode outer while-True loops need no \
invariant or variant; loops inside critical sections annotate only local variables."""


def _build_prompt(
    function_source: str,
    contracts: str,
    callee_contracts: str,
    class_context: str,
    memory_model: str,
    skill_content: str,
    task_skill_content: str,
) -> str:
    """Build the prompt for the invariant-writer agent."""
    parts = []

    # Include full PyCSL skill for transpiler limits and solver heuristics
    if skill_content:
        parts.append(skill_content)

    # Include task-specific skill (loop invariant guidelines)
    if task_skill_content:
        parts.append("\n\n" + task_skill_content)
    else:
        # Fallback: minimal inline instructions if skill file not available
        parts.append(
            f"\n\n# ACTIVE MEMORY MODEL: {memory_model.upper()}\n"
            "Add loop invariants and loop variants to every loop. "
            "Include counter bounds, accumulator properties, and a decreasing variant."
        )

    if memory_model == "concurrent":
        parts.append(
            "\n\n## Concurrent Model — Loop Annotation Rules\n\n"
            "- Outer `while True:` loop in a `#@ thread_entry` function: "
            "write NO `#@ loop invariant` and NO `#@ loop variant`. "
            "The `#@ \\diverges` annotation already handles the non-termination claim.\n"
            "- Loops INSIDE a `#@ critical <mutex>` block: do NOT add loop invariants "
            "that reference shared variables protected by `<mutex>`. "
            "The critical section boundary (havoc + assume + assert) manages those. "
            "DO add normal loop invariants/variants for loops over local variables.\n"
            "- Helper functions (not `#@ thread_entry`) called inside a critical section: "
            "apply standard loop invariant rules — they operate on local parameters only.\n"
        )

    parts.append(
        "\n\n# FUNCTION-LEVEL CONTRACTS (already decided)\n"
        "These contracts have been chosen for this function. Insert them as-is before the `def` line.\n\n"
        f"{contracts}\n"
    )

    if callee_contracts:
        parts.append(
            "\n\n# CALLEE CONTRACTS (already verified)\n"
            "Use these to write tighter invariants for this function.\n\n"
            + callee_contracts
        )

    if class_context:
        parts.append(
            "\n\n# CLASS CONTEXT\n"
            f"```python\n{class_context}\n```\n"
        )

    parts.append(f"\n\n# FUNCTION TO ANNOTATE\n\n```python\n{function_source}\n```")

    return "\n".join(parts)


def generate(
    function_source: str,
    contracts: str,
    callee_contracts: str,
    class_context: str,
    memory_model: str,
    skill_content: str,
    task_skill_content: str,
    model: str,
    project_directory: str,
) -> str:
    """Generate a fully annotated function with contracts + loop invariants.

    Args:
        function_source: The raw source code of the function.
        contracts: Contract lines from agent-contract-writer (each starting with #@).
        callee_contracts: Contracts of already-annotated callees for context.
        class_context: Optional class header + __init__ for method context.
        memory_model: One of 'hoare', 'typed', 'store', 'concurrent'.
        skill_content: Full PyCSL skill content for transpiler/solver guidance.
        task_skill_content: Task-specific skill (loop invariant guidelines).
        model: LLM model name.
        project_directory: Base directory for logging.

    Returns:
        The complete annotated function source code.
    """
    prompt = _build_prompt(
        function_source=function_source,
        contracts=contracts,
        callee_contracts=callee_contracts,
        class_context=class_context,
        memory_model=memory_model,
        skill_content=skill_content,
        task_skill_content=task_skill_content,
    )

    log(project_directory, AGENT_NAME, "Generating loop invariants and final annotation\n")

    response = llm_generate(
        prompt=prompt,
        system=_SYSTEM_PROMPT,
        agent_id=AGENT_NAME,
        model=model,
    )

    # Extract code from markdown fences
    annotated = _extract_code_block(response)

    log(project_directory, AGENT_NAME,
        f"Annotated function generated ({len(annotated)} chars)\n")
    return annotated


def _extract_code_block(text: str) -> str:
    """Extract code from markdown fences, falling back to raw text."""
    pattern = r"```python\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)

    pattern = r"```\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)

    return text
