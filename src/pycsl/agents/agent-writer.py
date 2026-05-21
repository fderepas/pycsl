"""
agent-writer.py — Coordinator for the 3-agent annotation pipeline.

Receives a single function (or small SCC group) via stdin as JSON and produces
the fully annotated function on stdout. Internally orchestrates three agents:

  1. agent-english-writer  — plain-English description of the function
  2. agent-contract-writer  — function-level contracts (#@ requires/ensures/assigns)
  3. agent-invariant-writer — loop invariants/variants + final assembly

Falls back to the original monolithic single-LLM-call approach if any sub-agent
fails, so the pipeline is never worse than before.

Input (JSON on stdin):
  - function_source: str    — the raw function source code to annotate
  - callee_contracts: str   — #@ contract lines of already-annotated callees
  - class_context: str      — optional class header + __init__ for method context
  - module_brief: str       — optional module-level architectural brief
  - callee_sources: str     — optional source snippets of key callees

CLI args:
  --memory-model {hoare|typed|store}
  --config <path-to-agents-config.json>
"""

import argparse
import json
import re
import sys
from pathlib import Path

from llm_client import llm_generate, log
from common import retrieve_skill_chunks, extract_code_block

AGENT_NAME = "agent-writer"

# Fixed queries used to always retrieve critical skill sections regardless of input code.
_ESSENTIAL_QUERIES = [
    "Required on every function requires ensures assigns loop invariant loop variant",
    "Forbidden in contract expressions NEVER use operators quantifiers",
    "Class support method annotation rules class invariant Level 2 Level 3",
]


def _build_monolithic_prompt(
    skill_content: str,
    function_source: str,
    callee_contracts: str,
    class_context: str,
    memory_model: str,
    module_brief: str = "",
) -> str:
    """Build the legacy single-LLM-call prompt (used as fallback)."""
    _model_notes = {
        "hoare": (
            "Use standard value-semantic arrays (`array int`). "
            "No `\\valid`, `\\separated`, or `\\assigns arr[lo..hi]` needed. "
            "Use `#@ assigns \\nothing` for pure functions."
        ),
        "typed": (
            "Arrays are heap-allocated (`loc` type). "
            "Use `#@ requires \\valid(arr, n)` to assert array validity. "
            "Use `#@ requires \\separated(a, na, b, nb)` when arrays must not alias. "
            "Use `#@ assigns arr[0..n]` (with `..`) as the frame condition for in-place mutations. "
            "Use `\\old(arr[i])` in ensures clauses to refer to the pre-state value of `arr[i]`. "
            "Use `#@ label L` immediately before a statement to mark a program point, "
            "then `\\at(arr[i], L)` in contracts to reference the array state at that point."
        ),
        "store": (
            "Same as typed model: arrays are heap-allocated. "
            "Use `#@ requires \\valid(arr, n)`, `#@ requires \\separated(a, na, b, nb)`, "
            "`#@ assigns arr[0..n]`, `\\old(arr[i])`, `#@ label L`, and `\\at(arr[i], L)` "
            "as needed for heap-aware contracts."
        ),
    }

    memory_ctx = (
        f"\n\n# ACTIVE MEMORY MODEL: {memory_model.upper()}\n"
        f"The pipeline is configured to use the `{memory_model}` memory model. "
        + _model_notes.get(memory_model, _model_notes["hoare"])
    )

    parts = [skill_content, memory_ctx]

    if module_brief:
        parts.append(
            "\n\n# MODULE CONTEXT\n"
            "This function belongs to the following module. Use this to understand "
            "the architectural role and naming conventions.\n\n"
            + module_brief
        )

    parts.append(
        "\n\n# TASK\n"
        "You are annotating a SINGLE function (not a whole file). "
        "Output ONLY the annotated function with `#@` contract comments. "
        "Do NOT add imports, class definitions, or any code outside this function. "
        "Output the code between ```python and ```.\n\n"
        "CRITICAL: Do NOT modify, rewrite, simplify, or omit any line of the "
        "function body. The body must remain EXACTLY as given — character for "
        "character. You may ONLY add `#@` annotation lines before `def` and "
        "inside loops. Everything else must be unchanged."
    )

    if callee_contracts:
        parts.append(
            "\n\n# CALLEE CONTRACTS (already verified)\n"
            "The following functions have already been annotated and verified. "
            "Use their contracts to write tighter invariants for this function.\n\n"
            + callee_contracts
        )

    if class_context:
        parts.append(
            "\n\n# CLASS CONTEXT\n"
            "This function is a method of the following class:\n\n"
            + class_context
        )

    parts.append(f"\n\n# FUNCTION TO ANNOTATE\n\n{function_source}")

    return "\n".join(parts)


