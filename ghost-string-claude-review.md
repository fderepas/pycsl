# Review of `ghost-string.md` — Claude

## Overall verdict

Highest strategic value of the six plans — string ghosts partially close the Layer 1
string-building barrier — but the plan overstates what this achieves relative to Layer 3
and underestimates how deeply the string domain is entangled in Module6.

---

## Key strengths

- **Correct diagnosis of the root cause**: Module4 hard-codes `"int"` for all ghost
  variable scope entries regardless of declared type. This is the single line that
  blocks string ghosts.
- **Module2 already parses strings**: `ESCAPED_STRING → StringLiteral` is in the grammar
  today; the parser change is purely additive.
- **`_expr_to_whyml_string_ctx` as a separate method**: the right architectural choice.
  A dedicated string-context transpiler avoids contaminating the int-context path and
  makes the feature independently testable.
- **`^` operator is safe**: not in the current contract grammar; Python's bitwise XOR
  `^` is not supported in PyCSL contracts, so there is no conflict.
- **Backward compatibility**: default `declared_type = "int"` preserves all existing
  tests.

---

## Critical issues

### Issue 1 — Layer 3 replacement claim is incorrect (must retract)

The plan states:
> "Applied across all 10 WP arms, string ghosts could replace: 10 val string specs,
> 9 val function code specs, 4 human-audited coherence axioms."

This is incorrect and would mislead implementers about what work remains.

String ghosts prove: `\result == _out` where `_out` is a ghost string built step by step
in the Python body. This closes the **output-shape** gap at Layer 1: we know the
function returned the exact string the ghost tracked.

Layer 3 (`pycsl-wp-spec.mlw`) proves something different: the generated string is
semantically equivalent to evaluating the WhyML WP rule — i.e., that `eval_whyml_stmts
code st = update st x val`. String ghosts cannot express this because `\result` in
PyCSL is a `string`, not a state transformer.

**Fix**: reframe as "string ghosts strengthen Layer 1 contracts by making the output
shape machine-checked, while Layer 3 continues to prove semantic equivalence."

### Issue 2 — Module6 does not preserve strings in spec context today

The plan's Section 5c shows:
```python
if t == "String":
    if getattr(self, '_in_spec', False):
        return f'"{escaped}"'        # preserve in contracts
    return str(hash(f'"{escaped}"') % 2147483647)  # hash in body
```
and presents this as a modification. But the current code has no conditional — it always
hashes. This needs to be stated clearly as a new branch, not presented as an existing
conditional being extended.

### Issue 3 — `needs_string` flag is hardwired to False

The preamble scan controls `use string.String` emission via a `needs_string` flag, but
inspection of Module6 shows this flag is never set to `True` in practice (the code path
that would set it is unreachable in the current implementation). The plan says "extend
it to detect string ghost usage" without showing the mechanism.

**Fix**: set `self._needs_string_ghost = True` when any `ghost_type == "string"` IR node
is encountered during the function scan, then check this flag in `_emit_preamble`.

### Issue 4 — Additional Module6 touch points not covered

The plan covers `_handle_ghost_assign_stmt` and `_expr_to_whyml`. But the string domain
also touches:
- `_coerce_str_arg`: used when a function call expects a string argument; must not
  coerce ghost string variables to `int`.
- `_handle_fstring_expr`: f-string handling in body context; ghost strings should not
  participate in f-string lowering.
- Return-type inference: `_infer_return_type` may see `string` annotations and produce
  wrong WhyML types if string ghosts are in scope.

These paths must be audited and gated on `ghost_type != "string"` where relevant.

### Issue 5 — `_in_spec` state at ghost declaration site

Ghost variable declarations (`let ghost s = ref "hello" in ...`) are emitted inside
`_handle_ghost_assign_stmt`, which is called from the statement-level transpiler. At
that point `self._in_spec` may be `False` (body context). The string initializer must
always be treated as a string literal even in body context, because the ghost declaration
is not a runtime computation.

**Fix**: in `_handle_ghost_assign_stmt`, when `ghost_type == "string"`, always use
`_expr_to_whyml_string_ctx` regardless of `self._in_spec`.

---

## Suggestions

1. Retract the Layer 3 replacement claim; add a subsection "What string ghosts do and do
   not prove" clarifying the Layer 1 / Layer 3 split.
2. Fix the current-state table: "Module6 hashes ALL string literals to ints in both spec
   and body context today."
3. Add `self._ghost_string_vars: Set[str]` to `_reset_function_state`; use it to gate
   the string-context path in the Var handler.
4. Add `self._needs_string_ghost: bool` flag; set it during IR scan, check in
   `_emit_preamble`.
5. Audit `_coerce_str_arg`, `_handle_fstring_expr`, return-type inference.
6. Document `^` precedence explicitly: binds tighter than `and`/`or`/`==>`, looser than
   function application.
7. Confirm that `_in_spec` is set correctly (or is irrelevant) at the ghost declaration
   emit site.

---

## Suggested staging

**Phase 1 (minimal viable):**
- `GhostAssignDecl.declared_type` with `"string"` value
- Module4: `ghost_type == "string"` → scope entry as `"str"`, reject `+=`/`-=`/`*=`
- Module5: carry `ghost_type` in IR
- Module6: `_handle_ghost_assign_stmt` string branch with `_expr_to_whyml_string_ctx`
- Module6: `StrConcat` handler in `_expr_to_whyml` (spec context only)
- Module6: `_needs_string_ghost` flag → `use string.String` in preamble
- Test: `ghost s : string = "a"`, `ghost s = s ^ "b"`, `ensures \result == s`

**Phase 2 (after Phase 1 tests pass):**
- `\str_length` and `\str_sub` builtins
- Audit of all secondary Module6 touch points
- Self-annotation of one Module6 handler to validate the Layer 1 strengthening

**Defer:**
- Layer 3 replacement claim investigation (will not fully materialize; document why)
- Ghost string equality via SMT string theory benchmarks

---

## Comparison with GPT review

**Agreement:**
- GPT correctly identifies the Module6 string-not-preserved-in-spec-context issue.
- GPT correctly flags `needs_string` as inactive.
- GPT correctly says the Layer 3 replacement claim conflicts with `semantic-ceiling.md`.
- GPT correctly flags the need for a dedicated ghost-type map.

**Additional issues (not in GPT review):**
- The `_in_spec` interaction at the ghost declaration site is a concrete problem not
  mentioned by GPT.
- `_coerce_str_arg` and `_handle_fstring_expr` are specific touch points GPT does not
  name.
- The `^` precedence needs to be a first-class grammar decision, not assumed.

**Disagreement with GPT:**
- GPT says "high priority: fix current-state inaccuracies first". I'd say implement in
  parallel — the current-state fix is a doc change, not a blocker for the code change.
  Start the implementation alongside the doc correction.
