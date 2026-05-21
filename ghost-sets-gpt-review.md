Review of `ghost-sets.md`.

## Overall verdict
Promising, but needs revision. The layering is directionally right, but the document overstates current support and underestimates the plumbing needed to make ghost sets fit cleanly into the existing pipeline.

## Strong points
- Good separation between Layer 1 concerns and Why3/L3 concerns.
- Correctly identifies `desugar_correct` as the existing Rocq/Lean blocker for `SFor`, not for ghost sets.
- `map int bool` is a pragmatic and understandable representation choice.
- `\to_set` looks like a useful later helper for bridging representations.

## Main issues / technical risks
- The current-state claims are off: Module4 still records all ghost vars as `int`, and Module5 treats `SetLit` as `dict_vars`.
- `\set_card` is inconsistent between the 1-arg examples and the bounded-cardinality design.
- Existing ad hoc set handling in Module6 should not be conflated with the proposed ghost-set semantics.
- The overall scope reads optimistic; the parser, IR, typing, and downstream lowering work are larger than the doc suggests.

## Formal-proof impact
No Rocq/Lean changes should be needed unless the theorem statement itself is extended. This is mainly a Layer 1 plus Why3 effort. Expect new Why3 lemmas/axioms for extensional equality, subset, algebraic operations, and especially cardinality and `\to_set`.

## Specific suggestions
- Make `\set_card(s, lo, hi)` the only supported form.
- Add a distinct ghost-set IR/type tag instead of reusing Python `SetLit`.
- Fix Module5 classification so ghost sets are not routed through `dict_vars`.
- Keep ghost-set refs separate from int ghost refs in Module6.
- Stage the feature: membership/add/remove first, then algebra ops, then cardinality.

## Suggested priority
- High: parser, IR, and type separation.
- Medium: Why3 lemmas and axioms.
- Low: docs and tests.
