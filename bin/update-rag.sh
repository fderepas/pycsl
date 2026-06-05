#!/bin/bash
# update-rag.sh — Rebuild the RAG index from all skills in config/skills/.
#
# Usage:
#   ./bin/update-rag.sh
#
# Must be run after any change to a SKILL.md file under config/skills/.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
fi

echo "Rebuilding RAG index from config/skills/ ..."
# `-u` (unbuffered stdout) so the indexer's per-batch progress streams live —
# without it Python block-buffers when stdout is piped/redirected, hiding
# progress until the run ends (a slow Ollama embed then looks like a hang).
# Do NOT pipe this through `tail`/`head` for the same reason.
PYTHONPATH=src python -u -m skill2rag build --skill-dir config/skills
echo "RAG index rebuilt → data/embeddings/skills_index.json"
