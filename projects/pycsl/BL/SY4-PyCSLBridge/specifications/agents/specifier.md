# SY4-PyCSLBridge — Specifier (Persona binding)

**Role:** Specifier (per `cmmi-agent-roles` Abstract Role Aliases)
**Layer scope:** L2 → L5 for `src/pycsl_bridge/`

## Binding

developer

## Responsibilities

- Define what `src/pycsl_bridge/` produces at each in-scope level.
- Maintain coherence between this System's spec and the BL
  `BL/specifications/main.md` (which includes `csl-from-scratch`).
- For SY3-Pycsl and SY6-PycslLib (S1 owners): writes `#@` contracts
  on functions in `src/pycsl_bridge/`. These contracts ARE the L5 specs.

## Constraint

Specifier MUST be a different agent/persona from the Verifier and
Reconciliator (independence constraint from `project-lifecycle`).
Under Profile-P single-developer, the developer plays all three
roles serially but the role hat-switching is recorded in commits
(commit message tag: `role: specifier|verifier|reconciliator`).
