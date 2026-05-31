# SY8-SelfAnnotate — Reconciliator (Persona binding)

**Role:** Reconciliator
**Layer scope:** L2 → L5 for `src/self-annotate/`

## Binding

coordinator.py exit 72/73 + agent-meta-monitor.py + agent-meta-reviewer.py

## Responsibilities

- On test failure, diagnose the cause: Specifier fault, Verifier
  fault, or sub-actor (component/module/unit) fault.
- Route the fault to the responsible party. Does NOT repair.
- Track repeated escalations (per `coordinator.py`'s 3-strike
  loop-detection convention).
- For SY3-Pycsl + SY6-PycslLib: also detect L3-ceiling gaps in
  `agent-stdlib-annotate.py` output and trigger feature-plan
  proposal per `better-agent.md` Phase 2 (DEFERRED — pending
  `agent-feature-supervisor.py` implementation).
