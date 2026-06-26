# os.path string operations unsupported by pycsl

**Category:** Ergonomics gap (language coverage)
**Filed by:** test-supervise-sl (os.path fleet)
**Date:** 2026-06-22 (updated 2026-06-23)

## Problem

`pycsl_lib/os/path.py` uses Python string operations that pycsl cannot emit or
verify:

- `path.rfind('/')` — string search: **not supported** (emission error)
- `path.split('/')` — string split: **not supported** (emission error)
- `path[i + 1:]` / `path[:i]` — string slicing: emits as `subscript_get`
  (uninterpreted), **not connectible** to `\str_sub` in contracts
- `path[0] == '/'` — string indexing: emits but **times out** (30s,
  `subscript_get` is uninterpreted; SMT cannot relate it to `\str_sub`)
- `*parts` (variadic) in `join`: causes **duplicate `py_result` ref** emission
  (type mismatch: `int ref` shadowed by `string ref`)

## Consequence

6 of 11 `os.path` functions (`abspath`, `basename`, `dirname`, `join`,
`normpath`, `splitext`) are **unannotatable** — their bodies use unsupported
operations, so no body-verifiable contract can be added. `isabs` is annotated
but its importer consequence test **times out** (SMT string theory).

Only 4 trivial functions (`exists`, `expanduser`, `isdir`, `isfile`) are
body-verified and have proven consequence tests.

## UPDATE (2026-06-23) — partial workaround landed

A pure-Python reimplementation (Strategy A) was found to bypass several of
these gaps: `len(s)`, `s[i] == c`, `s[a:b]`, and `s + t` ARE now lowered to
body-verifiable `str_length_op` / `str_sub_op` / `str_concat_op` (with
length `ensures`), so tail-scan loops using them body-verify. **basename,
dirname, join** were rewritten this way (3/6 → body-verified, zero-TCB).
The remaining blockers:

- **splitext**: a `(str, str)` tuple RETURN is not inferred (tuple component
  type defaults to `int` → "expression has type (string, string), expected
  (int, int)"). Body-verification impossible without tuple-component-type
  inference. **Open.**
- **normpath**: `path.split('/')` and `'/'.join(parts)` still opaque; the
  `..`-resolution loop over the split result is too complex for SMT even
  with the str_sub bridge. **Open.**
- **abspath**: transitively depends on `normpath`. **Open.**
- **Stronger postconditions** (e.g. `basename` no-slash ⟹ identity, a
  `\forall` over string positions) cause SMT OOM — would need Rocq/Lean
  escalation per the doctrine.

## Suggested fix

1. Add native pycsl support for `str.rfind`, `str.split`, and string slicing
   (lower to Why3 `string.String` operations or axiomatize).
2. Connect `subscript_get` (body-level string indexing) to `\str_sub`
   (contract-level) via an axiom or built-in lemma so body-VCs can discharge.
3. Fix the variadic-args emission (`*parts` → duplicate `py_result` ref).
4. **Infer tuple-component types from the body** (`return (s1, s2)` where
   `s1`/`s2` are strings → `(string, string)`, not `(int, int)`). Would
   unblock `splitext`.
5. For SMT string-theory timeouts, route to Rocq/Lean (the doctrine's
   escalation path) — the `\str_length`/`\str_sub` goals are tractable in
   a proof assistant.
