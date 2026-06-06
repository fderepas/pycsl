# Execution plan — remove `libcst` from PyCSL (Option 2)

> Executes `remove-libcst-from-pycsl.md`. That file is the spec; this is the
> concrete, decision-resolved execution path.

## Context

After Change A/B, the verify pipeline parses Python with the pure-Python
`pure_ast` (no CPython `compile`). The **last** native/third-party parser is
`libcst` (Rust), used in exactly one file — `Module1_Ingestor.py` — to associate
`#@` comments with the construct they annotate. Removing it makes `pure_ast` +
stdlib `tokenize` the *only* parser/lexer in PyCSL's trusted base, and — the real
win — collapses the **two-parser consistency assumption** (libcst vs `ast` must
agree on structure/line numbers) into one tree and one tokenizer.

Verified scope: `libcst` is imported only in `Module1_Ingestor.py` (`pyproject.toml:11`,
`Makefile:6` install it). Module1's public surface to preserve: `PyCSLContract`
and `Module1_Ingestor(src).process() -> List[PyCSLContract]` (callers:
`pycsl.py:148-149` deps, `pycsl.py:800-801` main; `Module3_Weaver.py:20` imports
`PyCSLContract`).

## Decisions (resolved)

- **Tree-walk via `pure_ast.parse`, not a token-only scan.** `pure_ast` now parses
  `match` (Change A/B) and the 410-file reference corpus parses 100% under it;
  Module3 already parses the same files with `pure_ast`, so Module1 matching it is
  *consistent*, not a new constraint. PEP 695 (`def f[T]`, `type X=`) loud-fails in
  both — acceptable (the file can't be verified anyway). Token-only is the
  documented fallback only if Module1 must outlive the parser's grammar coverage.
- **Differential-gated rewrite.** Keep the current libcst Module1 as
  `Module1_libcst.py` and require byte-identical `List[PyCSLContract]` before
  deleting libcst.

## Change 1 — `pure_ast.comments(source)` (additive, ~30 lines)

Add a `Comment` slots-class + `comments(source)` next to `_lex` in
`src/pycsl/pure_ast.py`, exported via `__all__` (line 30). A **separate, read-only**
`tokenize` scan (NOT through `_lex`, which discards `COMMENT` at `_SKIP`,
`pure_ast.py:434`) yielding every `COMMENT` token as
`Comment(lineno, col_offset, text, own_line, indent)`, where `own_line` is true iff
only whitespace precedes it on its line. Reuse `_lex`'s codepoint→byte `to_byte`
conversion for `col_offset` so positions match node conventions. Does not touch the
parser hot path or its trusted surface.

## Change 2 — rewrite `Module1_Ingestor.py` (drop libcst)

Keep `PyCSLContract` and `_MODULE_PREFIXES` verbatim. New `process()`:
`tree = pure_ast.parse(src)`; `coms = [own-line #@ comments]`; `return _harvest(tree, coms)`.
`_harvest` reproduces libcst's behavior exactly (each rule is a faithfulness
requirement pinned by the §Verification differential):

