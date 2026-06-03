# Removing the libcst Dependency from PyCSL

**Status:** ✅ Verify pipeline done; dependency retained (see scope note).
**Goal:** Eliminate `libcst` so PyCSL has **no third-party / native parser** in
its trusted base. After this change the only parser anywhere in the pipeline is
the pure-Python `pure_ast` (Change B, already delivered), and the only lexer is
the standard-library, pure-Python `tokenize` it is built on.

> **What was done.** `Module1_Ingestor.py` is rewritten libcst-free (uses
> `pure_ast.parse` + the new `pure_ast.comments()`), reproducing the libcst
> harvester's output **byte-for-byte** on all 410 reference-corpus files and 13
> targeted edge cases (decorators, between-decorators drop, async normalization,
> trailing-ghost footers, blank-line runs, semicolons, nested-class mangling
> quirk, module header/prepend, if/try drops, inline-comment ignore). The
> **verify pipeline (`src/pycsl/`) now contains no `import libcst`** — the TCB
> goal. cmmi-audit 9/0; pure_ast self-test unaffected.
>
> **Scope correction (§1 was wrong).** `libcst` is *not* used in only one file.
> Besides `Module1_Ingestor.py` (now migrated), it is imported by
> `src/pycsl_emit/` (`emitter/annotator.py`, `emitter/locator.py` — CST-based
> code rewriting) and `src/self-annotate/src/Module1_Ingestor.py` (the annotated
> self-verification mirror of Module1). So `libcst` is **kept in `pyproject.toml`
> / `Makefile`** — dropping it (§9) requires migrating `pycsl_emit` (a real
> effort: it does lossless CST transformation, not just comment harvesting) and
> re-porting the self-annotate Module1 mirror. Those are separate follow-ups; the
> soundness win (no two-parser consistency assumption in the verify path) is
> already realized.

**Why this is worth doing (TCB argument).** Today contract ingestion trusts
*two independent native parsers* — `libcst` (Rust) in `Module1` to decide where
functions/classes/loops are, and `compile`/`ast` (C) in `Module3` to build the
tree Modules 3–5 reason over — plus an unstated assumption that the two agree on
structure and line numbers. A disagreement (grammar-version skew, different
node-boundary conventions) could attach a contract to a position that doesn't
line up with the node being verified, and PyCSL would prove the wrong property
silently. Replacing `libcst` with a harvester that reads the **same tokens and
the same tree** as the parser removes the Rust extension *and* eliminates the
inter-parser consistency assumption. One tokenizer, one grammar, one notion of
"where is this construct."

This is a few days of pure-Python work, not a libcst reimplementation: PyCSL
uses almost none of libcst's lossless-CST machinery (see §1).

---

## 1. Exactly what libcst is used for (scoped)

`libcst` appears in **one file**, `Module1_Ingestor.py` (Modules 2–6 do not use
it). Its entire job there is to associate `#@` comments with the construct they
annotate and report that construct's start line. Concretely it relies on:

- `cst.parse_module` + `MetadataWrapper` + `PositionProvider` — parse and line
  numbers (`pure_ast.parse` already gives nodes with byte-accurate
  `lineno`/`end_lineno`).
- `CSTVisitor` + `visit_*` hooks + node-type checks for `Module`, `ClassDef`,
  `FunctionDef`, `While`, `For`, `With`, `SimpleStatementLine`, `IndentedBlock`
  (`pure_ast` has all these node types, `walk`, and `NodeVisitor`).
- The **one capability `ast`/`pure_ast` lacks**: standalone comment trivia —
  `EmptyLine.comment`, a statement's `leading_lines`, `Module.header`, and
  `IndentedBlock.footer`. This is *only* own-line (standalone) comments;
  Module1 never reads trailing/inline comments.

So the gap to close is narrow: **expose standalone comments with positions**,
then reproduce libcst's leading/header/footer association rules in Python.

---

## 2. Design overview

Two changes, one additive and one a rewrite:

1. **`pure_ast` gains a `comments(source)` helper** (additive, ~30 lines) that
   returns standalone comments with byte-accurate positions, indentation, and
   text — derived from the same `tokenize` pass `_lex` already runs (it
   currently *discards* comments at `_SKIP`, line 439). This is the "change in
   pure_ast." It does **not** touch the parser hot path or expand the parser's
   trusted surface; it is a separate, read-only token scan.

2. **`Module1_Ingestor.py` is rewritten** to drop `libcst` and instead use
   `pure_ast.parse` (for structure/names/positions) plus `pure_ast.comments`
   (for the `#@` lines), applying libcst's association rules itself. The
   association policy — which comment annotates which construct — is
   soundness-relevant and belongs in PyCSL's auditable code, not buried in the
   parser.

Result: `Module1.process()` returns the **same** `List[PyCSLContract]` as today;
nothing downstream changes.

---

## 3. Change 1 — `pure_ast.comments(source)`

Add to `pure_ast.py`, next to `_lex`. Reuse `_lex`'s existing `to_byte`
coordinate conversion so comment columns match node `col_offset` conventions.

