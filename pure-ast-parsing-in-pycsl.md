# Pure-AST Parsing in PyCSL

**Status:** Draft / proposal (v2 — re-grounded against the committed `pure_ast.py`)
**Goal:** Make PyCSL's *toolchain* stop depending on CPython's C parser by routing
Modules 3/4/5 through the already-written, `compile`-free `src/pycsl/pure_ast.py`,
then harden + verify that parser and (optionally) retire the remaining native
boundary (`libcst` in Module 1).
**Scope note:** Grounded in the actual module sources (`Module1`–`Module6`), the
committed `src/pycsl/pure_ast.py` (HEAD), and a drop-in compatibility check against
the exact API those modules use. Claims are cited to `file:line`.

> **v2 correction.** v1 assumed `pure_ast.parse` was `compile`-backed (with a
> `_from_builtin` transcriber and `_C_AST_BASE` introspection, `compile` at
> `357/399/403`). The committed file is **not** that: `pure_ast.parse`
> (`pure_ast.py:1913`) already tokenizes with the stdlib pure-Python `tokenize`
> module (`import tokenize as _tokenize`, line 405) and runs a **hand-written
> recursive-descent parser** (`_lex` at 443, `class _Parser` at 492). There is no
> `compile(`, no `_from_builtin`, no `_C_AST_BASE` in the file; the node schema is
> declarative (`_NODE_SPEC`). **The "build a real parser / remove `compile`" work
> is substantially already done.** This plan is re-scoped accordingly.

---

## 1. Verified current architecture

Where Python *source text* becomes a tree, and what each stage depends on:

| Stage | File:line | Parser / input | Produces |
|-------|-----------|----------------|----------|
| Ingest `#@` comments | `Module1_Ingestor.py:225` | **libcst** (`cst.parse_module`) | `List[PyCSLContract]` — comment metadata |
| Parse Python + weave | `Module3_Weaver.py:328` | **stdlib `ast`** (`ast.parse`) | `ast.AST` with `csl_*` attributes |
| Semantic analysis | `Module4_SemanticAnalyzer.py:155` | consumes the `ast.AST` | scope/type diagnostics |
| IR emission | `Module5_IREmitter.py:30` | consumes the `ast.AST` | JSON IR |
| WhyML transpile | `Module6` | consumes the JSON IR | `.mlw` |

Facts, all re-verified:

1. **`Module3_Weaver.py:328` (`ast.parse`) is the only Python-source parse inside
   the Module1–6 pipeline.** Modules 4 and 5 never parse — they receive the tree
   Module 3 built. **However**, the wider tool *does* parse elsewhere:
   `pycsl.py:115,160` (dependency loading, `_ast.parse`), and several
   `agents/*` + `proof2why3/*` modules. **Change A is only complete if `pycsl.py`'s
   import-resolution path is migrated too** — scope it to the core pipeline *and*
   `pycsl.py`, not Module 3 alone.
2. **Modules 3/4/5 are *consumers* of the `ast` node API, not parsers.** All three
   subclass `ast.NodeVisitor` (`M3:25`, `M4:155`, `M5:30`) and `import ast`
   (`M3/4/5:3`); they call `ast.walk` (`M3:311`; `M4:411,459,482,489,589`;
   `M5:1029`), `ast.iter_child_nodes` (`M4:349`), and isinstance-check ~70
   `ast.<Node>` classes — including the deprecated `ast.Index` (`M5:563,718`).
3. **There is no Python parser to *build* inside Module1–6** — and crucially, there
   is already a complete one in `pure_ast.py`. `Module2_Parser` parses the `#@`
   contract DSL (Lark/EBNF, `M2:966`), not Python. The Rocq/Lean semantics in
   `src/formal-semantics/` are a soundness proof over a small core subset, not an
   executable parser.

**Two distinct native/external parsers remain, and they are not equal in kind:**

- `libcst` (Rust extension) — `Module1_Ingestor.py:225`. A genuine native boundary
  under UB-7.4.
