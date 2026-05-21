Review of `ghost-string.md`.

## Overall verdict

Promising direction, but not accurate enough as written. The doc correctly identifies the int-only ghost limitation, but it overstates current Module6 behavior and underestimates the plumbing required to make string ghosts real.

## Strong points

- Correctly spots the hard-coded ghost type issue in Module4.
- Correctly notes Module2 already parses string literals.
- Good instinct that support must flow parser → semantic → IR → WhyML.

## Main issues / technical risks

- Module6 does not preserve strings in spec context today: `_expr_to_whyml()` hashes `String` nodes.
- `needs_string` is currently always false, so no string path is actually activated.
- String support will touch `_coerce_str_arg`, `_coerce_to_int`, `_handle_fstring_expr`, return-type inference, and metadata handling.
- `ghost s : string` and `^` need real parser, transformer, and validation changes.
- The claim that this can remove the need for Layer 3 val specs conflicts with `src/self-annotate/README.md` and `semantic-ceiling.md`.

## Formal-proof impact

No Rocq/Lean proof changes appear necessary for the implementation itself. But Why3 / Layer 3 work is still needed for semantic correspondence, and string concatenation will likely need extra solver support.

## Specific suggestions

- Recast the goal as adding string-typed ghosts at Layer 1 while keeping Layer 3 for semantic bridging.
- Add a dedicated ghost-type map instead of overloading `current_scope` with `str`.
- Thread string-awareness through Module6 explicitly.
- Whitelist `string` in the parser.
- Treat `^` precedence and solver behavior as first-class design decisions.

## Suggested priority

High: fix current-state inaccuracies and the proof-scope overclaim first. Then implement parser / semantic / IR changes. Defer optional builtins.
