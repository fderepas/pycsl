---
name: agent-project-structure
description: Provides the recommended harness-agnostic directory layout for a Python agent project that contains multiple agents, reusable skills, reference examples, test suites, local embeddings storage, and configuration files. Covers where RAG indexes derived from skills and other corpora should live, and the source-vs-derived split that keeps skills portable. Use this skill whenever the user is scaffolding a new agent project, restructuring an existing one, asking where to put agents, skills, tests, embeddings, vector indexes, or config, asking where a RAG version of a skill belongs, or wants a portable layout that works across any LLM runtime or agent harness.
---

# Agent Project Structure

A portable directory convention for Python agent projects. It is deliberately
independent of any specific LLM provider, agent runtime, or harness: the same
tree works whether the project is driven by an in-house orchestrator, an
open-source framework, or a vendor SDK. The only contract is that "skills"
follow the cross-vendor `SKILL.md` convention (a folder containing a `SKILL.md`
file with YAML frontmatter plus optional `scripts/`, `references/`, and
`assets/` subfolders).

## When to use this skill

Apply this layout when any of the following is true:

- A new Python project will host one or more agents.
- An existing project mixes agent logic, prompts, vector data, and tests in
  ad-hoc locations and needs to be reorganized.
- The project must remain portable across runtimes (no hard dependency on a
  single harness's auto-discovery directory).
- Multiple agents share a common pool of skills, tools, and embeddings.
- You need to decide where embeddings, vector indexes, or "RAG versions" of
  skills should live relative to the skills themselves.

## Recommended tree

```text
my_project/
├── config/                        ← all project + agent configuration
│   ├── settings.json              ← project-level agent settings
│   ├── default.yaml               ← model, budgets, allowed tools
│   ├── dev.yaml / prod.yaml       ← environment overlays
│   ├── mcp_servers.json           ← external tool / MCP connector definitions
│   ├── agents/                    ← agent persona definitions (markdown)
│   │   ├── researcher.md          ← Agent 1 persona (retrieval + analysis)
│   │   └── writer.md              ← Agent 2 persona (drafting + editing)
│   ├── commands/                  ← reusable command definitions
│   ├── hooks/                     ← pre/post-tool hook scripts
│   └── skills/                    ← skills available to agents (source only)
│       ├── pdf-processing/
│       │   ├── SKILL.md           ← required: YAML frontmatter + instructions
│       │   ├── scripts/           ← executable helpers (.py / .sh)
│       │   ├── references/        ← reference docs, loaded on demand
│       │   └── assets/            ← templates, schemas, fonts
│       └── data-extraction/
│           └── SKILL.md
│
├── src/
│   └── my_project/                ← Python source code (importable package)
│       ├── __init__.py
│       ├── main.py                ← entry point, orchestrates the agents
│       ├── agents/                ← two example agents
│       │   ├── __init__.py
│       │   ├── researcher.py      ← Agent 1: RAG over data/embeddings/
│       │   └── writer.py          ← Agent 2: drafts from researcher's notes
│       ├── indexing/              ← ingestion scripts (chunk, embed, write)
│       │   ├── index_skills.py    ← walks config/skills/ → data/embeddings/skills_index/
│       │   └── index_corpus.py    ← walks data/corpus/   → data/embeddings/corpus_index/
│       ├── tools/                 ← custom tool functions, connector wrappers
│       └── prompts/               ← system-prompt fragments
│
├── tests/                         ← test suites
│   ├── unit/
│   │   ├── test_researcher.py
│   │   └── test_writer.py
│   ├── integration/               ← end-to-end multi-agent runs
│   └── evals/                     ← agent and skill evaluations
│
├── examples/                      ← runnable reference examples
│   ├── run_researcher.py          ← runs the Researcher agent alone
│   ├── run_writer.py              ← runs the Writer agent alone
│   └── researcher_to_writer.py    ← chains both agents in a pipeline
│
├── data/                          ← local storage (gitignored)
│   ├── corpus/                    ← raw source documents (PDFs, markdown, ...)
│   ├── embeddings/                ← derived vector indexes (regenerable)
│   │   ├── skills_index/          ← chunks + vectors built from config/skills/
│   │   │   ├── chroma.sqlite3
│   │   │   └── manifest.json      ← source files, embedding model, build time
│   │   └── corpus_index/          ← chunks + vectors built from data/corpus/
│   │       ├── chroma.sqlite3
│   │       └── manifest.json
│   ├── memory/                    ← persisted agent state and logs
│   └── cache/
│
├── AGENTS.md                      ← project-wide instructions for any agent
├── pyproject.toml                 ← Python package + dependency manifest
├── .env.example                   ← secrets template (real .env is gitignored)
└── README.md
```

## Rationale per directory

### `config/`

Holds everything that configures the project at runtime: model settings,
environment overlays, external tool definitions, agent personas, hooks, and
the skill library. Keeping all of these under one root means a harness only
needs to be pointed at a single directory to discover the project's
agents and capabilities. Each subfolder has a single responsibility:

- `agents/` — one markdown file per persona. Personas are declarative
  (instructions, allowed tools, model preference) so they can be loaded by
  any runtime that understands plain markdown plus frontmatter.
- `skills/` — one folder per skill, following the `SKILL.md` convention.
  This is the only piece of the layout with a cross-vendor standard, so it
  should be respected even when the rest of the harness is custom.
  **Skills here are source-only — never store pre-built embeddings, vector
  indexes, or other derived artifacts inside a skill folder.** See
  "Skills as RAG sources" below for the full rationale.
- `hooks/`, `commands/` — optional, but reserved here so projects do not
  reinvent these locations later.

### `src/my_project/`

Standard Python `src/` layout. The package name (`my_project`) matches the
distribution name in `pyproject.toml` so the project is importable and
installable like any other Python library. Two example agents live under
`agents/`:

- `researcher.py` — loads its persona from `config/agents/researcher.md`,
  queries `data/embeddings/`, and invokes the `pdf-processing` and
  `data-extraction` skills as needed.
- `writer.py` — loads its persona from `config/agents/writer.md` and
  consumes the researcher's structured output to produce the final artifact.

Custom tools live in `src/my_project/tools/`. Prompt fragments live in
`src/my_project/prompts/` so they can be unit-tested and version-controlled
alongside the code that uses them. Ingestion scripts that build vector
indexes live in `src/my_project/indexing/` — they are application code, not
skill content.

### `tests/`

Three tiers, mirroring industry norms:

- `unit/` — fast, deterministic tests of individual functions and tools.
- `integration/` — full agent runs against fixtures or recorded traces.
- `evals/` — quality measurements (accuracy, groundedness, refusal rates)
  run on a representative dataset. Separated from `integration/` because
  evals are typically slower, non-deterministic, and graded.

### `examples/`

Runnable scripts intended for *consumers* of the project: the shortest path
from a fresh clone to a working agent invocation. The two single-agent
examples (`run_researcher.py`, `run_writer.py`) demonstrate each agent in
isolation; `researcher_to_writer.py` shows the canonical hand-off pattern
between them.

Do not confuse `examples/` with the per-skill `references/` folders. The
former is example code for humans; the latter is reference material that an
agent reads on demand when a skill is invoked.

### `data/`

Local, gitignored storage with a strict **source-vs-derived split**:

- `corpus/` — **source** documents the project indexes for retrieval (PDFs,
  markdown, scraped pages, exported tickets). Treat as read-mostly; the
  ingestion pipeline reads from here.
- `embeddings/` — **derived** vector indexes built from `corpus/` and from
  `config/skills/`. Every subdirectory should be reproducible from source
  by re-running the ingestion script. The convention is one subfolder per
  logical index (`skills_index/`, `corpus_index/`, etc.), each containing
  the vector-store files plus a `manifest.json` recording which source
  files were indexed, which embedding model produced the vectors, and when.
- `memory/` — persisted conversation state, agent scratchpads, run logs.
- `cache/` — anything that can be regenerated (HTTP caches, intermediate
  artifacts).

The source-vs-derived split matters because vector indexes go stale when
either the source changes or the embedding model changes. Keeping derived
artifacts under `embeddings/` (never mixed into `corpus/` or
`config/skills/`) makes it safe to delete and rebuild any index without
risking source loss.

Ingestion scripts that populate `data/embeddings/` belong in
`src/my_project/indexing/` — never inside `data/` itself.

### Root files

- `AGENTS.md` — project-wide instructions loaded by any compliant agent
  harness at session start. Acts as the shared "team handbook" so every
  agent inherits the same conventions regardless of persona.
- `pyproject.toml` — single source of truth for the Python package,
  dependencies, and tool configuration.
- `.env.example` — documents required secrets without committing them.

## Skills as RAG sources

The single most common question this layout answers: **where does the "RAG
version" of a skill go?** Short answer: not inside the skill folder. Skills
under `config/skills/` are source content; their RAG-derived form
(chunks + embeddings + index files) lives under `data/embeddings/skills_index/`
and is rebuilt from source whenever needed.

This separation is not arbitrary. There is currently **no official
specification covering pre-built embeddings inside a skill folder** — the
cross-vendor `SKILL.md` standard defines only `SKILL.md`, `scripts/`,
`references/`, and `assets/`. The emerging convention across multiple
agent runtimes (package managers, workspace tools, skill-aware indexers)
is to treat skills as the *input* to a RAG pipeline, not as the carrier
of a pre-built index. Four reasons this separation is the right call:

- **Model-coupling.** An embedding is tied to a specific model and
  dimension. Bundling a 3072-dim index inside a skill makes that skill
  useless to anyone running a different embedding model. Skills are
  meant to be portable; embeddings break portability.
- **Staleness.** Editing a single line in `SKILL.md` invalidates every
  chunk that overlaps that line. A bundled index goes stale on every
  commit and there is no harness convention for triggering rebuilds.
- **Size.** A 1,500-line skill produces a 10–50 MB index depending on
  chunk size and model dimension. Source repositories tracking skills
  do not want that weight, and skills are positioned as small,
  human-editable artifacts.
- **Use-case diversity.** The same skill source might be chunked
  differently for different RAG purposes — small chunks for precise
  retrieval, larger chunks for synthesis, contextual-retrieval chunks
  with summaries prepended. Bundling one chunking forecloses the others.

### How the pieces connect

The data flow is one-directional and reproducible:

```text
config/skills/**/SKILL.md          ─┐
config/skills/**/references/*.md   ─┼──→ src/my_project/indexing/index_skills.py
                                    │           │
                                    │           ▼
                                    │    data/embeddings/skills_index/
                                    │      ├── chroma.sqlite3   (vectors)
                                    │      └── manifest.json    (provenance)
                                    │
data/corpus/**                     ─┼──→ src/my_project/indexing/index_corpus.py
                                    │           │
                                    │           ▼
                                    │    data/embeddings/corpus_index/
```

At query time, agents in `src/my_project/agents/` open the appropriate
index under `data/embeddings/` and retrieve top-k chunks. They never read
source files under `config/skills/` for retrieval — only the ingestion
pipeline does.

### The `manifest.json` contract

Every index subdirectory under `data/embeddings/` should contain a
`manifest.json` recording, at minimum:

- The list of source files indexed (paths + content hashes).
- The embedding model name and dimension.
- The chunking parameters (size, overlap, strategy).
- The build timestamp.

On rebuild, the ingestion script compares current source hashes against
the manifest and re-embeds only what changed. The manifest is also what
makes an index *portable across machines* — a teammate can verify their
local index matches yours, or trigger a clean rebuild if not.

### When you must bundle an index with a skill

The only legitimate case for bundling derived artifacts with a skill is
**distribution of a single skill plus its index as a self-contained
package** (e.g., shipping to teammates without access to the build
pipeline). Even then, treat the bundled index as a cache the runtime may
or may not use, place it in a clearly-named `index/` subfolder, and tag
the subfolder with the embedding model:

```text
pycsl-annotate/
├── SKILL.md
├── references/
└── index/                              ← optional, cache-style
    └── voyage-3-1024d.chroma/
```

No current harness scans for this convention — you need explicit code in
your loader to find and use it. The cleaner architecture is to keep all
indexes in `data/embeddings/` and let the project's ingestion pipeline
build them on first run.

## Two-agent example, end-to-end

The skeleton ships with two cooperating agents to make the layout concrete:

1. **Researcher** (`src/my_project/agents/researcher.py`)
   - Persona: `config/agents/researcher.md`
   - Reads from: `data/embeddings/skills_index/` and `data/embeddings/corpus_index/`
   - Skills used: `pdf-processing`, `data-extraction`
   - Output: a structured notes object handed to the Writer.

2. **Writer** (`src/my_project/agents/writer.py`)
   - Persona: `config/agents/writer.md`
   - Reads from: the Researcher's output
   - Output: the final document, dropped into `data/` or returned to the caller.

`main.py` wires the two together for production use; the three scripts
under `examples/` demonstrate the pieces in isolation and as a pipeline.
Before either agent can run, `src/my_project/indexing/index_skills.py` and
`index_corpus.py` must be invoked at least once to populate
`data/embeddings/` — typically wired as a `make index` target or as a
first-run check in `main.py`.

## Portability notes

This layout deliberately avoids two common harness-specific traps:

1. **No reserved dotfile directories.** Some runtimes auto-scan a fixed
   directory (for example a hidden folder at the project root) to discover
   skills and personas. Putting everything under `config/` instead keeps
   the project legible and means migrating between harnesses is a matter
   of pointing the new runtime at `config/` — not renaming directories.

2. **`SKILL.md` is the only cross-vendor contract.** As long as each skill
   folder contains a `SKILL.md` with valid YAML frontmatter (`name` and
   `description` at minimum), the skill is portable. Keep skill bodies
   harness-agnostic: avoid runtime-specific tool names in the instructions,
   prefer describing capabilities ("read the PDF", "query the vector
   store") over naming concrete APIs.

If a specific harness requires its own discovery directory, prefer a
symbolic link from the harness-expected location to `config/` rather than
moving the canonical files. The project's source of truth stays in one
place.

## Anti-patterns to avoid

- Putting prompts and personas inside `src/` as Python string literals.
  They belong in markdown so non-engineers can edit them and so they are
  diffable.
- Storing embeddings under `src/` or inside a package. Binary vector
  files do not belong in importable code.
- **Bundling embeddings inside `config/skills/<skill>/`.** Derived
  artifacts mix with source, the skill becomes coupled to one embedding
  model, and rebuilds are blocked by the source-vs-derived confusion.
  Indexes belong in `data/embeddings/`.
- **Indexing skills and corpus into the same vector collection.** Use
  separate subfolders (`skills_index/`, `corpus_index/`) so each can be
  rebuilt, versioned, and queried independently. Mixed collections make
  it impossible to tell whether a retrieved chunk came from an
  authoritative skill rule or from a domain document.
- **Omitting `manifest.json` from a derived index.** Without provenance,
  there is no way to detect staleness, no way to know which embedding
  model the vectors came from, and no way to safely share the index
  across machines.
- Mixing skill scripts with application code. Scripts an agent shells
  out to from a skill live inside that skill's `scripts/` folder;
  scripts the application imports live in `src/my_project/`.
- A single `tests/` folder with no separation between unit, integration,
  and eval tests. The three have different runtimes, different failure
  semantics, and different CI cadences.
- Committing `.env` or any contents of `data/`. Only `.env.example` and
  optional seed files belong in version control.
