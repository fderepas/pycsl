import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from llm_client import llm_generate, log
from common import retrieve_skill_chunks, extract_code_block

AGENT_NAME = "agent-reconcile"

# Fixed queries to always retrieve critical reconciliation context.
_ESSENTIAL_QUERIES = [
    "Module5 IR emitter statement expression handler dispatch",
    "Module6 WhyML transpiler expression statement memory model",
    "Forbidden in contract expressions NEVER use operators",
    "Required on every function requires ensures assigns",
]


def read_text(path: Path, project_directory: Path, label: str) -> str:
    if not path.exists():
        log(project_directory, AGENT_NAME, f"Error: {label} file not found at {path}")
        sys.exit(1)

    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        log(project_directory, AGENT_NAME, f"Error reading {label} file at {path}: {exc}")
        sys.exit(1)


def load_config(project_root: Path) -> dict[str, Any]:
    config_path = project_root / "config" / "agents-config.json"
    if not config_path.exists():
        log(project_root, AGENT_NAME, f"Error: Configuration file not found at {config_path}")
        sys.exit(1)

    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log(project_root, AGENT_NAME, f"Error parsing {config_path}: {exc}")
        sys.exit(1)


def require_config_key(config: dict[str, Any], key: str, project_directory: Path, config_path: Path) -> Any:
    if key not in config:
        log(project_directory, AGENT_NAME, f"Error: Missing required key '{key}' in {config_path}")
        sys.exit(1)
    return config[key]


def read_optional_file(path: Path) -> str | None:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = stripped[start : end + 1]
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed

    raise json.JSONDecodeError("Could not extract JSON object", text, 0)


