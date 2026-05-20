"""
agent-infer-invariants.py — Infer loop invariants/variants from existing contracts.

Given a Python file that already has human-written function-level contracts
(#@ requires, #@ ensures, #@ assigns), this script adds #@ loop invariant and
#@ loop variant annotations to every loop inside each annotated function.

It NEVER adds or modifies requires/ensures/assigns contracts.
It NEVER adds \\trusted annotations.

Usage:
    python agent-infer-invariants.py --in <file.py> [--out <file.py>] [--config <path>]
"""

import argparse
import re
import sys
from importlib import util as _importlib_util
from pathlib import Path

# Ensure the agents directory is on sys.path so common/llm_client imports work
_AGENTS_DIR = Path(__file__).parent.resolve()
if str(_AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_DIR))

from common import log  # noqa: E402

AGENT_NAME = "agent-infer-invariants"


def _load_agent(name: str):
    """Load a hyphen-named agent module from the agents directory."""
    spec = _importlib_util.spec_from_file_location(
        name.replace("-", "_"), _AGENTS_DIR / f"{name}.py"
    )
    mod = _importlib_util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _extract_contracts_before(source_lines: list[str], start_line: int) -> tuple[str, int]:
    """Find #@ contract lines that immediately precede the def at start_line.

    Scans backwards from the line before the def, skipping blank lines,
    stopping at the first non-blank non-#@ line.

    Returns (contracts_str, first_contract_line_1based). If no contracts
    are found, returns ("", start_line).
    """
    idx = start_line - 2  # 0-based index of line before def
    found: list[tuple[int, str]] = []

    while idx >= 0:
        stripped = source_lines[idx].rstrip()
        if stripped.strip().startswith("#@"):
            found.append((idx, stripped.strip()))
            idx -= 1
        elif stripped.strip() == "":
            idx -= 1
        else:
            break

    if not found:
        return "", start_line

    found.reverse()
    first_line_1based = found[0][0] + 1  # convert to 1-based
    contracts_str = "\n".join(text for _, text in found)
    return contracts_str, first_line_1based


def _get_class_context(source_lines: list[str], func_info, func_map: dict) -> str:
    """Return class header + __init__ source for a method, or "" for a top-level function."""
    if not func_info.class_name:
        return ""

    class_def_line = ""
    for line in source_lines:
        if re.match(rf"^class {re.escape(func_info.class_name)}\b", line.strip()):
            class_def_line = line.rstrip()
            break

    init_info = func_map.get(f"{func_info.class_name}.__init__")
    parts = []
    if class_def_line:
        parts.append(class_def_line)
    if init_info:
        parts.append(init_info.source)
    return "\n".join(parts)


def _build_callee_contracts(func_info, func_map: dict, done: dict[str, str]) -> str:
    """Build a callee-contracts context string from already-processed callees."""
    parts = []
    for callee_name in sorted(func_info.callees):
        contracts = done.get(callee_name, "")
        if contracts.strip():
            parts.append(f"# {callee_name}\n{contracts}")
    return "\n\n".join(parts)


def _extract_contract_lines(annotated_source: str) -> str:
    """Extract only the #@ lines from an annotated function (for callee context)."""
    lines = [l.strip() for l in annotated_source.splitlines() if l.strip().startswith("#@")]
    return "\n".join(lines)


