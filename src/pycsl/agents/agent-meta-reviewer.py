#!/usr/bin/env python3
"""
Agent Meta Reviewer — human interface and trend analyzer for the self-healing pipeline.

Reads metrics produced by agent-meta-monitor and agent-meta-evaluator, calls an LLM
to synthesize a PR description and a macro-level system recommendation, then writes
the structured JSON and a Markdown file for human or CI/CD consumption.
"""

import argparse
import json
import re
import sys
from pathlib import Path

AGENT_NAME = "agent-meta-reviewer"

from llm_client import llm_generate, log as _llm_log  # noqa: E402


def log(msg: str, out_dir: Path) -> None:
    _llm_log(out_dir, AGENT_NAME, f"[{AGENT_NAME}] {msg}\n")


def load_json(path: Path, out_dir: Path) -> dict:
    if not path or not path.exists():
        log(f"Warning: {path} not found — using empty placeholder", out_dir)
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"Warning: could not parse {path}: {e}", out_dir)
        return {}


def extract_json_from_response(text: str) -> dict:
    m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    # Fallback: try parsing the whole response as JSON
    return json.loads(text.strip())


def build_prompt(monitor: dict, eval_data: dict, reconcile: dict) -> str:
    return f"""You are a Staff Software Engineer reviewing an automated self-healing pipeline run.

## Operational Health Metrics (from agent-meta-monitor)
{json.dumps(monitor, indent=2)}

## Fix Efficacy Evaluation (from agent-meta-evaluator)
{json.dumps(eval_data, indent=2)}

## Original Reconciliation Recommendation (from agent-reconcile)
{json.dumps(reconcile, indent=2)}

Based on the data above, produce a structured review with these JSON fields:

- "pr_title": A concise PR title summarising the automated fix
- "pr_body": A Markdown PR body covering: the problem, the fix applied, blast radius, and test results
- "system_recommendation": Macro-level advice on whether the base prompts or system config need adjusting,
  based on the health metrics and test outcomes
- "requires_human_intervention": true if resolution_status is "Regression" OR health_status is "warning",
  false otherwise

Just output the JSON between ```json and ```.
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Human interface and trend analyzer for the self-healing pipeline"
    )
    parser.add_argument(
        "--monitor-json",
        dest="monitor_json",
        required=True,
        help="Path to JSON produced by agent-meta-monitor.py",
    )
    parser.add_argument(
        "--eval-json",
        dest="eval_json",
        required=True,
        help="Path to JSON produced by agent-meta-evaluator.py",
    )
    parser.add_argument(
        "--reconcile-json",
        dest="reconcile_json",
        required=True,
        help="Path to recommendation JSON produced by agent-reconcile.py",
    )
    parser.add_argument(
        "--out-json",
        dest="out_json",
        required=True,
        help="Output path for the structured review JSON",
    )
    parser.add_argument(
        "--out-md",
        dest="out_md",
        required=True,
        help="Output path for the Markdown PR body",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to agents-config.json (used for model selection)",
    )
    args = parser.parse_args()

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_dir = out_json.parent

    config_path = Path(args.config)
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"ERROR: Could not load config: {e}", out_dir)
        return 1

    model = config.get("model", "claude-sonnet-4.6")

    monitor = load_json(Path(args.monitor_json) if args.monitor_json else None, out_dir)
    eval_data = load_json(Path(args.eval_json) if args.eval_json else None, out_dir)
    reconcile = load_json(Path(args.reconcile_json) if args.reconcile_json else None, out_dir)

    prompt = build_prompt(monitor, eval_data, reconcile)
    log("Calling LLM for review...", out_dir)

    try:
        response = llm_generate(prompt=prompt, system="", agent_id=AGENT_NAME, model=model)
        log(f"LLM response received ({len(response)} chars)", out_dir)
        result = extract_json_from_response(response)
    except (json.JSONDecodeError, Exception) as e:
        log(f"ERROR parsing LLM response: {e}", out_dir)
        result = {
            "pr_title": "Automated pipeline review (parse error)",
            "pr_body": f"Could not parse LLM response: {e}",
            "system_recommendation": "Manual review required",
            "requires_human_intervention": True,
        }

    required_keys = {"pr_title", "pr_body", "system_recommendation", "requires_human_intervention"}
    missing = required_keys - set(result.keys())
    if missing:
        log(f"WARNING: LLM response missing keys: {missing}", out_dir)

    try:
        from schema_validator import validate_or_warn
        validate_or_warn(result, "reviewer",
                         logger=lambda msg: log(msg, out_dir))
    except ImportError:
        pass
    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    out_md.write_text(result.get("pr_body", ""), encoding="utf-8")
    log(f"Wrote review to {out_json} and {out_md}", out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
