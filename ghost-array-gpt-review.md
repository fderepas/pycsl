Review of `ghost-array.md`.

## Overall verdict
Needs revision before implementation. The direction is good, but it underestimates how many Module6 code paths must learn ghost-array semantics, and `\\is_permutation` is riskier than presented.

## Strong points
- The current gap is identified correctly.
- Ghost arrays should be mutable values, not ref-wrapped scalars.
- The main work is in parser, semantic, IR, and WhyML layers, not Rocq/Lean.
- `desugar_correct` is unrelated to this change.

## Main issues / technical risks
- Module6 array-sensitive paths extend beyond `_handle_ghost_assign_stmt`; they also include `_handle_var_expr`, `_handle_subscript`, `_handle_len_call`, `_handle_join_call`, `_classify_iterable`, `_scan_preamble_needs`, and body-state setup.
- Simply unioning `_ghost_array_vars` into `_current_array1d_params` is insufficient.
- Memory-model differences are under-specified.
- `\\is_permutation` via recursive `count` is solver-heavy and will need extra Why3 lemmas.
- `declared_type="array"` needs a precise semantic mapping.

## Formal-proof impact
No Rocq/Lean proof change is likely for ghost arrays. This is mainly Layer 1 + Why3 work per `src/self-annotate/README.md` and related docs. `\\is_permutation` is a Why3/solver issue, not a proof-assistant issue.

## Specific suggestions
- Add explicit ghost-array handling in all Module6 array-sensitive paths.
- Separate ghost kind from Python type strings.
- Gate the first version to Hoare/concurrent unless a non-Hoare encoding is defined.
- Defer `\\is_permutation` until `\\copy` + update + swap lemma work is in place.
- Start with a small end-to-end test.

## Suggested priority
- High: core plumbing
- Medium: `\\is_permutation`
- Low: Rocq/Lean
