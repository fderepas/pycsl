# Undefined-behaviour patterns (hard-reject)

Load when PyCSL rejects code with a `PyCSLSemanticError` citing
one of the UB-7.X categories, or when deciding whether to apply
an escape annotation.

> **Rulebook:** `config/skills/pycsl-ub-catalog/SKILL.md` is the
> normative reference for the five UB categories — detection
> mechanism, verification stance, error messages, corpus tests.
> Consult it before adding any escape annotation. This file is the
> annotator-workflow summary only.

Five Python patterns are hard-rejected before the proof obligation
is even generated. Authoring annotated code that trips one of these
checks produces a `PyCSLSemanticError`, not a proof failure — the
diagnosis points to a *structural* problem to rewrite or explicitly
bless.

| UB | Trigger | Escape annotation |
|---|---|---|
| 7.1 | Mutation of the iterated container inside `for x in C:` | `#@ allow_iteration_mutation` (per loop) |
| 7.2 | Class with both `__hash__` and `__eq__` | none — axiom mode by default; strict mode requires `#@ proof <prover>` |
| 7.3 | Shared-variable access outside `#@ critical` (concurrent model) | none — strict mode is opt-in (`--strict-concurrent-checks`) |
| 7.4 | `import ctypes` / `cffi` / `numpy.ctypeslib` / `cython` | `#@ \trusted` on at least one function in the file |
| 7.5 | Class with `__del__` | `#@ allow_finalizer` (per class) |

**Default for the annotator:** rewrite, don't bless. The reject
exists because the construct cannot be soundly modelled — the
escape annotation documents the assumption but does not make the
proof more meaningful. Reach for the catalog rulebook when you need
to decide between rewrite and bless.
