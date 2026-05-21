Review of `ghost-dictionnaries.md`.

## Overall verdict
Promising, but not ready as written. The core idea fits PyCSL well, especially as a ghost-only extension, but the document overstates some current-state details and leaves a semantic hole around `\map_dom`.

## Strong points
- It targets a real gap: integer-only ghost dictionaries are a useful missing abstraction.
- `map.Map` plus `map.Const` is the right Why3 foundation for this feature.
- The proposal reuses the existing ghost pipeline instead of introducing a new proof architecture.

## Main issues / technical risks
- The current-state table is incomplete: Module6 already has runtime dict lowering and dict locals, so the feature is not starting from a blank slate.
- `\map_dom(m, k)` is underspecified for total maps with default `0`; “explicitly set” and “currently non-default” are not the same thing.
- Typed ghost syntax will require real parser grammar and transformer changes, not just a `declared_type` field.
- Helpers like `map_count` and `map_sum` are likely solver hot spots and may need careful axiom/lemma design.

## Formal-proof impact
No Rocq/Lean changes are needed for the base feature. Most of the work is Layer 1 plus Why3 translation. Optional higher-level predicates would need Why3 lemmas or axioms, not proof-assistant work.

## Specific suggestions
- Revise the current-state section to mention existing dict lowering in Module6.
- Replace `\map_dom` with a clearer predicate, or drop it until the semantics are nailed down.
- Make parser support explicit in Module2 rather than implied by type metadata alone.
- Keep `ghost x = ...` backward-compatible.
- Add parser tests for both legacy and typed ghost forms.

## Suggested priority
- **P1:** parser, semantics, and transpiler plumbing.
- **P2:** optional counting/sum helpers and documentation.