def _run_3agent_pipeline(
    function_source: str,
    callee_contracts: str,
    class_context: str,
    memory_model: str,
    skill_content: str,
    english_writer_skill: str,
    contract_writer_skill: str,
    invariant_writer_skill: str,
    model: str,
    project_directory: str,
    module_brief: str = "",
    callee_sources: str = "",
    catalog_seed: str = "",
    assigns_hint: str = "",
    formal_model_hint: str = "",
) -> str:
    """Run the 3-agent pipeline: english → contracts → invariants.

    Raises on failure so the caller can fall back to the monolithic approach.
    """
    # Import sub-agents (they live in the same directory)
    from importlib import util as _importlib_util

    agents_dir = Path(__file__).parent

    def _load_module(name: str):
        spec = _importlib_util.spec_from_file_location(
            name, agents_dir / f"{name}.py"
        )
        mod = _importlib_util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    english_writer = _load_module("agent-english-writer")
    contract_writer = _load_module("agent-contract-writer")
    invariant_writer = _load_module("agent-invariant-writer")

    # Step 1: English description
    log(project_directory, AGENT_NAME, "Pipeline step 1/3: English description\n")
    english_desc = english_writer.generate(
        function_source=function_source,
        class_context=class_context,
        skill_content=english_writer_skill,
        model=model,
        project_directory=project_directory,
        module_brief=module_brief,
        callee_contracts=callee_contracts,
        callee_sources=callee_sources,
        catalog_seed=catalog_seed,
        formal_model_hint=formal_model_hint,
    )
    if not english_desc.strip():
        raise RuntimeError("English writer returned empty description")

    # Step 2: Function-level contracts
    log(project_directory, AGENT_NAME, "Pipeline step 2/3: Function contracts\n")
    contracts = contract_writer.generate(
        function_source=function_source,
        english_description=english_desc,
        class_context=class_context,
        memory_model=memory_model,
        skill_content=contract_writer_skill,
        model=model,
        project_directory=project_directory,
        module_brief=module_brief,
        callee_contracts=callee_contracts,
        catalog_seed=catalog_seed,
        assigns_hint=assigns_hint,
    )
    if not contracts.strip():
        raise RuntimeError("Contract writer returned empty contracts")

    # Step 3: Loop invariants + final assembly
    log(project_directory, AGENT_NAME, "Pipeline step 3/3: Loop invariants\n")
    annotated = invariant_writer.generate(
        function_source=function_source,
        contracts=contracts,
        callee_contracts=callee_contracts,
        class_context=class_context,
        memory_model=memory_model,
        skill_content=skill_content,
        task_skill_content=invariant_writer_skill,
        model=model,
        project_directory=project_directory,
        module_brief=module_brief,
    )
    if not annotated.strip():
        raise RuntimeError("Invariant writer returned empty output")

    return annotated


