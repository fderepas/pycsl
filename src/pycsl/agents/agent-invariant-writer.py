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
by SMT solvers via WhyML."""


def _build_prompt(
    function_source: str,
    contracts: str,
    callee_contracts: str,
    class_context: str,
    memory_model: str,
    skill_content: str,
) -> str:
    """Build the prompt for the invariant-writer agent."""
    _model_notes = {
        "hoare": (
            "Value-semantic arrays (`array int`). No `\\valid`, `\\separated`, "
            "or `\\assigns arr[lo..hi]`. Use `#@ assigns \\nothing` for pure functions."
        ),
        "typed": (
            "Heap-allocated arrays (`loc` type). Use `\\valid(arr, n)`, "
            "`\\separated(a, na, b, nb)`, `\\assigns arr[0..n]`, `\\old(arr[i])`."
        ),
        "store": (
            "Same as typed. Use `\\valid`, `\\separated`, `\\assigns arr[0..n]`, `\\old(arr[i])`."
        ),
    }

    parts = []

    # Include skill content for transpiler limits and solver heuristics
    if skill_content:
        parts.append(skill_content)

    parts.append(
        f"\n\n# ACTIVE MEMORY MODEL: {memory_model.upper()}\n"
        f"The pipeline is configured to use the `{memory_model}` memory model. "
        + _model_notes.get(memory_model, _model_notes["hoare"])
    )

    parts.append(
        "\n\n# TASK\n"
        "You are given a Python function and its already-written function-level contracts. "
        "Your job is to:\n"
        "1. Insert the contracts immediately before the `def` line (no blank lines between).\n"
        "2. Add `#@ loop invariant` and `#@ loop variant` to EVERY `for` and `while` loop, "
        "placed immediately before the loop keyword.\n"
        "3. Rewrite `for x in collection:` loops to `while` loops with an index variable "
        "when needed for PyCSL (PyCSL desugars `for` but explicit `while` is more reliable).\n"
        "4. Add PEP 484 type hints to all parameters and return type.\n"
        "5. Output ONLY the complete annotated function between ```python and ```.\n"
        "\n"
        "## Loop invariant guidelines\n"
        "- Every loop invariant must be true before the loop starts AND preserved by each iteration.\n"
        "- Include bounds on the loop counter: `0 <= i and i <= n`.\n"
        "- Include accumulator properties derived from the postcondition. For example, if the "
        "postcondition says `\\result >= 0`, prove it by showing the accumulator is >= 0 at every step.\n"
        "- If a function counts items (e.g., negatives + zeros + positives), include a conservation "
        "invariant: `negatives + zeros + positives == i` (processed so far).\n"
        "- The loop variant must be a non-negative integer expression that strictly decreases "
        "each iteration (typically `n - i`).\n"
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
    model: str,
    project_directory: str,
) -> str:
    """Generate a fully annotated function with contracts + loop invariants.

    Args:
        function_source: The raw source code of the function.
        contracts: Contract lines from agent-contract-writer (each starting with #@).
        callee_contracts: Contracts of already-annotated callees for context.
        class_context: Optional class header + __init__ for method context.
        memory_model: One of 'hoare', 'typed', 'store'.
        skill_content: Full PyCSL skill content for transpiler/solver guidance.
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
