Review of `ghost-lists.md`.

## Overall verdict

Major revision needed. The core idea is sound, but the plan underestimates how many paths in `src/pycsl` and the self-annotate mirror tree need coordinated updates.

## Strong points

- Correctly identifies an int-only ghost pipeline.
- Good separation between Python `list` to Why3 `array int` and ghost lists to Why3 `list int`.
- Ref-wrapped ghost lists are the right model.

## Main issues / technical risks

- `Module4` does not really support `list[T]` deeply because generics are mostly dropped to `Any`.
- New list AST nodes will need updates to variable extraction and `_iter_csl_children`.
- `Module6` has many list/array classification paths that would miscompile ghost lists unless updated consistently.
- Self-annotated Rocq/Lean copies are omitted from scope.

## Formal-proof impact

No Rocq/Lean proof changes seem required. This is mostly Layer 1 plus Why3 work. Conversion/permutation helpers will likely need Why3 lemmas and solver tuning.

## Specific suggestions

- Use a distinct `declared_type = "ghost_list"` end-to-end rather than overloading `list`.
- Defer `\to_list` and permutation helpers until core `\nil`, `\cons`, and `\append` work.
- Add explicit Why3 helper lemmas for `length`, `append`, `mem`, and `nth`.
- Update self-annotated copies and the coverage report.

## Suggested priority

- **P1:** plumbing
- **P2:** Why3 imports/lemmas + smoke tests
- **P3:** conversion/permutation builtins and docs
