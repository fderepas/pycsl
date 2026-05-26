---
name: polish-skill
description: Polishes an existing SKILL.md file so it triggers reliably, scans well, and preserves every technical claim verbatim from the original; when a deep polish is warranted, it also splits cleanly into a SKILL.md plus reference files. Use whenever the user says "polish this skill", "clean up my skill", "make this skill better", "this SKILL.md is too long", uploads a `SKILL.md` file for polish, or asks for help reorganizing skill content under a `references/` folder. Also use when the user wants their skill checked for the common authoring failure modes: undertriggering descriptions, mis-numbered headings, mis-indented bullets, forward references, dead file paths, mixed cautionary-vs-canonical examples, run-on prose bullets, or a single `SKILL.md` past ~500 lines that should be broken up.
---

# Polish Skill

Your job is to take an existing skill (a `SKILL.md` file, optionally with companion files in `scripts/`, `references/`, `assets/`) and produce a polished version that is easier for a model to absorb, harder to mis-trigger, and structured for progressive disclosure when oversized — without altering any technical claim.

The polish is **conservative on content** (preserve every rule, NEVER, workaround, and worked example verbatim wherever possible) and **opinionated on structure** (fix numbering, headings, indentation, forward references, and oversize). The goal is that a model loading the polished skill mid-task finds the right rule faster and applies it more reliably than it would with the original.

## When NOT to use this skill

Do not use this skill to:

- Author a *new* skill from scratch — that is a different workflow (description-driven design, eval loop, iteration). Use a skill-creator workflow instead.
- Rewrite a skill's technical content. If a rule looks wrong or outdated, flag it and ask before changing it. Hard-won verification, transpiler, or domain knowledge in the original should be preserved even when it looks odd; the user almost certainly earned it through painful debugging.
- Translate a skill between languages or harnesses. That is a port, not a polish.

## Workflow

Follow these steps in order. Do not skip the audit step — most of the value of this skill is in catching specific failure modes that are hard to see when you're already writing the output.

### Step 1 — Read the entire file

Use the `view` tool to read every line of the uploaded `SKILL.md`. If the file is large, view it in passes — but make sure you have seen every line before doing anything else. Skimming and pattern-matching to "looks like a standard skill" misses the specific issues that matter.

If companion files exist in `references/`, `scripts/`, or `assets/`, list them but do not modify them unless the user explicitly asks. The polish targets `SKILL.md`.

### Step 2 — Audit against the failure-mode checklist

Walk this list out loud (literally — write the findings to the user) before producing any output. Each item is a real failure mode that hurts skill reliability in practice:

#### Frontmatter audit

1. Is `name` lowercase-with-hyphens, no spaces? Does it match the folder name?
2. Does `description` start by saying *what the skill does* (verb phrase), then *when to use it* (trigger conditions)?
3. Does the description undertrigger? A skill that only says "annotates Python code with contracts" will be skipped when a user asks "can you add invariants to my loop." Add the informal phrasings users actually use ("add contracts", "prove this correct", "make this verifiable").
4. Does the description overtrigger? Vague triggers like "for any Python task" cause the skill to load for irrelevant requests and waste context.
5. Does the description make false claims about contents ("11+ examples" when there are exactly 11, "complete reference" when sections are missing)? Adjust to match reality.

#### Structural audit

6. Is the numbering consistent? Watch for sequences like `1, 2, 3, 3b, 4` — these are signs that a section was retrofitted as a sub-item when it should be a top-level heading.
7. Are headings semantically grouped? A section titled "Code Generation Constraints" that contains both NEVERs and supported-feature notes is doing two jobs and confuses retrieval.
8. Are forward references resolved? If Example 9 says "see §7" and §7 appears *after* Example 9, the model has to re-read the file to find it. Move §7 above, or restructure.
9. Are cautionary examples mixed with canonical examples? If Examples 1–8 are templates to imitate but Examples 9–10 carry "ASPIRATIONAL / DO NOT IMITATE" warnings, separate them into clearly-labeled sections. Mixing them is actively misleading — the model copies whichever it pattern-matches first.

#### Formatting audit