```python
class Comment:
    __slots__ = ("lineno", "col_offset", "text", "own_line", "indent")
    def __init__(self, lineno, col_offset, text, own_line, indent):
        self.lineno = lineno          # 1-based, matches node.lineno
        self.col_offset = col_offset  # byte offset, matches node.col_offset
        self.text = text              # raw, e.g. "#@ requires x > 0"
        self.own_line = own_line      # True iff only whitespace precedes it
        self.indent = indent          # leading-whitespace width of the line

def comments(source):
    """All comments in `source`, with positions. `own_line` distinguishes a
    standalone comment line (libcst EmptyLine.comment) from a trailing comment
    after code (which PyCSL ignores)."""
    if isinstance(source, bytes):
        source = source.decode("utf-8")
    out = []
    g = _tokenize.generate_tokens(_io.StringIO(source).readline)
    for t in g:
        if t.type != _tokenize.COMMENT:
            continue
        before = t.line[:t.start[1]]
        own = (before.strip() == "")
        indent = len(before) - len(before.lstrip()) if own else t.start[1]
        out.append(Comment(t.start[0], t.start[1], t.string, own, indent))
    return out
```

Export it (`__all__`). That is the whole pure_ast change. (Reusing the
byte-offset conversion is optional here since Module1 only needs lines and
indentation, but keeping it consistent with `_lex` avoids surprises.)

---

## 4. Change 2 — rewrite `Module1_Ingestor.py`

Replace the libcst imports/visitor/engine. Keep `PyCSLContract` and
`_MODULE_PREFIXES` exactly as they are. New `process()`:

```python
import pure_ast as ast   # or the Change-A `pyast` seam

def process(self) -> List[PyCSLContract]:
    tree = ast.parse(self.source_code)            # one pure_ast parse
    coms = [c for c in ast.comments(self.source_code)
            if c.own_line and c.text.startswith("#@")]
    return _harvest(tree, coms)
```

`_harvest` reproduces libcst's behavior. Implement it in these steps, each a
faithfulness requirement validated by the §5 differential.

### 4.1 Build the ordered list of annotatable constructs

Walk `tree` in source order and collect, for each construct PyCSL annotates, a
record `(kind, name, start_line, indent, is_block_owner)`:

- **kinds and `node_type` strings** (must match today's output):
  `ClassDef`→`"ClassDef"`; `FunctionDef` **and** `AsyncFunctionDef`→`"FunctionDef"`;
  `While`→`"While"`; `For` **and** `AsyncFor`→`"For"`; `With` **and**
  `AsyncWith`→`"With"`; any other statement→`"SimpleStatement"`.
  (libcst has no async-specific nodes, so async variants must normalize to the
  non-async string.)
- **`node_name`:** class → its name; function → its name, **mangled
  `f"{enclosing_class.lower()}__{name}"` when directly inside a class**;
  `While`→`"<while_loop>"`, `For`→`"<for_loop>"`, `With`→`"<with>"`,
  simple statement→`"<statement>"`.
- **`start_line` (decorator-aware):** libcst's node starts at its **first
  decorator**, not at `def`/`class`. So
  `start_line = min(d.lineno for d in node.decorator_list)` if decorated, else
  `node.lineno`. Getting this wrong shifts `line_number` for every decorated
  def/class and can break Module3's matching.
- **`indent`:** the column at which the construct's line begins.
- Enclosing-class tracking for mangling falls out of tree nesting (a function
  whose parent is a `ClassDef`), replacing libcst's `visit/leave_ClassDef`
  state.

### 4.2 Associate each `#@` comment

For a standalone `#@` comment at `(line, indent)`, find `prev` = the nearest
construct/statement starting above `line` and `next` = the nearest starting
below it:

- **No `prev` (comment precedes the first statement) → module header.** Collect
  the cleaned text into `_module_header_contracts`. If it starts with one of
  `_MODULE_PREFIXES` (`shared `, `mutex_invariant `, `lock_order `), also emit a
  `PyCSLContract(node_type="Module", node_name="<module>", line_number=0, …)`.
- **`indent > next.indent` (comment is deeper than the following code) →
  trailing/footer of the block it closes.** This is libcst's
  `IndentedBlock.footer`: attach to `prev` (the block's last statement) and emit
  `node_type="TrailingSimpleStatement", node_name="<trailing>",
  line_number=prev.start_line`. Also handle the EOF case: if there is no `next`
  and `indent > 0`, it is still a trailing ghost on `prev`; if `indent == 0` it
  is a module-level trailing comment libcst keeps in the module footer and
  Module1 ignores it.
- **Otherwise → leading comment of `next`.** Attach to `next` and emit with
  `next`'s kind/name/start_line.

Comments that fall in the same leading run accumulate (source order) onto the
same construct; blank lines between `#@` lines do **not** break the run
(libcst's `leading_lines` includes blank `EmptyLine`s).

### 4.3 Reproduce the header-consumption quirk

Today `_extract_contracts_from_node` prepends **all** `_module_header_contracts`
(once) to the **first** construct of type `ClassDef/FunctionDef/While/For/With`
visited in source order — and only those five types consume it
(`SimpleStatementLine`/`IndentedBlock` do not). Because they are prepended, that
first construct emits a contract **even if it had no `#@` of its own**.
Replicate exactly: prepend the header contracts to the first such construct in
source order; that construct emits regardless of whether it had own contracts.
This is the subtlest behavior — rely on the differential to confirm it.

### 4.4 Emit

Produce `PyCSLContract`s in the **same order** libcst's depth-first source-order
walk produced them (sort emitted records by the visit order: parents before
children, by start line). Order matters if any downstream code is
order-sensitive; the differential will tell you.

---

## 5. Faithfulness oracle (the acceptance gate)

The rewrite is correct iff it reproduces the current output. Keep the old
libcst `Module1` temporarily as `Module1_libcst.py` and diff:

1. **Unit differential.** Over a corpus of contract-annotated `.py` files (the
   existing PyCSL examples/regression inputs, plus the edge cases in §6), assert
   `Module1_new(src).process() == Module1_libcst(src).process()` — i.e.
   identical `List[PyCSLContract]` (same order, same `node_type`, `node_name`,
   `line_number`, `contracts`). This is the gate.
2. **Pipeline differential.** Run the full pipeline on the corpus with the old
   and new `Module1` and assert identical IR (JSON) and WhyML. This catches any
   ordering or line-number assumption Module3 makes that the unit test misses.

Keep both modules until the corpus is green, then delete `libcst` and
`Module1_libcst.py` and drop `libcst` from dependencies/`pyproject`.

---

## 6. Edge cases the corpus must cover

These are where comment-association conventions bite:

- `#@` directly above a **decorator** (must attach to the decorated def/class
  and report the *decorator* line).
- multiple stacked decorators; `#@` between two decorators.
- `#@` above the **first** statement (module header) vs. above a later one.
- module-level `shared`/`mutex_invariant`/`lock_order` (line-0 Module contract
  *and* the prepend-to-first-construct behavior).
- **trailing ghost** as the last line of a loop/if/with body (footer) vs. a
  leading comment of the next outer statement — the indentation discriminator.
- trailing ghost at **end of file** inside a block.
- `#@` separated from its construct by blank lines (still attaches).
- **async** `def`/`for`/`with` (must normalize to `FunctionDef`/`For`/`With`).
- methods inside a class (name mangling `class.lower()__method`); nested
  classes; functions nested in functions.
- multi-line `def` signatures and parenthesized `with` items (start line is the
  first line).
- semicolon-separated simple statements on one line.
- a `#@` that is a **trailing inline** comment after code (`x = 1  #@ ghost`) —
  libcst stores this in `TrailingWhitespace`, which Module1 never reads, so the
  new harvester must **ignore** it (`own_line` filter).
- `else`/`elif`/`except`/`finally` clauses (their bodies are blocks too).

---

## 7. TCB accounting and honest caveats

- **The harvester is in the TCB.** "Which contract attaches to which node" is
  soundness-relevant: a misassociation verifies the wrong property. The win is
  that it is small, pure-Python, auditable, and driven by the same tree/tokens
  as the verifier — not that it is outside the trusted base.
- **`tokenize` remains**, but it is stdlib, pure Python, and now the *single*
  shared lexer (one trusted lexer instead of two trusted parsers). Hand-writing
  a lexer to drop even `tokenize` is a separate, larger step you can defer.
- **Association is convention, not truth.** Even libcst makes choices about
  comment ownership. The spec here is therefore "reproduce PyCSL's current
  observable behavior," which §5's differential pins down precisely — not "match
  some abstract ideal."
- **Grammar-coverage coupling.** Using `pure_ast.parse` for structure means
  `Module1` now fails (loudly, `PyCSLSyntaxError`) on constructs `pure_ast`
  doesn't parse (`match`, PEP 695). This is consistent with the post-Change-A
  pipeline, which already fails on them. If you need `Module1` to keep working
  on those (as libcst did), implement §4.1 as a **token-only** scan
  (keywords + `NAME` + INDENT/DEDENT tracking) instead of walking the tree —
  same association logic, no dependency on the parser's grammar coverage. Treat
  this as the fallback design, not the default.

---

## 8. Out of scope

- Modules 2–6 (unchanged; they already consume `pure_ast` after Change A).
- Extending `pure_ast`'s grammar (`match`, PEP 695) — tracked in that file's
  COVERAGE MANIFEST.
- Sharing a single parse between `Module1` and `Module3` (a possible later
  optimization; currently each parses independently, which is fine).

---

## 9. Done when

- `pure_ast.comments(source)` exists and is exported.
- `Module1_Ingestor.py` imports no `libcst`; `libcst` is removed from project
  dependencies.
- The §5 unit and pipeline differentials are byte-identical to the libcst
  baseline across the corpus (with any deliberately excluded files listed and
  justified).
- No third-party or native parser remains in PyCSL's trusted base; the only
  lexer is stdlib `tokenize` and the only parser is `pure_ast`.
