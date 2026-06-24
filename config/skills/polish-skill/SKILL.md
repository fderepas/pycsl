---
name: polish-skill
description: >-
  Provides guidelines and utilities for polishing existing skills, ensuring consistent documentation, naming conventions, and complete metadata across the skill repository. Use to audit or improve other skill definitions.
---

# Polish Skill

This skill offers best‑practice recommendations for cleaning up and standardising the other skills in the
`config/skills/` directory. It checks that each skill has a valid `SKILL.md` manifest, proper markdown
structure, and that the `name` field matches the directory name.

Typical actions performed by this skill:
- Verify the presence of a `SKILL.md` file.
- Ensure the `name` entry equals the directory name.
- Confirm the description is non‑empty and follows the one‑paragraph style.
- Report any deviations for manual correction.
