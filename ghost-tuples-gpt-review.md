Review of `ghost-tuples.md`.

## Overall verdict
Good direction, but the scope looks under-defined. This is mostly a Layer 1 / WhyML codegen change, not a Rocq/Lean proof rewrite.

## Strong points
- Correctly identifies the `Tuple` -> `0` fallback in Module6 normal assign paths.
- Choosing fixed-arity `tuple2`/`tuple3`/`tuple4` is the right shape.
- Whole-tuple reassignment only is consistent with Why3 tuple semantics.
- Keeping the change out of `src/formal-semantics` proofs is the right instinct.

## Main issues / technical risks
- Module4 needs more than scope registration: `_iter_csl_children()` must recurse into new tuple nodes.
- Falling back from unsupported `\\proj` to `0` would be unsound; those cases should be rejected earlier.
- Inferring tuple arity from variable names is fragile; arity should live in the IR.
- Self-annotated Rocq/Lean copies appear to be missing from scope.

## Formal-proof impact
No Rocq/Lean theorem changes seem necessary. Only a Layer 3 bridge spec would create proof work, and ghost tuples alone do not imply that.

## Specific suggestions
- Add tuple nodes to `_iter_csl_children()` and validate arity/index explicitly.
- Carry tuple arity in IR instead of looking it up from names.
- Make unsupported `\\proj` cases hard errors.
- Update self-annotated copies and coverage-report expectations.
- Add focused tests for `\\mktuple`, `\\fst`, `\\snd`, `\\proj`, and tuple ghost reassignment.

## Suggested priority
High for correctness and scope, low for proof risk.