def build_prompt(
    *,
    skill_annotator: str,
    skill_agents: str,
    skill_module5: str,
    skill_module6: str,
    memory_model: str,
    script_path: Path,
    script_content: str,
    stdout_path: Path,
    stdout_content: str,
    stderr_path: Path,
    stderr_content: str,
    ret_code: str,
    whyml_path: Path | None,
    whyml_content: str | None,
    rag_context: str | None = None,
) -> str:
    _memory_model_notes = {
        "hoare": (
            "Value-semantic arrays (`array int`). No heap. "
            "Common errors: missing `use array.Array`, `array int` type mismatch."
        ),
        "typed": (
            "Heap-based model. Arrays become `(arr: loc) (arr_len: int)` parameters. "
            "Heap variable: `int_mem : ref (map loc int)`. "
            "Reads: `Map.get !int_mem (arr + i)`. Writes: `int_mem := Map.set !int_mem (arr + i) v`. "
            "Predicates: `\\valid(arr, n)`, `\\separated(a, na, b, nb)`. "
            "Frame: `\\assigns arr[lo..hi]`. Pre-state: `\\old(arr[i])`. "
            "Labels: `#@ label L` / `\\at(arr[i], L)`. "
            "Common errors: `Cannot find theory Map`, `type mismatch loc vs array int`, "
            "`arr_len unbound`, label not found."
        ),
        "store": (
            "Identical to typed model but heap variable is named `store` (not `int_mem`). "
            "Same predicates, parameters, and error patterns as typed."
        ),
    }
    model_note = _memory_model_notes.get(memory_model, _memory_model_notes["hoare"])

    sections = [
        "You are an expert Python developer and PyCSL reconciliation agent.",
        "Given the failure context below, determine the most appropriate action to perform and return ONLY valid JSON.",
        "",
        "Return an object with these required fields:",
        '- "language": the programming language of the program.',
        '- "author": the author or creator of the program.',
        '- "recommendation": a concise recommendation for the action to perform.',
        '- "target": one of "update-pycsl-scripts", "error-in-annotations", or "unknown".',
        '- "fault_class": one of "sub-actor", "specifier", or "verifier" — the CMMI',
        "  cross-level routing class:",
        '    * "sub-actor": the failure is in THIS function\'s body or its own annotations',
        "      (a per-unit fix); this is the default for most annotation errors.",
        '    * "specifier": the failure is caused by how the FILE was decomposed — wrong',
        "      callee-contract assumptions, missing/incorrect interface contracts between",
        "      functions, or an ordering that makes this unit unprovable in isolation. It",
        "      cannot be fixed in this unit alone; the file must be re-decomposed.",
        '    * "verifier": the proof obligations themselves are mis-scoped (rare).',
        "",
        "Use the following context and skills:",
        f"--- ACTIVE MEMORY MODEL: {memory_model.upper()} ---",
        model_note,
        "",
    ]

    if rag_context:
        sections.extend([
            "--- RELEVANT SKILL KNOWLEDGE (RAG-retrieved) ---",
            rag_context,
            "",
        ])
    else:
        sections.extend([
            "--- SKILL ANNOTATOR ---",
            skill_annotator,
            "",
            "--- SKILL AGENTS ---",
            skill_agents,
            "",
            "--- SKILL MODULE 5 ---",
            skill_module5,
            "",
            "--- SKILL MODULE 6 ---",
            skill_module6,
            "",
        ])

    sections.extend([
        "--- TARGET SCRIPT ---",
        f"Path: {script_path}",
        script_content,
        "",
        "--- STANDARD OUTPUT ---",
        f"Path: {stdout_path}",
        stdout_content,
        "",
        "--- STANDARD ERROR ---",
        f"Path: {stderr_path}",
        stderr_content,
        "",
        "--- RETURN CODE ---",
        ret_code,
    ])

    if whyml_path is not None and whyml_content is not None:
        sections.extend(
            [
                "",
                "--- WHYML SCRIPT ---",
                f"Path: {whyml_path}",
                whyml_content,
            ]
        )

    sections.extend(
        [
            "",
            "Constraints:",
            "- Just output the JSON between \"```json\" and \"```\".",
            "- Output raw JSON only, with no extra commentary.",
            "- Base the recommendation on whether the failure is in annotations or in the PyCSL scripts themselves.",
            f"- The active memory model is `{memory_model}`. Consider model-specific errors:",
            "  * \'error-in-annotations\': wrong \\valid/\\separated syntax, missing \\assigns region, bad #@ label placement, \\at label not found.",
            "  * \'update-pycsl-scripts\': Module6 missing Map preamble, loc vs array int type mismatch, arr_len parameter not emitted.",
        ]
    )
    return "\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a reconciliation prompt and JSON response for a failing PyCSL run."
    )
    parser.add_argument("--script", required=True, help="Path to the Python file under analysis.")
    parser.add_argument("--out", required=True, dest="out_file_name", help="Path to the output JSON file.")
    parser.add_argument("--stdout", required=True, help="Path to the captured standard output.")
    parser.add_argument("--stderr", required=True, help="Path to the captured standard error.")
    parser.add_argument("--ret-code", required=True, dest="ret_code", help="The captured return code.")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent  # src/pycsl/agents -> project root
    config = load_config(project_root)
    config_path = project_root / "config" / "agents-config.json"

    model = require_config_key(config, "model", project_root, config_path)
    project_directory = Path(str(require_config_key(config, "project-directory", project_root, config_path))).expanduser().resolve()
    memory_model = config.get("memory-model", "hoare")
    rag_index_name = config.get("rag-index")
    rag_top_k = config.get("rag-top-k", 10)
    log(project_directory, AGENT_NAME, f"Memory model: {memory_model}")
    skill_annotator_name = str(require_config_key(config, "skill-annotate", project_root, config_path))
    skill_agents_name = str(require_config_key(config, "skill-agents", project_root, config_path))
    skill_module5_name = str(require_config_key(config, "skill-module5", project_root, config_path))
    skill_module6_name = str(require_config_key(config, "skill-module6", project_root, config_path))

    def resolve_relative(name: str) -> Path:
        path = Path(name)
        return path if path.is_absolute() else project_root / path

    script_path = Path(args.script)
    stdout_path = Path(args.stdout)
    stderr_path = Path(args.stderr)

    script_content = read_text(script_path, project_directory, "target script")
    stdout_content = read_text(stdout_path, project_directory, "stdout")
    stderr_content = read_text(stderr_path, project_directory, "stderr")

    # Try RAG retrieval using error context as the query
    rag_context = None
    if rag_index_name:
        rag_index_path = resolve_relative(rag_index_name)
        error_query = f"{stderr_content}\n\n{script_content[:500]}"
        rag_context = retrieve_skill_chunks(
            index_path=rag_index_path,
            main_query=error_query[:1500],
            top_k=rag_top_k,
            project_root=project_root,
            essential_queries=_ESSENTIAL_QUERIES,
        )
        if rag_context:
            log(project_directory, AGENT_NAME, "Using RAG-retrieved skill chunks")

    # Load full skill files as fallback (or when RAG not available)
    if rag_context is None:
        log(project_directory, AGENT_NAME, "Using full skill files (RAG index unavailable)")
    skill_annotator = read_text(resolve_relative(skill_annotator_name), project_directory, "skill-annotate")
    skill_agents = read_text(resolve_relative(skill_agents_name), project_directory, "skill-agents")
    skill_module5 = read_text(resolve_relative(skill_module5_name), project_directory, "skill-module5")
    skill_module6 = read_text(resolve_relative(skill_module6_name), project_directory, "skill-module6")

    whyml_path = script_path.with_suffix(".mlw") if script_path.suffix == ".py" else script_path.with_suffix(".mlw")
    whyml_content = read_optional_file(whyml_path)

    prompt = build_prompt(
        skill_annotator=skill_annotator,
        skill_agents=skill_agents,
        skill_module5=skill_module5,
        skill_module6=skill_module6,
        memory_model=memory_model,
        script_path=script_path,
        script_content=script_content,
        stdout_path=stdout_path,
        stdout_content=stdout_content,
        stderr_path=stderr_path,
        stderr_content=stderr_content,
        ret_code=args.ret_code,
        whyml_path=whyml_path if whyml_content is not None else None,
        whyml_content=whyml_content,
        rag_context=rag_context,
    )

    try:
        llm_response = llm_generate(prompt=prompt, system="", agent_id=AGENT_NAME, model=model)
    except Exception as exc:
        log(project_directory, AGENT_NAME, f"Error calling llm_generate: {exc}")
        sys.exit(1)

    # Extract JSON from markdown fences if present
    llm_response = extract_code_block(llm_response, "json")

    try:
        result = extract_json_object(llm_response)
    except json.JSONDecodeError as exc:
        log(project_directory, AGENT_NAME, f"Error: LLM response was not valid JSON: {exc}")
        sys.exit(1)

    required_keys = ("language", "author", "recommendation", "target")
    missing = [key for key in required_keys if key not in result]
    if missing:
        log(project_directory, AGENT_NAME, f"Error: LLM response is missing required keys: {', '.join(missing)}")
        sys.exit(1)

    # Cross-level routing class (consumed by coordinator.route): default to
    # "sub-actor" (the per-unit fix path) when the model omits or mis-fills it,
    # preserving prior behavior and satisfying the reconcile schema.
    if result.get("fault_class") not in ("sub-actor", "specifier", "verifier"):
        result["fault_class"] = "sub-actor"

    out_path = Path(args.out_file_name)
    try:
        from schema_validator import validate_or_warn
        validate_or_warn(result, "reconcile",
                         logger=lambda msg: log(project_directory, AGENT_NAME, msg))
    except ImportError:
        pass
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError as exc:
        log(project_directory, AGENT_NAME, f"Error writing output file {out_path}: {exc}")
        sys.exit(1)

    log(project_directory, AGENT_NAME, f"Successfully saved reconciliation JSON to {out_path}")


if __name__ == "__main__":
    main()
