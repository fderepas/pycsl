#!/usr/bin/env python3
"""
Agent Script Update - Applies reconciliation recommendations to PyCSL scripts.

This agent receives a reconciliation JSON from agent-reconcile.py and applies
the recommended changes to Module*.py or agent-*.py files using the MCP server.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Optional

from llm_client import llm_generate, log

AGENT_NAME = "agent-script-update"


def extract_code_block(text: str, language: str) -> str:
    """Extract code block from markdown fences or return original text."""
    import re
    # Try language-specific fence first
    pattern = rf"\`\`\`{language}\n(.*?)\n\`\`\`"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    # Try generic fence
    pattern = r"\`\`\`\n(.*?)\n\`\`\`"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    # Return original if no fences found
    return text


def build_prompt(recommendation: dict, project_directory: Path,
                  memory_model: str = "hoare",
                  whyml_content: Optional[str] = None,
                  update_history: Optional[list] = None,
                  is_similar: bool = False) -> str:
    """Build the prompt for agent-script-update based on the recommendation."""
    target = recommendation.get("target", "unknown")
    rec_text = recommendation.get("recommendation", "")

    whyml_section = ""
    if whyml_content:
        whyml_section = f"""
## Generated WhyML Code
This is the WhyML intermediate representation that Why3 tried to verify and rejected.
Use it to understand exactly what the annotation compiled to and why the proof failed.

```whyml
{whyml_content}
```
"""

    _memory_model_hints = {
        "hoare": (
            "Standard value-semantic arrays (`array int`). No heap variable.\n"
            "Common annotation errors: unnecessary `\\valid`/`\\separated`, wrong `\\assigns` syntax.\n"
            "Common script errors: missing `use array.Array`, wrong array length call."
        ),
        "typed": (
            "Heap-based model. Arrays become `(arr: loc) (arr_len: int)` parameters.\n"
            "Heap variable: `int_mem : ref (map loc int)`. Preamble needs `use map.Map`.\n"
            "Common annotation errors: `\\valid(arr, n)` missing parens, `\\assigns arr[lo..hi]` wrong range operator (`..` not `:`), "
            "blank line between `#@ label L` and labeled statement, `\\at` label not in scope.\n"
            "Common script errors: Module6 missing Map preamble, `loc` vs `array int` mismatch, "
            "`arr_len` parameter not emitted, frame condition not wired after `ensures` clauses."
        ),
        "store": (
            "Identical to typed model but heap variable is named `store` (not `int_mem`).\n"
            "Same annotation/script errors as typed model — check `store` vs `int_mem` naming."
        ),
    }
    memory_model_section = (
        f"\n## Active Memory Model: `{memory_model}`\n"
        + _memory_model_hints.get(memory_model, _memory_model_hints["hoare"])
        + "\n"
    )

    history_section = ""
    if is_similar and update_history:
        attempts_text = "\n".join(
            f"  Attempt {i + 1}: files_changed={e.get('files_changed', [])}, "
            f"summary={e.get('summary', '(none)')}"
            for i, e in enumerate(update_history)
        )
        history_section = f"""
## ⚠ LOOP DETECTED — Previous Attempts Did Not Fix The Issue
The reconciliation agent has produced a recommendation similar to the previous one.
Your earlier update(s) did not resolve the problem. You MUST try a completely different
approach this time — do NOT repeat what was done before.

Previous update attempts for this file:
{attempts_text}
"""

    return f"""You are an expert Python developer tasked with applying a reconciliation recommendation to PyCSL scripts.
{memory_model_section}
## Recommendation Target
{target}

## Recommendation Text
{rec_text}
{whyml_section}{history_section}
## Allowed Update Targets
You may ONLY modify these two files:
- `src/pycsl/agents/agent-annotate.py` — the annotation agent logic
- `config/skills/pycsl-annotate/SKILL.md` — the annotator skill/prompt used by agent-annotate.py

**NEVER modify any file inside `tests/annotated/`.** Those files are auto-generated outputs and
must not be edited directly. All fixes must go into `agent-annotate.py` or the skill SKILL.md
so that future annotation runs produce correct results.

## Your Task
1. Use the MCP tools to read `src/pycsl/agents/agent-annotate.py` and/or `config/skills/pycsl-annotate/SKILL.md`
2. Apply the minimal change that addresses the recommendation
3. Preserve existing error handling, naming patterns, and code style
4. Only modify the files listed above

## MCP Tools Available
- list_update_targets(): List the allowed updateable files
- read_text_file(path): Read file contents
- read_json_file(path): Read JSON file
- write_text_file(path, content): Write file contents (allowed targets only)
- replace_text(path, old_text, new_text, count=1): Replace text in file (allowed targets only)

## Output
After applying the changes, provide a JSON summary with:
- "ok": true if successful
- "files_changed": list of files modified
- "summary": Brief description of changes made