10. Are bullets indented consistently? Bullets at 5–7 spaces instead of 4 render as nested sub-items and break the visual hierarchy.
11. Are bullets concise enough to scan? A "NEVER" rule that runs 200 words loses its emphasis. Long rules belong as their own subsection with prose paragraphs, not as a bullet.
12. Is code fenced with language tags (` ```python `)? Untagged blocks render without syntax highlighting and are harder to scan.
13. Are inline references (`§7`, `Section 4`, `Example 6`) consistent throughout? Mixing `§3`, `section 3`, and `Sec. 3` makes search harder.

#### Path and link audit

14. Do all internal file references point to files that exist *and* live in the standard layout? `references/foo.md` is conventional; `test-suite/foo.md` is not.
15. Are external URLs still valid?

#### Size audit

16. Is the file under ~500 lines? Beyond that, the model's attention starts to degrade and rules get missed. If over, plan a split into `SKILL.md` plus `references/*.md`.
17. Is content that *could* be a reference still inline? Examples: detailed transpiler limits, edge-case tables, cautionary worked examples, low-frequency lookup tables. These belong in `references/`.

### Step 3 — Report findings and confirm depth

Before writing any output, summarize what you found. Group findings by severity: surface (typos, indentation, dead paths) vs structural (heading reorganization, splits, forward-reference fixes).

Then ask the user — **with the `ask_user_input_v0` tool, not as a prose question** — whether they want a light polish (surface only, keep single file) or a deep polish (everything including the split into references). Default to single-select with two options. Do not skip this step even if the file is obviously oversized; some users have hard constraints (e.g., they're shipping to a harness that does not load `references/` and want a single file regardless of length).

### Step 4 — Plan the split (deep polish only)

If the user chose deep polish and the file warrants splitting:

- The body of `SKILL.md` should keep: frontmatter, workflow steps, the canonical examples to imitate, the rules a model needs on every invocation.
- Move to `references/` files: detailed constraint lists (transpiler limits, syntax forbidden lists), tables of patterns, cautionary examples, edge-case lookup data, anything the model only needs occasionally.
- Group references by *when the model would need to load them*, not by topic similarity. A single `references/everything.md` defeats the purpose. Aim for 2–5 reference files, each scoped to a clear "I need this when…" trigger.
- In the new `SKILL.md`, end with a "Reference files" section that lists each file with a one-sentence description of when to consult it. The model uses these descriptions to decide which file to read.

Name reference files by what they contain, not by section number: `transpiler-limits.md`, `solver-heuristics.md`, `matrix-patterns.md` — not `section-5.md`, `appendix-a.md`.

### Step 5 — Write the polished files

Use `create_file` to write each output file to `/mnt/user-data/outputs/<skill-name>/`. Maintain the standard layout:

```text
<skill-name>/
├── SKILL.md
├── references/
│   ├── <topic-1>.md
│   ├── <topic-2>.md
│   └── ...
├── scripts/        (if the original had one)
└── assets/         (if the original had one)
```

If the original had `scripts/` or `assets/`, copy them through unchanged unless the user asks otherwise.

### Step 6 — Verify and bundle

After writing all files:

1. Use `bash_tool` to `wc -l` each output file and confirm the line counts are in the expected ranges (`SKILL.md` ≤ ~500 lines for deep polish; references can be longer because they load on demand).
2. Use `bash_tool` to `zip -r` the entire folder into a single archive at `/mnt/user-data/outputs/<skill-name>.zip` so the user has both individual files and a bundle.
3. Use `present_files` to surface both the zip and the individual `.md` files. The zip goes first in the array — it's the primary deliverable; the individual files are for users who want to inspect one piece.

### Step 7 — Summarize the diff

End with a short, honest summary of what changed. Explicitly call out:

- What you fixed (frontmatter, headings, examples reorganized, bullets reformatted, dead references corrected, oversize split).
- What you intentionally preserved (every technical claim verbatim).
- Anything the user should double-check (e.g., "if I dropped a claim by accident, flag it and I'll restore the original wording").

Do not pad the summary with marketing language. The user just gave you a working artifact; respect that by being precise about what is different.

## Content-preservation rules

These are absolute. Violating them turns a polish into a rewrite, which is not what the user asked for.

- **Preserve every NEVER rule verbatim** — including any explanation of *why* the rule exists. The "because Alt-Ergo times out on nonlinear products" rationale is as important as the rule itself.
- **Preserve every workaround verbatim** — the suggested fix ("introduce a `found` variable", "use `i = n` to force loop exit") is the actionable part. Do not paraphrase it.
- **Preserve every worked example verbatim** in both input and output blocks. Re-fence with ` ```python ` if the original lacked language tags, but do not edit the code.
- **Preserve cautionary warnings verbatim** ("ASPIRATIONAL ONLY", "CONTAINS FALSE INVARIANTS"). These are load-bearing; the user added them after the original failed in some specific way.
- **Preserve technical terminology verbatim** even if it looks idiosyncratic. Domain-specific terms ("frame condition", "Hoare logic", "discharge a proof obligation") are not jargon to simplify away — they signal precision and the user's audience expects them.

### What you may change

- Heading numbering, heading levels, and section ordering (when fixing forward references or moving cautionary examples out of the imitate-these block).
- Bullet indentation, list markers, line wrapping.
- Code fence language tags.
- Internal references when you renumber sections (`§7` → `§3` if §7 became §3).
- Prose around technical claims (transitions, framing sentences) — but not the claims themselves.

## Anti-patterns to avoid

- **Don't rewrite the frontmatter description from scratch.** Edit the existing one. Wholesale rewrites tend to drop triggering phrases the user added on purpose.
- **Don't merge similar NEVER rules** into a single combined rule even if they share structure. They were probably written as separate rules because they fail in subtly different ways and the user wants the model to see them as distinct.
- **Don't add new examples.** The user has not asked for new content. Polish operates only on what is already there.
- **Don't drop content silently.** If something genuinely doesn't fit anywhere in the new structure, surface it in the summary so the user can decide.
- **Don't reorder the worked examples.** Examples 1–8 are usually ordered by complexity for a reason (each builds on patterns from earlier ones).
- **Don't infer missing context.** If a section references "the schema" or "the format" without specifying, leave it ambiguous in the output and flag it for the user — do not guess what was meant.

## Output requirements

The final response to the user should:

1. Briefly state what was done (1–2 sentences).
2. Show the final file structure with line counts.
3. Summarize what changed and what was preserved (the Step 7 diff).
4. Surface the zip and individual files via `present_files`.

Do not write a long postamble. The user can read the files; they need access, not narration.