def main():
    parser = argparse.ArgumentParser(
        description="Annotate a single Python function with PyCSL contracts."
    )
    parser.add_argument("--memory-model", default="hoare",
                        choices=["hoare", "typed", "store"],
                        help="Memory model for the contracts.")
    parser.add_argument("--config", required=True,
                        help="Path to agents-config.json.")
    args = parser.parse_args()

    config_path = Path(args.config)
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.parent.parent

    if not config_path.exists():
        log(".", AGENT_NAME, f"Error: config not found at {config_path}")
        sys.exit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    project_directory = config.get("project-directory", str(project_root))
    model = config.get("model")
    skill_annotator_name = config.get("skill-annotate")
    rag_index_name = config.get("rag-index")
    rag_top_k = config.get("rag-top-k", 10)

    # Sub-agent skill paths
    skill_english_name = config.get("skill-english-writer")
    skill_contract_name = config.get("skill-contract-writer")
    skill_invariant_name = config.get("skill-invariant-writer")

    if not model:
        log(project_directory, AGENT_NAME, "Error: 'model' missing in config")
        sys.exit(1)
    if not skill_annotator_name:
        log(project_directory, AGENT_NAME, "Error: 'skill-annotate' missing in config")
        sys.exit(1)

    # Read input from stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        log(project_directory, AGENT_NAME, f"Error: invalid JSON on stdin: {e}")
        sys.exit(1)

    function_source = input_data.get("function_source", "")
    callee_contracts = input_data.get("callee_contracts", "")
    class_context = input_data.get("class_context", "")
    module_brief = input_data.get("module_brief", "")
    callee_sources = input_data.get("callee_sources", "")
    catalog_seed = input_data.get("catalog_seed", "")
    assigns_hint = input_data.get("assigns_hint", "")
    formal_model_hint = input_data.get("formal_model_hint", "")

    if not function_source.strip():
        log(project_directory, AGENT_NAME, "Error: empty function_source")
        sys.exit(1)

    # Load skill content (RAG or full file)
    skill_content = None
    if rag_index_name:
        rag_index_path = Path(rag_index_name)
        if not rag_index_path.is_absolute():
            rag_index_path = project_root / rag_index_path
        _code_query = function_source[:800]
        _func_sigs = re.findall(r'^[ \t]*(?:class|def)\s+[^\n]+', function_source, re.MULTILINE)
        if _func_sigs:
            _code_query += "\n" + "\n".join(_func_sigs[:5])
        skill_content = retrieve_skill_chunks(
            index_path=rag_index_path,
            main_query=_code_query,
            top_k=rag_top_k,
            project_root=project_root,
            essential_queries=_ESSENTIAL_QUERIES,
        )
        if skill_content:
            log(project_directory, AGENT_NAME, "Using RAG-retrieved skill chunks\n")

    if skill_content is None:
        skill_annotator_path = Path(skill_annotator_name)
        if not skill_annotator_path.is_absolute():
            skill_annotator_path = project_root / skill_annotator_path
        if not skill_annotator_path.exists():
            log(project_directory, AGENT_NAME,
                f"Error: skill file not found at {skill_annotator_path}")
            sys.exit(1)
        skill_content = skill_annotator_path.read_text(encoding="utf-8")
        log(project_directory, AGENT_NAME, "Using full skill file (RAG unavailable)\n")

    # Load sub-agent skill files
    def _load_skill(name, key):
        if not name:
            return ""
        p = Path(name)
        if not p.is_absolute():
            p = project_root / p
        if p.exists():
            log(project_directory, AGENT_NAME, f"Loaded skill: {key}\n")
            return p.read_text(encoding="utf-8")
        log(project_directory, AGENT_NAME, f"Skill file not found: {p}\n")
        return ""

    english_writer_skill = _load_skill(skill_english_name, "skill-english-writer")
    contract_writer_skill = _load_skill(skill_contract_name, "skill-contract-writer")
    invariant_writer_skill = _load_skill(skill_invariant_name, "skill-invariant-writer")

    # Try the 3-agent pipeline first; fall back to monolithic on failure
    try:
        generated_code = _run_3agent_pipeline(
            function_source=function_source,
            callee_contracts=callee_contracts,
            class_context=class_context,
            memory_model=args.memory_model,
            skill_content=skill_content,
            english_writer_skill=english_writer_skill,
            contract_writer_skill=contract_writer_skill,
            invariant_writer_skill=invariant_writer_skill,
            model=model,
            project_directory=project_directory,
            module_brief=module_brief,
            callee_sources=callee_sources,
            catalog_seed=catalog_seed,
            assigns_hint=assigns_hint,
            formal_model_hint=formal_model_hint,
        )
        log(project_directory, AGENT_NAME, "3-agent pipeline succeeded\n")
    except Exception as e:
        log(project_directory, AGENT_NAME,
            f"3-agent pipeline failed ({e}), falling back to monolithic LLM call\n")
        prompt = _build_monolithic_prompt(
            skill_content=skill_content,
            function_source=function_source,
            callee_contracts=callee_contracts,
            class_context=class_context,
            memory_model=args.memory_model,
            module_brief=module_brief,
        )
        try:
            generated_code = llm_generate(
                prompt=prompt, system="", agent_id=AGENT_NAME, model=model
            )
        except Exception as e2:
            log(project_directory, AGENT_NAME, f"Error calling LLM: {e2}")
            sys.exit(1)
        generated_code = extract_code_block(generated_code, "python")

    # Write annotated function to stdout
    sys.stdout.write(generated_code)


if __name__ == "__main__":
    main()
