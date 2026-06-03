# Review of `pure-ast-parsing-in-pycsl.md`

## Verdict

The plan is **well-structured and intellectually honest** — the A/B decomposition, the
"two native parsers, not one" insight about `libcst`, and the "trust relocates, it does
not vanish" framing are all correct and align with PyCSL's 0-`\trusted` discipline. The
phasing and decision points are the right shape.

**But its single most load-bearing premise is factually stale.** The plan repeatedly
asserts that `pure_ast.parse` "still calls `compile` internally" and that Change B must
"build a real tokenizer + parser" and "delete the `compile` calls (`pure_ast.py:357,399,403`),
the `_from_builtin` transcriber, and the `_C_AST_BASE` introspection." **None of that
matches the committed `src/pycsl/pure_ast.py`.** The current file (HEAD, 3502 lines) already
*is* a hand-written, compile-free front-end:

- `parse()` (`pure_ast.py:1913`) tokenizes via stdlib `tokenize` (`import tokenize as _tokenize`,
  line 405 — pure Python, `compile`-free) and runs a hand-written recursive-descent parser
  (`_lex` at 443, `class _Parser` at 492, ~1300 lines).
- There is **no** `compile(` call anywhere in the file, **no** `_from_builtin`, **no**
  `_C_AST_BASE`. The node schema is declarative (`_NODE_SPEC`), not introspected from `_ast`.
- The module docstring says so explicitly (lines 19–23): *"`parse` is also pure Python: it
  tokenizes with the standard library's pure-Python `tokenize` module (which does **not** use
  `compile`) and runs a hand-written recursive-descent parser."*

So **Change B is substantially already done.** The plan reads as if written against an
earlier, `compile`-backed draft of `pure_ast` that the committed file has superseded. Before
anything else, the plan must be **re-grounded against the file as it exists** — otherwise
Phase 2 ("build the parser") mostly re-describes work already in the tree, and Phase 0's
rationale ("it passes *because* it inherits `compile`'s output") is untrue: it passes because
the hand-written parser is good. (Differential is **512/517**, not the "517/517" the §5 table
claims — 5 files use intentionally-deferred constructs that raise `PyCSLSyntaxError`; see
`pure_ast.py:49–52`.)

## Critical issue the plan would introduce: the `src/pycsl_lib/ast.py` collision

Phase 1, step 1 says: *"Create `src/pycsl_lib/ast.py` as the seam … re-export the public `ast`
surface from `pure_ast`."* **That file already exists and is something entirely different.**
`src/pycsl_lib/ast.py` is the **PyCSL verification stub** — the 0-`\trusted` model that *user
programs* import and that gets *verified by* pycsl (`NodeVisitor` as a body-verified record,
`parse`/`literal_eval` as `#@ \abstract` vals). It references `pure_ast` **zero** times, by
design.

There are two distinct "ast" concerns the plan conflates:

| | `src/pycsl_lib/ast.py` (exists) | `src/pycsl/pure_ast.py` (exists) |
|---|---|---|
| Role | verification **model** of `ast` | runtime **implementation** of `ast` |
| Consumer | *user code under verification* | the *toolchain* (Module3/4/5) |
| Form | `#@`-annotated stubs, 0 `\trusted` | real parser + node classes |

Routing the toolchain's parser seam through `src/pycsl_lib/ast.py` would **clobber the
verification stub** (or fuse two opposite purposes into one file). The seam for Change A must
live elsewhere — e.g. `Module3/4/5` do `import pure_ast as ast` directly, or a new
`src/pycsl/_ast_compat.py`. **Do not reuse `src/pycsl_lib/ast.py`.** This is the one change in
the plan that would actively break the build, so correct it before any work.

## What is actually left (re-scoped)

The plan's *bones* are right; the *state* is wrong. Re-cast:

- **Change A — route Modules 3/4/5 through `pure_ast` — STILL THE RIGHT FIRST STEP, NOT DONE.**
  Verified: `Module3_Weaver.py:328` (`ast.parse`) is the only Python-source parse in the
  Module1–6 pipeline; `M3:25 / M4:155 / M5:30` subclass `ast.NodeVisitor`; the `ast.walk` /
  `iter_child_nodes` sites are as listed; all three do plain `import ast` (M3/4/5:3). Keep this
  as Phase 1 — but fix the seam location (above) and note the genuinely-new piece is the
  **pipeline-level differential** (run the corpus through both stdlib-`ast` and `pure_ast`,
  assert byte-identical IR/WhyML). That harness does **not** exist yet — the only differential
  today is `pure_ast._self_test` (in-file, `dump`-level vs stdlib `ast`); there is no
  `test-suite/pure-ast*`.