def process_file(
    input_path: Path,
    output_path: Path,
    config: dict,
    project_directory: str,
) -> int:
    """Infer loop invariants for all annotated functions in input_path.

    Returns the number of functions processed.
    """
    splitter = _load_agent("agent-splitter")
    inv_writer = _load_agent("agent-invariant-writer")

    project_root = _AGENTS_DIR.parent.parent.parent

    model = config.get("model", "claude-sonnet-4.6")
    memory_model = config.get("memory-model", "hoare")

    def _load_skill(key: str) -> str:
        name = config.get(key, "")
        if not name:
            return ""
        p = Path(name)
        if not p.is_absolute():
            p = project_root / p
        if p.exists():
            return p.read_text(encoding="utf-8")
        log(project_directory, AGENT_NAME, f"Warning: skill not found: {p}\n")
        return ""

    skill_content = _load_skill("skill-annotate")
    task_skill_content = _load_skill("skill-invariant-writer")

    source = input_path.read_text(encoding="utf-8")
    source_lines = source.splitlines(keepends=True)

    functions, func_map = splitter._extract_functions(source)
    splitter._build_call_graph(functions, func_map)

    # Process in topological order so callees are done before callers
    sccs = splitter._tarjan_scc(func_map)
    ordered = [
        func_map[name]
        for scc in sccs
        for name in scc
        if name in func_map
    ]

    done_contracts: dict[str, str] = {}
    replacements: list[tuple[int, int, str]] = []

    for func_info in ordered:
        contracts_str, first_contract_line = _extract_contracts_before(
            source_lines, func_info.start_line
        )

        if not contracts_str.strip():
            log(project_directory, AGENT_NAME,
                f"Skip {func_info.name} — no contracts\n")
            continue

        log(project_directory, AGENT_NAME,
            f"Processing {func_info.name} "
            f"(lines {first_contract_line}–{func_info.end_line})\n")

        class_context = _get_class_context(source_lines, func_info, func_map)
        callee_contracts = _build_callee_contracts(func_info, func_map, done_contracts)

        try:
            annotated = inv_writer.generate(
                function_source=func_info.source,
                contracts=contracts_str,
                callee_contracts=callee_contracts,
                class_context=class_context,
                memory_model=memory_model,
                skill_content=skill_content,
                task_skill_content=task_skill_content,
                model=model,
                project_directory=project_directory,
            )
        except Exception as exc:
            log(project_directory, AGENT_NAME,
                f"Error on {func_info.name}: {exc}\n")
            continue

        done_contracts[func_info.name] = _extract_contract_lines(annotated)
        replacements.append((first_contract_line, func_info.end_line, annotated))

    if not replacements:
        log(project_directory, AGENT_NAME, "No annotated functions found — file unchanged\n")
        output_path.write_text(source, encoding="utf-8")
        return 0

    # Apply replacements in reverse line order to preserve indices
    replacements.sort(key=lambda r: r[0], reverse=True)
    lines = list(source_lines)

    for first_line, end_line, new_text in replacements:
        if not new_text.endswith("\n"):
            new_text += "\n"
        new_lines = new_text.splitlines(keepends=True)
        # Replace lines first_line..end_line (1-based, inclusive)
        lines[first_line - 1 : end_line] = new_lines

    output_path.write_text("".join(lines), encoding="utf-8")
    log(project_directory, AGENT_NAME,
        f"Wrote {len(replacements)} annotated functions to {output_path}\n")
    return len(replacements)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add loop invariants/variants to functions that already have contracts."
    )
    parser.add_argument("--in", dest="input_file", required=True,
                        help="Python source file to process (must have human-written contracts).")
    parser.add_argument("--out", dest="output_file", default=None,
                        help="Output file (default: overwrite input).")
    parser.add_argument("--config", dest="config_path",
                        default=None,
                        help="Path to agents-config.json (default: config/agents-config.json).")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output_file) if args.output_file else input_path

    # Resolve config
    project_root = _AGENTS_DIR.parent.parent.parent
    if args.config_path:
        config_path = Path(args.config_path)
    else:
        config_path = project_root / "config" / "agents-config.json"

    if not config_path.exists():
        print(f"Error: config not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    import json
    config = json.loads(config_path.read_text(encoding="utf-8"))
    project_directory = config.get("project-directory", str(project_root))

    log(project_directory, AGENT_NAME,
        f"Starting: {input_path} → {output_path}\n")

    count = process_file(input_path, output_path, config, project_directory)
    print(f"Done — {count} function(s) processed.")


if __name__ == "__main__":
    main()
