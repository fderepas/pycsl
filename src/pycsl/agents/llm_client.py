"""
Ollama LLM Client Module
========================

This module provides a shared utility for interacting with local Large Language Models
via the Ollama API of via GitHub Copilot. It is designed to be used across multiple agents in the system.

Key Features:
-------------
- Native API integration with Ollama's `/api/generate` endpoint.
- Support for "Thinking Mode" (e.g., for models like gemma4:31b), which allows 
  the model to reason before providing an answer without timing out.
- Automatic JSON Extraction: Bypasses strict JSON grammar constraints (which break 
  thinking models) and instead parses structured JSON directly out of Markdown blocks.
- Observability: Includes ANSI-colored terminal outputs to track prompts and responses.

Usage Example:
--------------
    from llm_client import ollama_generate
    
    system_prompt = "You are a helpful assistant."
    user_prompt = "Output a JSON object with keys 'name' and 'age'."
    
    response = ollama_generate(user_prompt, system_prompt)
    
    if isinstance(response, dict):
        print(response['name'])

Environment:
    OLLAMA_URL        Ollama base URL (config key: llm-ollama-url)
    MODEL_NAME        Model tag (default: gemma4:31b)
    PROJECT_ROOT      Path to project workspace (default: ./project)
"""

import json
import urllib.request
import datetime
import re
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Union


def _load_ollama_url() -> str:
    """Read Ollama URL from env var, then agents-config.json. Raises if neither provides it."""
    env = os.environ.get("OLLAMA_URL")
    if env:
        return env
    config_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir, os.pardir,
        "config", "agents-config.json"
    ))
    try:
        with open(config_path) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        raise RuntimeError(
            f"agents-config.json not found at {config_path}. "
            "Set the OLLAMA_URL environment variable or add "
            '"llm-ollama-url" to config/agents-config.json.'
        )
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Failed to parse agents-config.json: {e}. "
            "Fix the JSON or set the OLLAMA_URL environment variable."
        )
    url = cfg.get("llm-ollama-url")
    if not url:
        raise RuntimeError(
            'Key "llm-ollama-url" is missing from config/agents-config.json. '
            "Add it or set the OLLAMA_URL environment variable."
        )
    return url


MODEL_NAME = os.environ.get("MODEL_NAME", "gemma4:31b")
OLLAMA_URL = _load_ollama_url()
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", "./project")).resolve()

def write_next_sequential_file(dirname: str, prefix: str, data: str) -> str:
    """Write data to a new sequentially-numbered file in dirname.

    Scans dirname for existing files matching '<prefix>_<N>' and creates
    '<prefix>_<N+1>' with the given data, starting at '<prefix>_0' if none exist.

    Args:
        dirname: Directory path where the file will be written.
        prefix:  Filename prefix (e.g. 'agent_req').
        data:    Text content to write.

    Returns:
        The full path of the newly created file.
    """
    # Ensure the target directory exists
    os.makedirs(dirname, exist_ok=True)
    
    max_n = -1
    prefix_underscore = f"{prefix}_"
    
    # Iterate through files in the directory to find the largest 'n'
    for filename in os.listdir(dirname):
        # Check if the file matches the expected pattern
        if filename.startswith(prefix_underscore):
            suffix = filename[len(prefix_underscore):]
            
            # Ensure the suffix is a valid integer
            if suffix.isdigit():
                max_n = max(max_n, int(suffix))
    
    # Calculate m (n + 1)
    m = max_n + 1
    
    # Construct the new file path
    new_filename = f"{prefix}_{m}"
    new_filepath = os.path.join(dirname, new_filename)
    
    # Write the data to the new file
    with open(new_filepath, 'w', encoding='utf-8') as f:
        f.write(data)
        
    return new_filepath

from common import log  # noqa: E402 — re-exported for backward compat

