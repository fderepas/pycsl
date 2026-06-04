"""Module 1 — contract ingestion (libcst-free).

Harvests `#@` annotations and associates each with the construct it annotates,
using the same pure-Python front-end the rest of the pipeline uses
(`pure_ast.parse` for structure/names/positions + `pure_ast.comments` for the
standalone comment trivia `ast` does not retain). This replaces the former
libcst CST visitor; `process()` returns the identical `List[PyCSLContract]`.

The comment-association policy here is soundness-relevant (it decides which
contract attaches to which node), so it lives in PyCSL's auditable code rather
than a third-party parser. Behavior is pinned byte-for-byte against the former
libcst implementation by the differential in `bin/_libcst_diff.py`.
"""
from __future__ import annotations

import re
import pure_ast as ast
from dataclasses import dataclass, field
from typing import List, Optional

from errors import PyCSLParseError

_MODULE_PREFIXES: tuple = ('shared ', 'mutex_invariant ', 'lock_order ')


@dataclass
class PyCSLContract:
    """A collection of PyCSL contracts attached to a specific Python node."""
    node_type: str          # e.g., 'FunctionDef' or 'While'
    node_name: str          # e.g., 'add_positive' or '<while_loop>'
    line_number: int        # where the node starts (for error reporting)
    contracts: List[str] = field(default_factory=list)


# Node types that own a contract block (the five libcst `visit_*` had + the
# IndentedBlock footer). The first of these in source order consumes the module
# header (see `_emit`).
_HEADER_CONSUMERS = {"ClassDef", "FunctionDef", "While", "For", "With"}


class _Target:
    """One statement in source order, as the harvester sees it."""
    __slots__ = ("node", "node_type", "node_name", "start_line", "report_line",
                 "indent", "child_suites", "leading", "footer")

    def __init__(self, node, node_type, node_name, start_line, report_line, indent):
        self.node = node
        self.node_type = node_type      # emitted type, or None for an un-annotated
                                        # compound (If/Try/Match/…)
        self.node_name = node_name
        self.start_line = start_line    # decorator-aware (for comment association)
        self.report_line = report_line  # node.lineno — the emitted line_number
        self.indent = indent            # column where the construct begins
        self.child_suites = []          # list of suites, each a list of _Target
        self.leading: List[str] = []    # assigned leading #@ contracts
        self.footer: List[str] = []     # footer #@ contracts of this node's last child suite


def _clean(comment_text: str) -> str:
    return comment_text[2:].strip()


# Block-header `#@` bodies (own-line). Indentation is significant: clauses sit
# exactly 4 spaces deeper than the header. Both `act NAME:` (guarded cases) and
# `happy NAME:` (module-level HAPPY meta-property) fold identically. See
# `_Harvester._fold_blocks`.
_ACT_HDR = re.compile(r"^\s*act\s+(\w+)\s*:\s*$")
_HAPPY_HDR = re.compile(r"^\s*happy\s+(\w+)\s*:\s*$")
_BLOCK_HDRS = (("act", _ACT_HDR), ("happy", _HAPPY_HDR))


def _match_block_hdr(line: str):
    """Return `(keyword, name)` if `line` opens an `act`/`happy` block, else None."""
    for kw, rx in _BLOCK_HDRS:
        m = rx.match(line)
        if m:
            return kw, m.group(1)
    return None


def _indent_width(body: str) -> int:
    """Leading-whitespace width of an `#@` body; tabs are rejected (spaces only)."""
    lead = body[: len(body) - len(body.lstrip())]
    if "\t" in lead:
        raise PyCSLParseError(
            "tabs are not allowed in `act` block indentation; use 4 spaces",
            stage="Module1")
    return len(lead)


class Module1_Ingestor:
    """Ingests source code and extracts `#@` annotations as PyCSLContracts."""

    def __init__(self, source_code: str) -> None:
        self.source_code = source_code

    def process(self) -> List[PyCSLContract]:
        tree = ast.parse(self.source_code)
        coms = [c for c in ast.comments(self.source_code)
                if c.own_line and c.text.startswith("#@")]
        return _Harvester(coms).run(tree)


