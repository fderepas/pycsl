# proposed-features/

Staging area for **auto-generated feature plan drafts** awaiting
human approval. Produced by `agent-stdlib-annotate.py
--propose-feature` (per `better-agent.md` Phase 2 — currently
DEFERRED, pending implementation).

## Workflow

1. Agent detects ≥5 stuck functions in the same gap category (e.g.
   `iterator-semantics`).
2. Agent generates a draft `missing-<category>-feature.md` here,
   marked `STATUS: DRAFT`.
3. **Human reviews and edits** the draft.
4. To approve: move the draft to the repo root (sibling of
   `missing-iter-feature.md`) and flip `STATUS: DRAFT` →
   `STATUS: APPROVED`.
5. `agent-feature-supervisor.py` watches for the
   DRAFT → APPROVED transition and begins the supervised rollout
   (per `better-agent.md` Phase 3).

The first canonical example — `missing-iter-feature.md` — was
human-authored, not generated. It is the structural template every
auto-generated draft should resemble.