- **Change B — "build the parser" — REFRAME as "harden + verify the parser that exists."**
  The remaining real work is: (a) the **5/517 deferred constructs** (`pure_ast.py:74–86` lists
  them — close or document as permanently unsupported); (b) the **`col_offset` codepoint-vs-byte
  divergence**, which the plan flags correctly *and which `pure_ast` already documents as a live
  bug* (lines 81–86: `tokenize` gives codepoint columns, CPython's `ast` gives UTF-8 byte
  offsets) — the highest-value fidelity gap, since `include_attributes=True` differentials and
  downstream line/col reporting diverge on non-ASCII source today; (c) decide the **stdlib
  `tokenize` dependency** — `pure_ast` is `compile`-free but **not stdlib-free** (it took the
  plan's own §7-Q2 "reuse stdlib tokenize" option). Defensible, but state it as *already decided*
  and assess `tokenize`'s own f-string/error divergences rather than presenting it as open.
- **Verification ambition — the plan over-worries.** §3/§Phase 3 fret about a "memoizing PEG
  parser (backtracking, mutable state)" being hard to verify. The shipped parser is
  **recursive-descent**, not a memoizing PEG engine — a materially more tractable verification
  target (and closer to PyCSL's static subset). Rewrite the verification section around the
  actual implementation, and lean on the **`#@ \abstract`** primitive: `pure_ast.parse`
  is the canonical irreducibly-opaque op whose honest model is a bodyless `val` + bounded raises
  (`raises SyntaxError`) — exactly what `src/pycsl_lib/ast.py:parse` already is. "Ship the parser
  `\trusted` initially" should be "model it `#@ \abstract` (not `\trusted`) — 0 trusted; the spec
  is the auditable boundary."
- **`libcst` (Module1) — fully correct, keep as-is.** Verified: `Module1_Ingestor.py:225`
  (`cst.parse_module`) is the only libcst parse, a genuine native (Rust) boundary equal in kind
  to `compile` under UB-7.4. The Option-1/Option-2 split and "don't let Option 2 attach to
  Change B" advice are sharp; keep them.

## Smaller corrections / nits

- §1 "the only Python-source parse is `Module3_Weaver.py:328`" is true **only within
  Module1–6**. `pycsl.py:115,160` (dependency loading) and several `agents/*`, `proof2why3/*`
  modules also call `ast.parse`. Change A is incomplete if `pycsl.py`'s import-resolution still
  parses dependencies with stdlib `ast` — either scope the claim to the core pipeline explicitly
  or include `pycsl.py` in Change A.
- §5 "517/517 files passed" → **512/517** (5 deferred). Cite `pure_ast.py:49`.
- §4 Phase 0 "passes *because* `pure_ast` inherits `compile`'s output" → delete; it inherits
  nothing.
- §4 Phase 2.3 "delete `compile` calls (357,399,403), `_from_builtin`, `_C_AST_BASE`" → these do
  not exist; delete the step.
- §5 caveat about `_from_builtin` / version pinning → the *transcriber* is gone, but the
  version-pinning point survives in a new form: the hand-written grammar still targets 3.12
  (docstring line 25) and `_build_nodes` injects classes into `globals()` via `type()` (305/314).
  Keep the "pin 3.12 / fail loudly on unknown node" guidance, re-attributed to the grammar, not
  `compile`.

## Recommendation

Rewrite the plan against the committed `pure_ast.py` and re-title it to reflect reality: the
project is **(1) wire the pipeline onto `pure_ast` (Change A — days; the real near-term win) and
(2) harden + verify the already-written parser (close the 5 deferred constructs, fix `col_offset`
byte semantics, decide on `tokenize`, model `parse` as `#@ \abstract`)** — not "build a parser."
Fix the `src/pycsl_lib/ast.py` seam collision first. Keep the `libcst` analysis and the
differential-as-gate instrument verbatim — those are the plan's strongest parts.