Just output the JSON between ```json and ```.
"""


def run_agent(recommendation: dict, config: dict, project_directory: Path,
              whyml_content: Optional[str] = None,
              update_history: Optional[list] = None,
              is_similar: bool = False) -> Optional[dict]:
    """Run the agent-script-update LLM agent to apply recommendations."""
    model = config.get("model", "claude-sonnet-4.6")
    memory_model = config.get("memory-model", "hoare")
    prompt = build_prompt(recommendation, project_directory, memory_model, whyml_content, update_history, is_similar)

    log(project_directory, AGENT_NAME, f"[agent-script-update] Memory model: {memory_model}\n")
    log(project_directory, AGENT_NAME, f"[agent-script-update] Starting with target: {recommendation.get('target')}\n")

    try:
        response = llm_generate(
            prompt=prompt,
            system="",
            agent_id=AGENT_NAME,
            model=model
        )
        log(project_directory, AGENT_NAME, f"[agent-script-update] LLM Response:\n{response}\n")

        # Extract JSON from response
        json_text = extract_code_block(response, "json")
        result = json.loads(json_text)
        return result
    except json.JSONDecodeError as e:
        log(project_directory, AGENT_NAME, f"[agent-script-update] Failed to parse JSON response: {e}\n")
        return None
    except Exception as e:
        log(project_directory, AGENT_NAME, f"[agent-script-update] Error: {e}\n")
        return None


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Apply reconciliation recommendations to PyCSL scripts")
    parser.add_argument("--recommendation", required=True, help="Path to reconciliation JSON file")
    parser.add_argument("--config", required=True, help="Path to agents-config.json")
    parser.add_argument("--annotated-file", dest="annotated_file", default=None,
                        help="Path to the annotated .py file (used to locate the .mlw generated by pycsl)")
    parser.add_argument("--history-file", dest="history_file", default=None,
                        help="Path to a JSON file accumulating past update attempts for this file")
    parser.add_argument("--is-similar", dest="is_similar", action="store_true",
                        help="Set when the current recommendation is similar to the previous one")
    args = parser.parse_args()

    recommendation_path = Path(args.recommendation)
    config_path = Path(args.config)

    # Load config
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        return 1

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse config: {e}")
        return 1

    project_directory = Path(config.get("project-directory", "./my_project"))

    # Load recommendation
    if not recommendation_path.exists():
        log(project_directory, AGENT_NAME, f"ERROR: Recommendation file not found: {recommendation_path}\n")
        return 1

    try:
        with open(recommendation_path, 'r', encoding='utf-8') as f:
            recommendation = json.load(f)
    except json.JSONDecodeError as e:
        log(project_directory, AGENT_NAME, f"ERROR: Failed to parse recommendation: {e}\n")
        return 1

    log(project_directory, AGENT_NAME, f"[agent-script-update] Loaded recommendation: {recommendation}\n")

    # Load update history from file
    update_history: list = []
    history_path: Optional[Path] = Path(args.history_file) if args.history_file else None
    if history_path and history_path.exists():
        try:
            update_history = json.loads(history_path.read_text(encoding="utf-8"))
            log(project_directory, AGENT_NAME,
                f"[agent-script-update] Loaded {len(update_history)} prior attempt(s) from history\n")
        except Exception as e:
            log(project_directory, AGENT_NAME, f"[agent-script-update] Could not load history: {e}\n")

    # Load the WhyML file if available (produced by pycsl --keep-mlw)
    whyml_content: Optional[str] = None
    if args.annotated_file:
        mlw_path = Path(args.annotated_file).with_suffix(".mlw")
        if mlw_path.exists():
            whyml_content = mlw_path.read_text(encoding="utf-8")
            log(project_directory, AGENT_NAME, f"[agent-script-update] Loaded WhyML from {mlw_path}\n")
        else:
            log(project_directory, AGENT_NAME,
                f"[agent-script-update] WhyML file not found at {mlw_path}, continuing without it\n")

    agents_dir = config_path.parent
    mcp_script = agents_dir / "agent-script-update-mcp.py"
    log(project_directory, AGENT_NAME, f"[agent-script-update] Starting MCP server: {mcp_script}\n")
    if args.is_similar:
        log(project_directory, AGENT_NAME,
            f"[agent-script-update] Similar recommendation detected — agent will try a different approach\n")

    # Run the agent
    try:
        result = run_agent(recommendation, config, project_directory,
                           whyml_content=whyml_content,
                           update_history=update_history,
                           is_similar=args.is_similar)

        if result and result.get("ok"):
            log(project_directory, AGENT_NAME, f"[agent-script-update] Successfully applied changes\n")
            log(project_directory, AGENT_NAME, f"[agent-script-update] Files changed: {result.get('files_changed', [])}\n")
            log(project_directory, AGENT_NAME, f"[agent-script-update] Summary: {result.get('summary', '')}\n")

            # Persist this attempt to the history file
            if history_path is not None:
                entry = {
                    "attempt": len(update_history) + 1,
                    "recommendation_target": recommendation.get("target"),
                    "recommendation_text": recommendation.get("recommendation"),
                    "files_changed": result.get("files_changed", []),
                    "summary": result.get("summary", ""),
                }
                update_history.append(entry)
                try:
                    history_path.write_text(
                        json.dumps(update_history, indent=2, ensure_ascii=False),
                        encoding="utf-8"
                    )
                except Exception as e:
                    log(project_directory, AGENT_NAME, f"[agent-script-update] Could not write history: {e}\n")

            return 0
        else:
            log(project_directory, AGENT_NAME, f"[agent-script-update] Agent reported failure\n")
            return 1
    except Exception as e:
        log(project_directory, AGENT_NAME, f"[agent-script-update] Exception: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
