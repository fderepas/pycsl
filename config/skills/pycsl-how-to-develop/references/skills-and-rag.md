# Skills + RAG system

Load when modifying skill files, debugging agent retrieval, or
rebuilding the RAG index.

## Skill Files

Each skill lives in `config/skills/<name>/SKILL.md` with YAML frontmatter:

```yaml
---
name: pycsl-annotate
description: Master annotation skill for the PyCSL agent pipeline...
---
```

The body contains rules, examples, and NEVER constraints that the LLM agents follow.

## Terminology Glossary

Human-facing verification vocabulary lives in `docs/glossary/`.

Use the glossary to normalize recurring terms across docs and skills:

- prefer one primary term per concept
- record aliases in the glossary page rather than scattering competing names
- examples:
    - **witness** as the primary term, with *proof certificate* and *local
        certificate* as aliases
    - **ghost code** / **ghost state** / **ghost lowering** as distinct concepts
    - **local reasoning** and **global reasoning** as the preferred contrast when
        discussing solver behavior

## RAG Compilation

Skills are compiled into a vector index by `src/skill2rag/`:

```bash
./bin/update-rag.sh
# or equivalently:
python src/skill2rag build --skill-dir config/skills
```

This produces `data/embeddings/skills_index.json` (chunked text + 768-dimensional vectors via Ollama). Agents query this index at runtime to retrieve relevant skill fragments.

**CRITICAL: Run `./bin/update-rag.sh` after ANY change to a skill file.**

## Skill Inventory

| Skill | Used By | Purpose |
|-------|---------|---------|
| `pycsl-annotate` | agent-annotate.py | Master annotation rules, NEVER constraints |
| `contract-writer` | agent-contract-writer.py | Requires/ensures/assigns generation |
| `english-writer` | agent-english-writer.py | English spec generation |
| `invariant-writer` | agent-invariant-writer.py | Loop invariant/variant generation |
| `polish-skill` | agent-annotate.py | Post-processing polish rules |
| `agent-project-structure` | project scaffolding | Directory layout conventions |
| `pycsl-how-to-develop` | developer reference | This skill |