def ollama_generate(prompt: str, system: str, temperature: float, agent_id: str) -> str:
    """Send a prompt to the Ollama LLM and return the raw text response.

    Logs the request and response to sequentially-numbered files under
    PROJECT_ROOT/logs, and prints them to stdout with ANSI colours for
    easy visual monitoring.  Thinking mode is always enabled so that
    reasoning models (e.g. gemma4:31b) can deliberate before answering
    without hitting the request timeout.

    Args:
        prompt:      The user-facing prompt text.
        system:      The system prompt that sets the model's behaviour.
        temperature: Sampling temperature (higher = more creative).
        agent_id:    Identifier used as the log-file prefix
                     (e.g. 'planner', 'coder').

    Returns:
        The model's response as a plain string.  Callers that expect
        structured data should parse JSON out of the returned string
        themselves (see extract_json_from_response if available).
    """
    fmt_json=False
    # ANSI color codes
    LIGHT_GREY = "\033[90m"   # Bright black/grey
    LIGHT_GREEN = "\033[92m"  # Light green
    RESET = "\033[0m"
    # Display the prompt in light grey
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_next_sequential_file(PROJECT_ROOT / "logs", agent_id+"_req",
                               f"System: {system}\nPrompt: {prompt}\n")
    print(f"{LIGHT_GREY}--- Sending to LLM [{current_time}] ---", file=sys.stderr)
    print(f"System: {system}", file=sys.stderr)
    print(f"Prompt: {prompt}", file=sys.stderr)
    print(f"----------------------{RESET}", file=sys.stderr)

    body: dict[str, Any] = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "think": True,
        "options": {"temperature": temperature},
    }
    if fmt_json:
        body["format"] = "json"
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=2400) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    answer = data.get("response", "")

    # Display the answer in light green
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"{LIGHT_GREEN}--- LLM Response [{current_time}] ---", file=sys.stderr)
    print(f"{answer}", file=sys.stderr)
    print(f"--------------------{RESET}", file=sys.stderr)
    write_next_sequential_file(PROJECT_ROOT / "logs", agent_id+"_res",
                               answer)

    return answer


def githubcopilot_generate(prompt: str, system: str, agent_id: str, model: str) -> str:
    """Send a prompt to an LLM via the GitHub Copilot CLI and return the response.

    Combines system and user prompts into a single '--prompt' argument passed to
    the 'copilot' CLI tool.  stdout is captured as the answer; stderr is
    forwarded to the console so CLI warnings remain visible.

    Logs the request and response to sequentially-numbered files under
    PROJECT_ROOT/logs (same convention as ollama_generate), and prints them to
    stdout with ANSI colours for easy visual monitoring.

    Args:
        prompt:   The user-facing prompt text.
        system:   The system prompt that sets the model's behaviour.  It is
                  prepended to the user prompt separated by a newline.
        agent_id: Identifier used as the log-file prefix
                  (e.g. 'planner', 'coder').
        model:    Model name to pass to the Copilot CLI
                  (e.g. 'claude-opus-4.6').

    Returns:
        The model's response as a plain string.

    Raises:
        subprocess.CalledProcessError: If the 'copilot' CLI exits with a
            non-zero return code.
    """
    # ANSI color codes
    LIGHT_GREY = "\033[90m"
    LIGHT_GREEN = "\033[92m"
    RESET = "\033[0m"

    # Combine system and user prompts into one string for the CLI
    full_prompt = f"{system}\n{prompt}" if system else prompt

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_next_sequential_file(PROJECT_ROOT / "logs", agent_id + "_req",
                               f"System: {system}\nPrompt: {prompt}\n")
    print(f"{LIGHT_GREY}--- Sending to GitHub Copilot [{current_time}] ---", file=sys.stderr)
    print(f"System: {system}", file=sys.stderr)
    print(f"Prompt: {prompt}", file=sys.stderr)
    print(f"Model: {model}", file=sys.stderr)
    print(f"--------------------------------------------------{RESET}", file=sys.stderr)

    cmd = [
        "copilot",
        "--prompt", full_prompt,
        "--allow-tool", "write",
        "--model", model,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    answer = result.stdout

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{LIGHT_GREEN}--- GitHub Copilot Response [{current_time}] ---", file=sys.stderr)
    print(f"{answer}", file=sys.stderr)
    print(f"-----------------------------------------------{RESET}", file=sys.stderr)
    write_next_sequential_file(PROJECT_ROOT / "logs", agent_id + "_res",
                               answer)

    return answer


def llm_generate(prompt: str, system: str, agent_id: str, model: str) -> str:
    """Dispatch a prompt to the appropriate LLM backend based on the model name.

    Open-weight models are served locally via Ollama; proprietary models are
    reached through the GitHub Copilot CLI.  If the model name is not found in
    either list, a ValueError is raised so callers get an explicit error rather
    than a silent no-op.

    Args:
        prompt:   The user-facing prompt text.
        system:   The system prompt that sets the model's behaviour.
        agent_id: Identifier used as the log-file prefix (e.g. 'planner').
        model:    Model name, e.g. 'gemma4:31b' or 'claude-opus-4.6'.

    Returns:
        The model's response as a plain string.

    Raises:
        ValueError: If model is not present in either known model list.
    """
    open_weight_model_list = ["gemma4:31b", "qwen3.6:35b"]
    proprietary_model_list = ["claude-opus-4.6", "claude-sonnet-4.6"]

    if model in open_weight_model_list:
        return ollama_generate(prompt, system, temperature=0.7, agent_id=agent_id)
    elif model in proprietary_model_list:
        return githubcopilot_generate(prompt, system, agent_id, model)
    else:
        raise ValueError(
            f"Unknown model '{model}'. "
            f"Add it to open_weight_model_list or proprietary_model_list in llm_generate()."
        )
