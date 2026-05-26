---
name: pycsl-docs
description: Explains the CMMI-style conventions used to structure docs/*reference.md files — the three-layer architecture (syntax → static semantics → translation), normative document patterns (Status, Version, Source of truth, Scope, Companion documents, section/§ cross-referencing, Gap Analysis), and how to create or extend a reference document. Use this skill when answering questions about PyCSL contract validity that require navigating between the three reference documents, when deciding which reference doc to consult for a specific error or contract question, or when creating or extending a reference document in the docs/ directory.
---

# PyCSL Documentation Architecture

## The Three-Layer Stack

The three `docs/*reference.md` files form an ordered stack. Each layer answers a
strictly stronger question than the one below it:

| Layer | Document | Question answered |
|-------|----------|-------------------|
| 1 | `pycsl-concrete-syntax-reference.md` | Is this string a syntactically valid PyCSL annotation? (grammar productions) |
| 2 | `pycsl-static-semantics-reference.md` | Is this annotation well-formed in context Γ? (scope, type, placement rules) |
| 3 | `pycsl-translational-reference.md` | Does this annotation generate valid WhyML? (T : AnnotatedPython → WhyML) |

**A contract that passes Layer 1 may fail Layer 2.**
**A contract that passes Layer 2 may fail Layer 3.**

This strict ordering is the key architectural property. When validating a contract:
- Start at Layer 1 (syntax) and work upward.
- A Layer 3 failure is the most dangerous: `pycsl --no-proof` reports success but
  Why3 rejects the generated `.mlw`. The canonical example: `"key" in d` where `d`
  is unannotated — passes Layers 1 and 2, fails Layer 3 (G6, §T.11.1).

---

## Document Conventions (Normative Preamble Pattern)

Every `docs/*reference.md` opens with this structured preamble:

```markdown
**Status:** Normative
**Version:** N.M
**Source of truth:** <implementation file(s)>, cross-referenced against
  test-suite/annotations.md (paragraph numbering preserved).
**Scope:** What this document covers. It does NOT cover <sibling concerns>
  (see <sibling doc>).
**Companion documents:** (optional) explicit cross-references.
```

**Rules for each field:**

- **Status: Normative** — the document is authoritative. When code and doc
  disagree, the doc defines the intended behaviour and the code has a bug.
  Never write "Status: Informative" for a reference doc.

- **Source of truth** — must name specific implementation files (e.g.,
  `Module2_Parser.py`) and the `test-suite/annotations.md` paragraph range
  from which the document was derived. This makes the doc auditable.

- **Scope / does NOT cover** — the "does NOT cover" sentence is required.
  It must point explicitly to the sibling doc that covers the excluded topic.
  This prevents scope creep across sessions and makes cross-referencing
  deterministic. Example from the concrete syntax reference:
  > "It does NOT define what the annotations mean (see
  > `pycsl-static-semantics-reference.md` for well-formedness rules...)."

- **Companion documents** — list sibling docs with one-line descriptions.
  Update these when adding a new reference document.

---

## Section Numbering and Cross-Referencing Conventions

Each document uses a distinct section prefix so cross-document citations are
unambiguous even when section numbers collide:

| Document | Prefix | Examples |
|----------|--------|---------|
| Concrete syntax reference | decimal (no prefix) | §1.2, §3.1.8 |
| Static semantics reference | decimal + `§` for subsections; `E` for error codes | §2.3.1, §6.1, E1, E2 |
| Translational reference | `§T` prefix | §T.2.2, §T.6.1, §T.9.1, §T.11.1 |

**Cross-document citation form:**
- Within a document: `(§3.1.8)` — section number alone is sufficient.
- Across documents: `(§T.2.2 of translational reference)` or `(E2, static
  semantics reference §9)`.

**Gap codes** (`G1`, `G6`, …) are defined in the translational reference §T.11
and referenced by both the static semantics reference and the global plan.

**Error codes** (`E1`–`E5`) are defined in the static semantics reference §9
(Error Catalogue) and used in the global plan appendix.

---

## Navigating to the Right Document

| Question | Layer | Document and section |
|----------|-------|----------------------|
| Is `\forall i;` the right separator? | 1 | Concrete syntax reference §2 |
| Can I use `\result` in `requires`? | 2 | Static semantics reference §3.1.5 (E1) |
| Why does `"key" in d` fail Why3? | 3 | Translational reference §T.11.1 (G6) + §T.2.2 |
| What does `assigns` generate in Hoare model? | 3 | Translational reference §T.9.1 |
| What does a string literal map to in WhyML? | 3 | Translational reference §T.6.1 |
| Why is `self.field` safe in a class invariant? | 2 | Static semantics reference §2.3.1 + §6.1 |
| Which params become `int` vs `array int`? | 3 | Translational reference §T.2.2 |
| What does `\result` become in WhyML? | 3 | Translational reference §T.6.5 |
| What does `\trusted` emit? | 3 | Translational reference §T.10 |
| What is the error code for an unbound variable? | 2 | Static semantics reference §9 (E2) |
| What does `\map_set(d, k, v)` emit in WhyML? | 3 | Translational reference §T.8.5 |
| Is `\map_remove(d, k)` a valid atom? | 1 | Concrete syntax reference §3.1.24 |
| What is the WhyML type of a ghost dict? | 2 | Static semantics reference §2.4.2b (type mapping τ_ghost) |

---

## How to Create a New Reference Document

Follow this checklist to ensure the new document integrates correctly with
the existing stack:

1. **Define the layer position.** Which question does this document answer?
   Does it extend an existing layer or introduce a new one? If new, define
   its prefix convention and update the section-numbering table above.

2. **Write the normative preamble.** Fill in all five fields: Status (always
   Normative), Version, Source of truth (cite specific files), Scope (with
   "does NOT cover" sentence), Companion documents.

3. **Anchor to `test-suite/annotations.md`.** Preserve paragraph numbering
   wherever possible. Note the correspondence with `_Corresponds to
   annotations.md §N_` on each section that mirrors a test paragraph.

4. **Add a Gap Analysis section.** Be explicit about what the document does
   not prove or specify. Use the `G` prefix for gap codes (e.g., G6: dict/set
   membership — abstract, not modelled in WhyML). Gaps anchor the boundary
   between "this is a known limitation" and "this is a bug."

5. **Cross-reference both ways.** Update the "Companion documents" sections
   of all sibling docs to point to the new document.

6. **Update this skill** (`pycsl-docs/SKILL.md`) to include the new layer
   in the Three-Layer Stack table and the navigation table.

7. **Update `pycsl-annotate/references/validation-stack.md`** if the new
   document introduces new IS/SR/TR rules or gap codes that affect contract
   validity.

---

## Relationship to Other Skills

- **`pycsl-annotate`** — the annotation workflow skill. Its
  `pycsl-annotate/references/validation-stack.md` distils IS-1…IS-6, SR-1…SR-6, TR-1…TR-6 from the three
  reference docs into a single decision checklist.
- **`pycsl-how-to-develop`** — the developer onboarding skill. Explains the
  full pipeline architecture, CLI flags, agent system, and how to add new
  language features. Reference docs should be updated as part of the
  8-step "How to Add Features" checklist in that skill.
