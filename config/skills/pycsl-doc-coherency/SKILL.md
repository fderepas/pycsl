---
name: pycsl-doc-coherency
description: Documents the cross-surface coherency invariant for PyCSL `#@` directives — every directive defined in `test-suite/annotations.md` (the canonical source) must also be documented in `README.md`, `docs/pycsl-concrete-syntax-reference.md`, `docs/pycsl-static-semantics-reference.md`, `docs/pycsl-translational-reference.md`, and a relevant `config/skills/` skill. The discipline is enforced by `bin/doc-coherency.py --check`, wired into `bin/run-reference-tests.sh` as a leading CI gate. Use this skill whenever adding a new contract directive (`#@ no_exception`, `#@ allow_finalizer`, ...), reconciling drift detected by the check, or auditing documentation parity before a release.
---

# PyCSL Documentation Coherency

## Purpose and scope

This skill governs the invariant:

> *"For every `#@` directive defined in `test-suite/annotations.md`,
> the directive must also appear in `README.md`, the three
> `docs/pycsl-*reference*.md` files, and at least one
> `config/skills/` skill."*

The invariant is required because PyCSL's directive surface is
documented in five places that serve different audiences (quick
reference, normative grammar, static semantics, WhyML translation,
annotator workflow). Without enforcement, documentation drifts: a
directive added to `Module2_Parser.py` and explained in the skill
might never reach the reference docs, or vice versa. The skill is
the analogue of `pycsl-stdlib-coverage` and `pycsl-exception-model`
applied to the directive catalogue rather than the API surface or
exception model.

## Why a separate skill

The five surfaces are individually under CCB-style control (each
reference doc has a `Status: Normative` preamble; the skill set is
RAG-indexed). Documentation coherency between them is a *systems*
property, not a per-file property. Promoting it to its own skill
makes the invariant auditable and assigns it an owner.

---

## The five normative surfaces

| Surface | Role | Pattern that signals "directive is documented" |
|---|---|---|
| `README.md` | User-facing quick reference | Row in the contract-language table at §"PyCSL Contract Language (Quick Reference)" |
| `test-suite/annotations.md` | Canonical source of directive names | Row in §2.X table + detail subsection `#### §X.Y.Z` |
| `docs/pycsl-concrete-syntax-reference.md` | Grammar | Production in the EBNF block + table row in §2.X |
| `docs/pycsl-static-semantics-reference.md` | Well-formedness rules | Inference rule under `#### §X.Y.Z` |
| `docs/pycsl-translational-reference.md` | WhyML translation rule | Translation rule under `### §T.X.Y` (or explicit no-emission note) |

`config/skills/` is checked at coarser granularity — each directive
must appear in at least one skill, but not necessarily every skill.
The `bin/doc-coherency.py` tool does not enforce per-skill coverage;
that's an editorial concern.

### Two kinds of "source": canonical name vs source of truth

`annotations.md` is the **canonical source** for the directive *catalogue*
— the authoritative list of which `#@` directives exist and their names.
That is an *internal* source: it settles what to document, and this skill
enforces that the five surfaces agree with it.