- stdlib `tokenize` — used *inside* `pure_ast` (`pure_ast.py:405`). Pure Python, so
  **not** a native boundary, but still an external stdlib dependency with its own
  fidelity quirks (f-strings, error recovery).

`compile` is **already gone** from `pure_ast`'s parse path. Removing stdlib `ast`
from the pipeline (Change A) does not, by itself, remove `libcst` — any end-state
that claims a self-contained front-end must address Module 1 (§3).

---

## 2. Reframing: two orthogonal changes

- **Change A — Decouple the *toolchain* from stdlib `ast`.** Route Modules 3/4/5
  (and `pycsl.py`'s dep loading) through `pure_ast`. This collapses the pipeline
  onto a single parse chokepoint, `pure_ast.parse`. *Mechanical and low-risk*:
  `pure_ast` is a validated drop-in (§5). **Not yet done.**
- **Change B — Harden + verify `pure_ast`'s hand-written parser.** *Not* "build a
  parser" — the recursive-descent parser exists and passes a 512/517 stdlib
  differential. The remaining work is: close the deferred constructs, fix the
  `col_offset` byte-offset divergence, settle the `tokenize` dependency, and model
  `parse` for verification. *Real but bounded — no greenfield parser project.*

Doing A first still pays off: it makes `pure_ast.parse` the single chokepoint, so
any later parser change (Change B fidelity fixes, or an eventual self-hosted
tokenizer) propagates to the whole pipeline through one function.

---

## 3. The second-parser decision (libcst)

- **Option 1 — Scope to stdlib `ast` only.** Route Modules 3/4/5 + `pycsl.py`
  through `pure_ast`; leave Module 1 on `libcst`, declared as a `\trusted`/native
  boundary with a named reviewer. PyCSL's *Python tree* is then produced by
  PyCSL-owned code; comment extraction stays native. Smaller, achievable.
- **Option 2 — Eliminate `libcst` too.** Extend `pure_ast` with a lossless,
  comment/trivia/exact-position concrete mode so Module 1 can drop `libcst`.
  Strictly larger: it means reproducing `libcst`'s job, not just stdlib `ast`'s.

Recommendation: target **Option 1** now; keep **Option 2** as the north star
(§Phase 3). Do not let Option 2's scope silently attach to Change B.

---

## 4. Phased plan

### Phase 0 — Persist the differential oracle (prerequisite)

Today the only differential is `pure_ast._self_test` (`pure_ast.py:3384`, invoked
`python pure_ast.py --self-test`): it parses every stdlib `.py` with both `pure_ast`
and stdlib `ast` and compares `ast.dump` — **512/517 byte-identical, 0 mismatches,
0 crashes; 5 files use intentionally-deferred constructs that raise
`PyCSLSyntaxError`** (`pure_ast.py:49–52`). This is a real, earned result (the parser
is hand-written), not inherited from `compile`.

- **Persist + widen it** as a repo test (e.g. `test-suite/pure-ast-differential/`):
  keep the `dump` differential, add a `ast.parse(pure_ast.unparse(t))` round-trip,
  and add `include_attributes=True` (this is what surfaces the `col_offset` gap —
  see Phase 2b).
- **Add the pipeline-level differential** (this does **not** exist yet): run the
  full PyCSL pipeline on the reference corpus twice — stdlib `ast` vs `pure_ast` —
  and assert identical IR/WhyML. This is the acceptance gate for **Change A**.
- Add CPython's own grammar/`ast` tests to the corpus for Phase 2.

### Phase 1 — Change A: route the toolchain through `pure_ast`

1. **Pick a seam that does not collide with the verification stub.**
   `src/pycsl_lib/ast.py` **already exists** and is the *PyCSL verification stub*
   (the 0-`\trusted` model user code imports and that pycsl verifies —
   `NodeVisitor` as a record, `parse`/`literal_eval` as `#@ \abstract` vals; it
   references `pure_ast` zero times). **Do not put the toolchain seam there** — it
   would clobber a file with the opposite purpose. Instead either:
   - have Modules 3/4/5 + `pycsl.py` do `import pure_ast as ast` directly, or
   - add a thin `src/pycsl/_ast_compat.py` that explicitly re-exports the needed
     `pure_ast` surface (prefer explicit re-exports over `from pure_ast import *`,
     so the dynamic class injection / metaclass surface isn't widened).
2. Change `import ast` → the chosen seam in `Module3/4/5` and `pycsl.py:115,160`.
   No other edits expected (§5).
3. Run the Phase 0 pipeline differential. Acceptance: **byte-identical IR and WhyML**
   on the entire reference corpus.

Risk: low. The behavioral surface is enumerated and satisfied in §5.

> Disambiguation to keep front-of-mind throughout:
> | | `src/pycsl_lib/ast.py` | `src/pycsl/pure_ast.py` |
> |---|---|---|
> | Role | verification **model** of `ast` | runtime **implementation** |
> | Consumer | user code under verification | the toolchain (M3/4/5) |
> | Form | `#@` stubs, 0 `\trusted` | real parser + node classes |

### Phase 2 — Change B: harden + verify the existing parser

The parser exists; this is fidelity + verifiability work, each piece independently
testable against the Phase 0 differential.

**2a. Close (or formally defer) the 5 unsupported constructs.** `pure_ast.py:74–86`
enumerates the deferred constructs that raise `PyCSLSyntaxError`. Either implement
them in `_Parser`, or document them as permanent unsupported with a clear message
(loud failure, never a wrong tree — the current discipline).

**2b. Fix `col_offset` codepoint-vs-byte semantics.** `pure_ast` already documents
this as a live bug (`pure_ast.py:81–86`): `tokenize` yields *codepoint* column
offsets, whereas CPython's `ast` reports UTF-8 *byte* offsets. This is the
**highest-value fidelity fix** — `include_attributes=True` differentials and any
downstream line/col reporting diverge on non-ASCII source today. Convert codepoint
columns → byte columns per line in the node-construction path.

**2c. Settle the `tokenize` dependency (decision, not open question).** `pure_ast`
took the "reuse stdlib `tokenize`" route. State this explicitly and assess its
divergences from the C tokenizer (notably PEP 701 f-strings and error recovery);
decide whether to keep it (pure-Python, so not a UB-7.4 native boundary) or write a
self-hosted tokenizer later (only needed for a fully self-contained, verifiable
front-end). Not a blocker for A.

**2d. Model `parse` for verification — `#@ \abstract`, not `\trusted`.** The shipped
parser is **recursive-descent**, not a memoizing PEG engine, so it is a far more
tractable verification target than v1 feared. Until/unless its body is written in
PyCSL's static subset and proven, model `pure_ast.parse` as an `#@ \abstract` val
with a bounded raises set (`raises SyntaxError`) — exactly the form
`src/pycsl_lib/ast.py:parse` already uses. This is the 0-`\trusted` boundary: the
contract is the auditable assumption, not an unchecked body.

Acceptance: the Phase 0 differential (now including `include_attributes` + the
round-trip) and CPython grammar tests pass on the corpus.

### Phase 3 — North star (optional): unify and verify

- **Replace `libcst` (Option 2):** extend `pure_ast` with a lossless,
  comment/trivia-preserving mode so Module 1 drops `libcst`. Then one PyCSL-owned
  front-end serves both comment extraction and the AST, and the last native boundary
  is gone.
- **Verify the parser:** only meaningful once it is written in PyCSL's static,
  verifiable subset. Recursive descent is tractable, but the dynamic node-class
  construction (`_build_nodes` injecting via `type()` into `globals()`, `pure_ast.py:289–314`;
  the `_ABC` `__instancecheck__` metaclass, `334–346`; reflective `getattr` dispatch,
  `2247–2253`) is unverifiable and would need a static rewrite. Treat full
  verification as a separate research goal; ship `parse` `#@ \abstract` (per 2d) in
  the meantime.

---

## 5. Drop-in compatibility checklist (Change A)

Verified against the running modules and the committed `pure_ast`:

| Requirement (used by M3/4/5) | `pure_ast` status |
|------------------------------|-------------------|
| `parse`, `walk`, `iter_child_nodes`, `NodeVisitor` | present (`1913/2022/2011/2247`) |
| `NodeVisitor.visit/generic_visit` reflective dispatch on a `pure_ast` tree | works (`2247–2253`) |
| ~70 node classes used in isinstance (`Assign`…`MatchOr`) | present (`_NODE_SPEC`) |
| Base categories `AST/expr/stmt/operator/cmpop/unaryop/comprehension` | present |
| Deprecated `Index`/`ExtSlice` (`M5:563,718`) | present (shims, `_NODE_SPEC:207–208`) |
| Arbitrary attribute assignment (`csl_*`) | works (no `__slots__` on nodes) |
| Stdlib differential (`dump`) | **512/517** (5 deferred; `pure_ast.py:49`) |

Caveats to track (not blockers for A; targets for B):

- **`col_offset` byte-vs-codepoint divergence** — see Phase 2b. Already a documented
  `pure_ast` limitation; matters for `include_attributes=True` and non-ASCII source.
- **Version pinning.** The hand-written grammar targets **Python 3.12** (docstring
  line 25); `_build_nodes` injects node classes via `type()` into `globals()`
  (`289–314`). Pin 3.12 explicitly and keep a loud failure on unknown constructs.
  *(v1's `_from_builtin`/`compile`-drift concern no longer applies — that path does
  not exist — but the single-language-version point survives, re-attributed to the
  grammar.)*
- **Wrapper dynamism.** The `type()`-injection, `__instancecheck__` metaclass, and
  reflective dispatch are fine at runtime but unverifiable — the reason Phase 3
  verification needs a static rewrite, and the reason the Phase 1 seam should use
  explicit re-exports rather than widening that dynamic surface.

---

## 6. Risks and honest costs

- **Effort.** Change A is days. Change B is bounded fidelity work (2a–2d), not a
  parser project; Option 2 (drop `libcst`) is the genuinely large piece.
- **Fidelity is now *earned*, not inherited.** v1 said every "matches CPython"
  result traced to `compile`; that is no longer true — the hand-written parser earns
  512/517 directly, and the differential corpus is what keeps it honest. The risk is
  the **tail**: the 5 deferred constructs and the `col_offset` gap are real divergences
  from CPython that the differential must drive to zero.
- **Trust does not vanish, it relocates.** Until the parser is verified it is an
  `#@ \abstract` boundary (not `\trusted`): proofs about parsed programs are
  conditional on the front-end's correctness, witnessed by the differential.
- **`libcst` remains** unless Option 2 is taken — the last native boundary.
- **Performance.** Recursive-descent pure-Python parsing is slower than the C
  parser; measure against the corpus, since CI runs the pipeline repeatedly.

---

## 7. Decision points

1. **Scope:** Option 1 (replace stdlib `ast` only) or Option 2 (also replace `libcst`)?
2. **`tokenize`:** keep the stdlib pure-Python `tokenize` (current choice — fast,
   pure-Python, but inherits its f-string/error quirks) or write a self-hosted
   tokenizer (only needed for a fully self-contained front-end)?
3. **Verification ambition:** ship `parse` `#@ \abstract` (recommended near-term), or
   commit up front to the static-subset rewrite needed to verify the parser body?
4. **Target language version:** confirm 3.12.x as the single supported grammar.

---

## 8. Acceptance criteria

- **Change A done when:** Modules 3/4/5 **and** `pycsl.py`'s dep loading import the
  `pure_ast` seam (not `src/pycsl_lib/ast.py`), and the full pipeline produces
  byte-identical IR/WhyML to the stdlib-`ast` baseline on the reference corpus.
- **Change B done when:** the 5 deferred constructs are closed or formally documented;
  the `col_offset` byte-offset fix lands; the stdlib `dump` + round-trip differential
  passes with `include_attributes=True`, plus CPython grammar tests, on the corpus;
  and `parse` is modeled `#@ \abstract` (0 `\trusted`).
- **Option 2 done when:** `Module1` no longer imports `libcst` and comment extraction
  runs on the pure front-end with unchanged `PyCSLContract` output.