class _Harvester:
    def __init__(self, comments: List[ast.Comment]) -> None:
        self._coms = sorted(comments, key=lambda c: c.lineno)
        self._out: List[PyCSLContract] = []
        self._module_header: List[str] = []
        self._module_contracts: List[str] = []
        self._header_consumed = False
        self._flat: List[_Target] = []          # all targets, source order
        self._dec_ranges: List[tuple] = []      # [first_decorator, def) spans — #@ here is dropped
        # Mirrors libcst's `_current_class`: set on entering a ClassDef, reset to
        # None (NOT the outer class) on leaving — so a method after a *nested*
        # class is unmangled. Replicated for byte-identical node_name output.
        self._cur_class: Optional[str] = None

    def _make(self, node):
        """Build one _Target (+ its child suite node-lists), using the stateful
        `_cur_class` for method-name mangling and normalizing async variants."""
        t = type(node).__name__
        decs = getattr(node, "decorator_list", None) or []
        report = node.lineno
        start = min([d.lineno for d in decs], default=report)
        if decs and start < report:
            self._dec_ranges.append((start, report))   # decorator whitespace → drop #@
        indent = getattr(node, "col_offset", 0)
        mk = lambda nt, nm: _Target(node, nt, nm, start, report, indent)
        if t == "ClassDef":
            return mk("ClassDef", node.name), [list(node.body)]
        if t in ("FunctionDef", "AsyncFunctionDef"):
            nm = f"{self._cur_class.lower()}__{node.name}" if self._cur_class else node.name
            return mk("FunctionDef", nm), [list(node.body)]
        if t == "While":
            return mk("While", "<while_loop>"), [list(node.body), list(node.orelse)]
        if t in ("For", "AsyncFor"):
            return mk("For", "<for_loop>"), [list(node.body), list(node.orelse)]
        if t in ("With", "AsyncWith"):
            return mk("With", "<with>"), [list(node.body)]
        if t == "If":
            return mk(None, None), [list(node.body), list(node.orelse)]
        if t in ("Try", "TryStar"):
            suites = [list(node.body)] + [list(h.body) for h in node.handlers] \
                + [list(node.orelse), list(node.finalbody)]
            return mk(None, None), suites
        if t == "Match":
            return mk(None, None), [list(c.body) for c in node.cases]
        return mk("SimpleStatement", "<statement>"), []   # simple statement

    # --- build the target tree (and flat source-order list) ---------------
    def _build(self, stmt_nodes) -> List[_Target]:
        suite = []
        for s in stmt_nodes:
            tgt, child_suite_nodes = self._make(s)
            self._flat.append(tgt)
            if tgt.node_type == "ClassDef":
                self._cur_class = tgt.node_name            # enter class
                tgt.child_suites = [self._build(cs) for cs in child_suite_nodes]
                self._cur_class = None                     # leave → None (libcst quirk)
            else:
                tgt.child_suites = [self._build(cs) for cs in child_suite_nodes]
            suite.append(tgt)
        return suite

    def run(self, tree) -> List[PyCSLContract]:
        top = self._build(tree.body)
        self._flat.sort(key=lambda t: t.start_line)
        self._assign()
        if self._module_contracts:
            self._out.append(PyCSLContract("Module", "<module>", 0, self._module_contracts))
        self._emit_suite(top)
        return self._out

    # --- assign each own-line #@ comment to exactly one slot --------------
    def _assign(self) -> None:
        starts = [t.start_line for t in self._flat]   # ascending
        import bisect
        for c in self._coms:
            # #@ inside decorator whitespace ([first_decorator, def)) is invisible
            # to libcst's leading_lines — drop it.
            if any(lo <= c.lineno < hi for lo, hi in self._dec_ranges):
                continue
            clean = _clean(c.text)
            raw = c.text[2:].rstrip()   # body with indentation kept (for `act` folding)
            # nearest target strictly above / below this comment line
            j = bisect.bisect_left(starts, c.lineno)
            prev = self._flat[j - 1] if j > 0 else None
            nxt = self._flat[j] if j < len(self._flat) else None
            if prev is None:
                # module header (before the first statement) — also the leading
                # contracts of the first statement, which `_emit_target` prepends.
                # Stored raw (indent kept) so `act` blocks there fold too.
                self._module_header.append(raw)
                if any(clean.startswith(p) for p in _MODULE_PREFIXES):
                    self._module_contracts.append(clean)
            elif (nxt is not None and c.indent > nxt.indent) or \
                 (nxt is None and c.indent > 0):
                # footer / trailing ghost of the block whose last stmt is `prev`
                prev.footer.append(clean)
            elif nxt is None:
                pass   # module-level trailing comment (indent 0) → ignored, as libcst
            else:
                nxt.leading.append(raw)   # raw (indent kept); normalized at emit

    # --- block folding (engaged ONLY when an `act`/`happy` header is present) -
    def _normalize_leading(self, raw_lines: List[str]) -> List[str]:
        """Turn a target's raw (indent-preserved) leading bodies into contract
        strings. With no block header present this is `[ln.strip() …]` — exactly
        what the old `_clean` produced, so non-block contracts are byte-identical.
        Only an `act`/`happy` header engages the folder."""
        if not any(_match_block_hdr(ln) for ln in raw_lines):
            return [ln.strip() for ln in raw_lines]
        return self._fold_blocks(raw_lines)

    def _fold_blocks(self, raw_lines: List[str]) -> List[str]:
        """Fold each `act NAME:` / `happy NAME:` header + its 4-space-indented body
        lines into one contract string `<kw> NAME: <clause> <clause> …`. Strict and
        fail-loud: a body line must be indented exactly 4 spaces under the header; any
        other indent, a tab, or an empty body is a hard `PyCSLParseError` (never
        reinterpreted)."""
        out: List[str] = []
        i, n = 0, len(raw_lines)
        while i < n:
            hdr = _match_block_hdr(raw_lines[i])
            if not hdr:
                out.append(raw_lines[i].strip())
                i += 1
                continue
            kw, name = hdr
            blk_indent = _indent_width(raw_lines[i])
            i += 1
            clauses: List[str] = []
            while i < n and raw_lines[i].strip():
                body_indent = _indent_width(raw_lines[i])
                if body_indent <= blk_indent:
                    break                       # block ends (next top-level contract)
                if body_indent != blk_indent + 4:
                    raise PyCSLParseError(
                        f"`{kw} {name}`: body must be indented exactly 4 spaces under "
                        f"`{kw}` (got {body_indent - blk_indent})", stage="Module1")
                clauses.append(raw_lines[i].strip())
                i += 1
            if not clauses:
                raise PyCSLParseError(f"`{kw} {name}`: empty body", stage="Module1")
            out.append(f"{kw} {name}: " + " ".join(clauses))
        return out

    # --- emit in libcst pre-order: node, then its block footer, then body --
    def _emit_suite(self, targets: List[_Target]) -> None:
        for tgt in targets:
            self._emit_target(tgt)
            for child in tgt.child_suites:
                if child:
                    self._emit_block_footer(child[-1])
                self._emit_suite(child)

    def _emit_target(self, tgt: _Target) -> None:
        contracts: List[str] = []
        # First header-consumer in source order prepends the module header once,
        # and emits even if it had no own contracts.
        if (tgt.node_type in _HEADER_CONSUMERS and not self._header_consumed
                and self._module_header):
            contracts.extend(self._normalize_leading(self._module_header))
            self._header_consumed = True
        contracts.extend(self._normalize_leading(tgt.leading))
        if contracts and tgt.node_type is not None:
            self._out.append(PyCSLContract(tgt.node_type, tgt.node_name,
                                           tgt.report_line, contracts))

    def _emit_block_footer(self, last_stmt: _Target) -> None:
        if last_stmt.footer:
            self._out.append(PyCSLContract("TrailingSimpleStatement", "<trailing>",
                                           last_stmt.report_line, list(last_stmt.footer)))