1. **Annotatable constructs, in source order** — walk `tree`, collect
   `(node_type, node_name, start_line, indent)` for `ClassDef`, `FunctionDef`/
   `AsyncFunctionDef`→`"FunctionDef"`, `While`, `For`/`AsyncFor`→`"For"`,
   `With`/`AsyncWith`→`"With"`, and any other statement→`"SimpleStatement"`.
   - `node_name`: class→name; function→name, **mangled `f"{enclosing_class.lower()}__{name}"`**
     when directly inside a class (enclosing class falls out of tree nesting,
     replacing libcst's `visit/leave_ClassDef`); `While`→`"<while_loop>"`,
     `For`→`"<for_loop>"`, `With`→`"<with>"`, simple stmt→`"<statement>"`.
   - **`start_line` decorator-aware**: `min(d.lineno for d in decorator_list)` if
     decorated else `node.lineno` (libcst's node starts at its first decorator —
     getting this wrong shifts `line_number` for every decorated def/class).
2. **Associate each own-line `#@` comment** at `(line, indent)` to nearest
   `prev`/`next` construct:
   - no `prev` (before first statement) → **module header**: accumulate cleaned
     text in `_module_header_contracts`; if it starts with a `_MODULE_PREFIXES`
     entry, also emit `Module`/`<module>`/`line_number=0`.
   - `indent > next.indent` (deeper than following code) → **block footer/trailing
     ghost**: attach to `prev` (block's last stmt) → `TrailingSimpleStatement`/
     `<trailing>`/`line_number=prev.start_line`. EOF-in-block (`no next`,
     `indent>0`) same; `indent==0` module-trailing → ignored (as libcst).
   - else → **leading comment of `next`** (blank lines don't break the run).
3. **Header-consumption quirk**: prepend all `_module_header_contracts` **once** to
   the **first** construct whose type ∈ {ClassDef, FunctionDef, While, For, With}
   (NOT SimpleStatement/Trailing) in source order — that construct emits *even if it
   had no own `#@`* (because `header + []` is non-empty). This is the subtlest
   behavior; rely on the differential.
4. **Emit** in libcst's depth-first source order (parents before children, by start
   line).

## Critical files
- `src/pycsl/pure_ast.py` — add `Comment` + `comments()`, export in `__all__`.
- `src/pycsl/Module1_Ingestor.py` — rewrite (drop libcst; add `_harvest`).
- `src/pycsl/Module1_libcst.py` — temporary copy of the current libcst Module1 (oracle); deleted at the end.
- `pyproject.toml` (line 11), `Makefile` (line 6) — drop `libcst` once green.

## Verification (the acceptance gate)
1. **Unit differential** — for every `test-suite/corpus/pycsl-reference/*.py` (410)
   plus the §6 edge cases, assert
   `Module1_new(src).process() == Module1_libcst(src).process()` (identical order,
   `node_type`, `node_name`, `line_number`, `contracts`). Build this as a temporary
   harness (e.g. `bin/_libcst_diff.py`).
2. **Pipeline differential** — full `bin/run-reference-tests.sh --pycsl` must match
   the pre-existing baseline failing set exactly (zero new failures), under a fixed
   `PYTHONHASHSEED` to avoid the known param-order flakiness.
3. `CMMI_AUDIT_NESTED=1 bin/cmmi-audit.sh` → 9/0; regenerate `MO15-PureAst` +
   `MO1-Module1Ingestor` mod-index (new defs).
4. Only after green: delete `Module1_libcst.py`, drop `libcst` from `pyproject.toml`
   + `Makefile`, confirm `grep -rn libcst src/pycsl` is empty, and re-run the gate.

## Edge cases the corpus/harness must cover (from spec §6)
`#@` above a decorator / between stacked decorators; module header vs later
statement; `shared`/`mutex_invariant`/`lock_order` (line-0 Module contract + prepend
quirk); trailing ghost at block end vs leading of next outer (indent discriminator);
trailing ghost at EOF in a block; `#@` separated by blank lines; async def/for/with
normalization; methods (mangling)/nested classes/nested funcs; multi-line signatures
& parenthesized `with`; `;`-separated simple statements; inline `x=1  #@ ghost`
(must be ignored via `own_line`); `else`/`elif`/`except`/`finally` block bodies.

## Risks / honest caveats
- **The harvester is in the TCB** — "which contract attaches to which node" is
  soundness-relevant. The win is small, pure-Python, auditable, single-tree logic —
  not removal from the trusted base. The differential pins "reproduce current
  observable behavior" exactly.
- **Decorator start-line** and the **header-consumption quirk** are the two most
  error-prone behaviors; both are explicitly differential-checked.
- `tokenize` remains (stdlib, pure-Python) — now the single shared lexer; dropping
  it too is a separate, larger step (deferred).