It is **not** the source of truth for what a directive *means*. A
directive's semantics is faithful only if it reflects Python's external
**source of truth** — the [language reference](https://docs.python.org/3/reference/index.html)
and [CPython](https://github.com/python/cpython) (see `csl-philosophy`
"The source of truth"). Example: the `#@ no_exception KeyError` directive
is coherent across the five surfaces *and* faithful only because a missing
dict read genuinely raises `KeyError` in CPython.

Keep the two apart: **coherency is internal parity** (the five surfaces
match `annotations.md`); **fidelity is to the source of truth** (the
documented semantics match the language reference / reference
implementation). `bin/doc-coherency.py` checks the former. The latter is
the author's obligation, enforced by review and the reference corpus — a
directive can be perfectly coherent and still wrong if its documented
meaning diverges from the source of truth (*coherent and wrong*).

---

## The discovery tool — `bin/doc-coherency.py`

Three modes:

```bash
bin/doc-coherency.py --list-directives          # print canonical directive set
bin/doc-coherency.py --check                    # reconcile all directives
bin/doc-coherency.py --check <directive>        # check a single directive
```

The tool extracts directive names from `test-suite/annotations.md`
(the canonical source) and greps each of the five surfaces using a
two-tier pattern set:

1. **Strong signals**: `#@ <name>`, `<name>_decl` (EBNF production),
   `<Directive>Decl` (CSL AST node class), backtick phrase starting
   with the directive, TeX-formatted directive in a translation rule.
2. **Boundary form**: bare `<name>` word boundary — accepted only for
   directives in `_DISTINCTIVE` (multi-syllable or otherwise unlikely
   to collide with English prose).

Single-syllable directive names that overlap with English (``class``,
``label``, ``loop``, ``ghost``) require a strong-signal match and
will not be considered "documented" if they only appear as bare
prose words.

**Exit codes** (workplan §13 step 7 conventions):

| Code | Meaning |
|---|---|
| 0 | All directives present in every normative surface |
| 1 | At least one directive is missing from at least one surface |
| 2 | Tool error (canonical source missing or unparseable) |

## CI gate

`bin/run-reference-tests.sh` runs the check as a leading gate (after
the stdlib-coverage check, before any corpus test). A drift in
documentation parity fails fast — before any proof is even attempted.

Temporary skip:

```bash
PYCSL_SKIP_DOC_COHERENCY_CHECK=1 bash bin/run-reference-tests.sh
```

The skip env var is for local development workflow only — CI should
never set it.

---

## When to update the rule

The coherency invariant must hold for every PR that adds, removes,
or renames a `#@` directive. The five-surface checklist is captured
in `config/skills/pycsl-how-to-develop/SKILL.md` §9 step 9 ("Cross-
surface documentation coherency"). The annotator-workflow rules for
each directive live in `pycsl-annotate`; this skill is the *system-
level* invariant.

The tool itself evolves when:

- A new normative surface is added (e.g., a fourth `docs/` reference
  doc). Add a `(label, path)` entry to `TARGETS` in
  `bin/doc-coherency.py`.
- A new pattern shape emerges (e.g., a new EBNF naming convention).
  Extend `_patterns_for()` in the tool. Test against the existing
  directive set to avoid regressions.
- An entirely new directive shape that breaks the
  `#@ <name>` regex (currently none exists). Extend the
  `_DIRECTIVE_PAT` regex and the `_KNOWN_ALIASES` table.

The canonical source — `test-suite/annotations.md` — does NOT
require tool updates when new directives are added; the regex
discovers them. Coherency *failures* are addressed by updating the
target surfaces, not the tool.

---

## Out of scope

- **Semantic faithfulness.** The tool does not verify that the
  description in README matches the contract-rule in
  `static-semantics-reference.md`. Structural correspondence only.
  Semantic review is the human's job (or a future LLM-judge soft
  gate, modelled on the stdlib-coverage skill's §6).
- **Skill content quality.** The tool counts skills as "covering" a
  directive if the directive name appears anywhere in the skill
  body — even in a prose sentence. The skill's `description:`
  alignment and depth-of-coverage are editorial concerns.
- **`config/skills/` per-skill enforcement.** The tool does not
  check which skill should cover which directive — that mapping is
  encoded in the skills' `description:` frontmatter and surfaces via
  RAG, not via the doc-coherency check.

---

## Related skills and docs

- `config/skills/pycsl-how-to-develop/SKILL.md` §9 step 9 — the
  per-PR checklist step that triggers the audit.
- `config/skills/pycsl-stdlib-coverage/SKILL.md` — the parallel
  discipline for the stdlib API surface. Same shape: canonical
  source + tool + check + CI gate.
- `config/skills/pycsl-exception-model/SKILL.md` — the rulebook for
  `no_exception`'s trigger table; not directly involved in the
  directive-coherency check.
- `config/skills/pycsl-docs/SKILL.md` — the three-layer doc
  architecture this skill enforces parity across.
- `bin/doc-coherency.py` — the implementation.
- `bin/run-reference-tests.sh` — the CI gate wiring.
