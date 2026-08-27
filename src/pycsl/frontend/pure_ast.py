"""
pure_ast — a pure-Python reimplementation of the standard library ``ast`` module.

The real ``ast`` module is split in two: the *node hierarchy* and the *parser*
live in C (``_ast`` / ``Python-ast.c`` and CPython's PEG parser), while the
helper layer (``Lib/ast.py``) is already Python.  This module reimplements the
whole public surface in pure Python:

  * the complete AST node class hierarchy (``AST``, ``Module``, ``BinOp`` ...),
    defined from an ASDL-derived table rather than imported from ``_ast``;
  * every helper: ``dump``, ``literal_eval``, ``walk``, ``copy_location``,
    ``fix_missing_locations``, ``increment_lineno``, ``get_docstring``,
    ``get_source_segment``, ``iter_fields``, ``iter_child_nodes``,
    ``NodeVisitor``, ``NodeTransformer`` and ``unparse``;
  * the deprecated ``Num``/``Str``/``Bytes``/``NameConstant``/``Ellipsis``
    compatibility shims;
  * a ``main()`` CLI mirroring ``python -m ast``.

``parse`` is also pure Python: it tokenizes with the standard library's
pure-Python ``tokenize`` module (which does **not** use ``compile``) and runs a
hand-written recursive-descent parser that builds the node classes defined
below.  Unsupported constructs raise ``PyCSLSyntaxError`` instead of producing
an incorrect tree.  See the COVERAGE MANIFEST below and ``parse``.

Targets the node schema and grammar of Python 3.12.
"""

import sys as _sys

__all__ = [
    # core
    'AST', 'parse', 'dump', 'copy_location', 'fix_missing_locations',
    'increment_lineno', 'iter_fields', 'iter_child_nodes', 'get_docstring',
    'get_source_segment', 'walk', 'NodeVisitor', 'NodeTransformer',
    'literal_eval', 'unparse', 'PyCSLSyntaxError',
    # standalone-comment harvesting (used by Module1 contract ingestion)
    'comments', 'Comment',
    # compile flags
    'PyCF_ONLY_AST', 'PyCF_TYPE_COMMENTS', 'PyCF_ALLOW_TOP_LEVEL_AWAIT',
]

# Compile-flag constants (values fixed by CPython's Include/cpython/compile.h).
PyCF_ONLY_AST = 0x0400
PyCF_TYPE_COMMENTS = 0x1000
PyCF_ALLOW_TOP_LEVEL_AWAIT = 0x2000

# ===========================================================================
# COVERAGE MANIFEST  (parser; the node layer & helpers are complete)
# ---------------------------------------------------------------------------
# Validated by differential test against the stdlib ``ast`` on the CPython
# 3.12 standard library: 512 / 517 files parse to a byte-identical
# ``ast.dump(...)`` (structure), 0 mismatches, 0 crashes.  The remaining 5
# files use constructs that are intentionally deferred and raise
# ``PyCSLSyntaxError`` (loud failure, never a wrong tree).
#
# IMPLEMENTED
#   - modes: 'exec', 'eval', 'single'
#   - all literals: int/float/complex (underscores, 0x/0o/0b), str/bytes with
#     full escape decoding and implicit concatenation, True/False/None/...
#   - f-strings (PEP 701): text, {expr}, conversions (!r/!s/!a), format specs
#     incl. nested fields, self-documenting {x=}, raw f-strings
#   - all operators with correct precedence/associativity (incl. ** and chained
#     comparisons), bool ops, unary, walrus :=, conditional expr, lambda
#   - calls (*, **, keywords, genexp arg), attribute/subscript/slice trailers
#   - list/set/dict displays and comprehensions (incl. async), starred elements
#   - await / yield / yield from
#   - statements: expr, assign / augmented / annotated, pass/break/continue,
#     return, raise (from), assert, global, nonlocal, del, import, from-import
#     (relative, *, aliases), if/elif/else, while/else, for/else, with (incl.
#     parenthesized items), try/except/except*/else/finally
#   - def / async def with full parameters (posonly /, *args, kw-only, **kw,
#     annotations, defaults, return annotation) and decorators
#   - class def (bases, keywords, decorators)
#   - correct expression context (Load/Store/Del) on all targets
#
# IMPLEMENTED
#   - match / case statements                        (PEP 634): literal,
#     singleton, capture, wildcard, value (dotted), OR (`|`), as-binding, and
#     sequence patterns (`[...]`/`(...)` with `*`-star). Class `C(...)` and
#     mapping `{...}` patterns raise PyCSLSyntaxError (loud-fail).
#
# NOT YET IMPLEMENTED  (each raises PyCSLSyntaxError with a clear message)
        #    - type-parameter syntax  def f[T] / class C[T]    (PEP 695, IMPLEMENTED)
#    - the `type X = ...` alias statement              (PEP 695, IMPLEMENTED)
#   - type comments (# type: ...)  -> parse(type_comments=True) raises
#   - class / mapping match patterns                 (PEP 634, see above)
#
# POSITIONS (match CPython's ``ast``)
#   - ``col_offset`` / ``end_col_offset`` are UTF-8 *byte* offsets (``_lex``
#     converts ``tokenize``'s codepoint columns to byte columns per line).
#   - Compound statements (def/class/if/while/for/with/try/match) end at their
#     last (deepest) body element, not the trailing NEWLINE/DEDENT
#     (``_Parser._fin_block``). No known position-fidelity gaps remain on the
#     supported grammar.
#
# The stdlib differential is the acceptance gate; run
# ``python pure_ast.py --self-test`` under CPython 3.12 (the targeted schema;
# a different interpreter's ``ast`` will report spurious diffs).
# ===========================================================================


# ---------------------------------------------------------------------------
# Node hierarchy
# ---------------------------------------------------------------------------

class AST:
    """Base class of every node, mirroring ``_ast.AST``."""
    _fields = ()
    _attributes = ()

    def __init__(self, *args, **kwargs):
        cls = type(self)
        if len(args) > len(cls._fields):
            raise TypeError(
                f"{cls.__name__} constructor takes at most "
                f"{len(cls._fields)} positional argument"
                f"{'' if len(cls._fields) == 1 else 's'}"
            )
        for name, value in zip(cls._fields, args):
            setattr(self, name, value)
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __repr__(self):
        return f"<{type(self).__module__}.{type(self).__qualname__} object>"


# ASDL-derived schema: name -> (base-category-name, fields, attributes).
# Generated from the live node definitions of the running interpreter.
_NODE_SPEC = {
    # --- abstract base categories (parent is AST) -------------------------
    'mod': ('AST', (), ()),
    'stmt': ('AST', (), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'expr': ('AST', (), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'expr_context': ('AST', (), ()),
    'boolop': ('AST', (), ()),
    'operator': ('AST', (), ()),
    'unaryop': ('AST', (), ()),
    'cmpop': ('AST', (), ()),
    'slice': ('AST', (), ()),
    'excepthandler': ('AST', (), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'pattern': ('AST', (), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'type_ignore': ('AST', (), ()),
    'type_param': ('AST', (), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'comprehension': ('AST', ('target', 'iter', 'ifs', 'is_async'), ()),
    'arguments': ('AST', ('posonlyargs', 'args', 'vararg', 'kwonlyargs', 'kw_defaults', 'kwarg', 'defaults'), ()),
    'arg': ('AST', ('arg', 'annotation', 'type_comment'), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'keyword': ('AST', ('arg', 'value'), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'alias': ('AST', ('name', 'asname'), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'withitem': ('AST', ('context_expr', 'optional_vars'), ()),
    'match_case': ('AST', ('pattern', 'guard', 'body'), ()),
    # --- mod --------------------------------------------------------------
    'Module': ('mod', ('body', 'type_ignores'), ()),
    'Interactive': ('mod', ('body',), ()),
    'Expression': ('mod', ('body',), ()),
    'FunctionType': ('mod', ('argtypes', 'returns'), ()),
    'Suite': ('mod', (), ()),
    # --- stmt -------------------------------------------------------------
    'FunctionDef': ('stmt', ('name', 'args', 'body', 'decorator_list', 'returns', 'type_comment', 'type_params'), None),
    'AsyncFunctionDef': ('stmt', ('name', 'args', 'body', 'decorator_list', 'returns', 'type_comment', 'type_params'), None),
    'ClassDef': ('stmt', ('name', 'bases', 'keywords', 'body', 'decorator_list', 'type_params'), None),
    'Return': ('stmt', ('value',), None),
    'Delete': ('stmt', ('targets',), None),
    'Assign': ('stmt', ('targets', 'value', 'type_comment'), None),
    'AugAssign': ('stmt', ('target', 'op', 'value'), None),
    'AnnAssign': ('stmt', ('target', 'annotation', 'value', 'simple'), None),
    'For': ('stmt', ('target', 'iter', 'body', 'orelse', 'type_comment'), None),
    'AsyncFor': ('stmt', ('target', 'iter', 'body', 'orelse', 'type_comment'), None),
    'While': ('stmt', ('test', 'body', 'orelse'), None),
    'If': ('stmt', ('test', 'body', 'orelse'), None),
    'With': ('stmt', ('items', 'body', 'type_comment'), None),
    'AsyncWith': ('stmt', ('items', 'body', 'type_comment'), None),
    'Match': ('stmt', ('subject', 'cases'), None),
    'Raise': ('stmt', ('exc', 'cause'), None),
    'Try': ('stmt', ('body', 'handlers', 'orelse', 'finalbody'), None),
    'TryStar': ('stmt', ('body', 'handlers', 'orelse', 'finalbody'), None),
    'Assert': ('stmt', ('test', 'msg'), None),
    'Import': ('stmt', ('names',), None),
    'ImportFrom': ('stmt', ('module', 'names', 'level'), None),
    'Global': ('stmt', ('names',), None),
    'Nonlocal': ('stmt', ('names',), None),
    'Expr': ('stmt', ('value',), None),
    'Pass': ('stmt', (), None),
    'Break': ('stmt', (), None),
    'Continue': ('stmt', (), None),
    'TypeAlias': ('stmt', ('name', 'type_params', 'value'), None),
    # --- expr -------------------------------------------------------------
    'BoolOp': ('expr', ('op', 'values'), None),
    'NamedExpr': ('expr', ('target', 'value'), None),
    'BinOp': ('expr', ('left', 'op', 'right'), None),
    'UnaryOp': ('expr', ('op', 'operand'), None),
    'Lambda': ('expr', ('args', 'body'), None),
    'IfExp': ('expr', ('test', 'body', 'orelse'), None),
    'Dict': ('expr', ('keys', 'values'), None),
    'Set': ('expr', ('elts',), None),
    'ListComp': ('expr', ('elt', 'generators'), None),
    'SetComp': ('expr', ('elt', 'generators'), None),
    'DictComp': ('expr', ('key', 'value', 'generators'), None),
    'GeneratorExp': ('expr', ('elt', 'generators'), None),
    'Await': ('expr', ('value',), None),
    'Yield': ('expr', ('value',), None),
    'YieldFrom': ('expr', ('value',), None),
    'Compare': ('expr', ('left', 'ops', 'comparators'), None),
    'Call': ('expr', ('func', 'args', 'keywords'), None),
    'FormattedValue': ('expr', ('value', 'conversion', 'format_spec'), None),
    'JoinedStr': ('expr', ('values',), None),
    'Constant': ('expr', ('value', 'kind'), None),
    'Attribute': ('expr', ('value', 'attr', 'ctx'), None),
    'Subscript': ('expr', ('value', 'slice', 'ctx'), None),
    'Starred': ('expr', ('value', 'ctx'), None),
    'Name': ('expr', ('id', 'ctx'), None),
    'List': ('expr', ('elts', 'ctx'), None),
    'Tuple': ('expr', ('elts', 'ctx'), None),
    'Slice': ('expr', ('lower', 'upper', 'step'), None),
    # legacy slice helpers
    'Index': ('slice', (), ()),
    'ExtSlice': ('slice', (), ()),
    # --- expr_context -----------------------------------------------------
    'Load': ('expr_context', (), ()),
    'Store': ('expr_context', (), ()),
    'Del': ('expr_context', (), ()),
    'AugLoad': ('expr_context', (), ()),
    'AugStore': ('expr_context', (), ()),
    'Param': ('expr_context', (), ()),
    # --- boolop / operator / unaryop / cmpop ------------------------------
    'And': ('boolop', (), ()), 'Or': ('boolop', (), ()),
    'Add': ('operator', (), ()), 'Sub': ('operator', (), ()),
    'Mult': ('operator', (), ()), 'MatMult': ('operator', (), ()),
    'Div': ('operator', (), ()), 'Mod': ('operator', (), ()),
    'Pow': ('operator', (), ()), 'LShift': ('operator', (), ()),
    'RShift': ('operator', (), ()), 'BitOr': ('operator', (), ()),
    'BitXor': ('operator', (), ()), 'BitAnd': ('operator', (), ()),
    'FloorDiv': ('operator', (), ()),
    'Invert': ('unaryop', (), ()), 'Not': ('unaryop', (), ()),
    'UAdd': ('unaryop', (), ()), 'USub': ('unaryop', (), ()),
    'Eq': ('cmpop', (), ()), 'NotEq': ('cmpop', (), ()),
    'Lt': ('cmpop', (), ()), 'LtE': ('cmpop', (), ()),
    'Gt': ('cmpop', (), ()), 'GtE': ('cmpop', (), ()),
    'Is': ('cmpop', (), ()), 'IsNot': ('cmpop', (), ()),
    'In': ('cmpop', (), ()), 'NotIn': ('cmpop', (), ()),
    # --- excepthandler ----------------------------------------------------
    'ExceptHandler': ('excepthandler', ('type', 'name', 'body'), None),
    # --- pattern ----------------------------------------------------------
    'MatchValue': ('pattern', ('value',), None),
    'MatchSingleton': ('pattern', ('value',), None),
    'MatchSequence': ('pattern', ('patterns',), None),
    'MatchMapping': ('pattern', ('keys', 'patterns', 'rest'), None),
    'MatchClass': ('pattern', ('cls', 'patterns', 'kwd_attrs', 'kwd_patterns'), None),
    'MatchStar': ('pattern', ('name',), None),
    'MatchAs': ('pattern', ('pattern', 'name'), None),
    'MatchOr': ('pattern', ('patterns',), None),
    # --- type_ignore / type_param ----------------------------------------
    'TypeIgnore': ('type_ignore', ('lineno', 'tag'), ()),
    'TypeVar': ('type_param', ('name', 'bound'), None),
    'ParamSpec': ('type_param', ('name',), None),
    'TypeVarTuple': ('type_param', ('name',), None),
}

# Attributes shared by the located node families. ``None`` in the table above
# means "inherit this family's standard attribute set".
_LOCATED = ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')


# Optional fields (ASDL ``?`` markers): these carry a class-level default of
# ``None`` so that constructing a node without them leaves the attribute
# readable, and so that ``dump`` can omit them when unset -- matching CPython.
_OPTIONAL_FIELDS = {
    'AnnAssign': ('value',),
    'Assert': ('msg',),
    'Assign': ('type_comment',),
    'AsyncFor': ('type_comment',),
    'AsyncFunctionDef': ('returns', 'type_comment'),
    'AsyncWith': ('type_comment',),
    'Constant': ('kind',),
    'ExceptHandler': ('type', 'name'),
    'For': ('type_comment',),
    'FormattedValue': ('format_spec',),
    'FunctionDef': ('returns', 'type_comment'),
    'ImportFrom': ('module', 'level'),
    'MatchAs': ('pattern', 'name'),
    'MatchMapping': ('rest',),
    'MatchStar': ('name',),
    'Raise': ('exc', 'cause'),
    'Return': ('value',),
    'Slice': ('lower', 'upper', 'step'),
    'TypeVar': ('bound',),
    'With': ('type_comment',),
    'Yield': ('value',),
    'alias': ('asname',),
    'arg': ('annotation', 'type_comment'),
    'arguments': ('vararg', 'kwarg'),
    'keyword': ('arg',),
    'match_case': ('guard',),
    'withitem': ('optional_vars',),
}


def _build_nodes(namespace):
    """Create every node class from ``_NODE_SPEC`` into ``namespace``."""
    created = {'AST': AST}

    def make(name):
        if name in created:
            return created[name]
        base_name, fields, attributes = _NODE_SPEC[name]
        base = created.get(base_name) or make(base_name)
        if attributes is None:
            attributes = _LOCATED
        body = {'_fields': tuple(fields),
                '_attributes': tuple(attributes),
                '__module__': 'ast'}
        for opt in _OPTIONAL_FIELDS.get(name, ()):
            body[opt] = None
        cls = type(name, (base,), body)
        created[name] = cls
        namespace[name] = cls
        return cls

    for node_name in _NODE_SPEC:
        make(node_name)


_build_nodes(globals())


# ---------------------------------------------------------------------------
# Deprecated Constant compatibility shims (Num/Str/Bytes/NameConstant/Ellipsis)
# ---------------------------------------------------------------------------

# Expose ``Constant.n`` / ``Constant.s`` as aliases of ``.value`` (back-compat).
def _const_value_getter(self):
    return self.value


def _const_value_setter(self, value):
    self.value = value


Constant.n = property(_const_value_getter, _const_value_setter)  # noqa: F821
Constant.s = property(_const_value_getter, _const_value_setter)  # noqa: F821


class _ABC(type):
    """Metaclass making ``isinstance(Constant(x), Num)`` & friends work."""
    def __instancecheck__(cls, inst):
        if not isinstance(inst, Constant):  # noqa: F821
            return False
        if cls in _const_types:
            try:
                value = inst.value
            except AttributeError:
                return False
            return (isinstance(value, _const_types[cls]) and
                    not isinstance(value, _const_types_not.get(cls, ())))
        return type.__instancecheck__(cls, inst)


def _new(cls, *args, **kwargs):
    if cls in _const_types:
        return Constant(*args, **kwargs)  # noqa: F821
    return Constant.__new__(cls, *args, **kwargs)  # noqa: F821


class Num(Constant, metaclass=_ABC):  # noqa: F821
    _fields = ('n',)
    __new__ = _new


class Str(Constant, metaclass=_ABC):  # noqa: F821
    _fields = ('s',)
    __new__ = _new


class Bytes(Constant, metaclass=_ABC):  # noqa: F821
    _fields = ('s',)
    __new__ = _new


class NameConstant(Constant, metaclass=_ABC):  # noqa: F821
    __new__ = _new


class Ellipsis(Constant, metaclass=_ABC):  # noqa: F821
    _fields = ()

    def __new__(cls, *args, **kwargs):
        if cls is Ellipsis:
            return Constant(..., *args, **kwargs)  # noqa: F821
        return Constant.__new__(cls, *args, **kwargs)  # noqa: F821


_const_types = {
    Num: (int, float, complex),
    Str: (str,),
    Bytes: (bytes,),
    NameConstant: (type(None), bool),
    Ellipsis: (type(...),),
}
_const_types_not = {
    Num: (bool,),
}

__all__ += ['Num', 'Str', 'Bytes', 'NameConstant', 'Ellipsis']


# ---------------------------------------------------------------------------
# Parsing — pure-Python tokenizer + recursive-descent parser (NO ``compile``).
# Tokens come from the standard library's pure-Python ``tokenize`` module; the
# grammar is implemented directly below.  Constructs that are not yet handled
# raise ``PyCSLSyntaxError`` (never a silently-wrong tree).  See the COVERAGE
# MANIFEST near the top of this module.
# ---------------------------------------------------------------------------

import tokenize as _tokenize
import io as _io
import keyword as _keyword
import unicodedata as _unicodedata

_g = globals()


def _N(name):
    return _g[name]


class PyCSLSyntaxError(SyntaxError):
    pass


_SOFT = {"match", "case", "type", "_"}

# ----------------------------------------------------------------------------
# Token stream
# ----------------------------------------------------------------------------

_SKIP = {_tokenize.COMMENT, _tokenize.NL, _tokenize.ENCODING}


class _Tok:
    __slots__ = ("type", "string", "start", "end")

    def __init__(self, t):
        self.type = t.type
        self.string = t.string
        self.start = t.start
        self.end = t.end

    def __repr__(self):
        return f"Tok({_tokenize.tok_name[self.type]}, {self.string!r}, {self.start})"


def _lex(source):
    if isinstance(source, bytes):
        source = source.decode("utf-8")
    if not source.endswith("\n"):
        source = source + "\n"
    # `tokenize` reports columns as CODEPOINT indices into each line, but
    # CPython's `ast` reports `col_offset`/`end_col_offset` as UTF-8 BYTE
    # offsets. Convert token coordinates once here so every node position
    # derived from them (via `_Parser._fin`/`_fin_pos`) is byte-based and
    # matches stdlib `ast` on non-ASCII source. ASCII lines (the common case)
    # have byte == codepoint, so they hit a no-op fast-path.
    lines = source.split("\n")
    ascii_line = [ln.isascii() for ln in lines]

    def to_byte(pos):
        row, ccol = pos
        if ccol == 0 or row < 1 or row > len(lines) or ascii_line[row - 1]:
            return pos
        return (row, len(lines[row - 1][:ccol].encode("utf-8")))

    toks = []
    g = _tokenize.generate_tokens(_io.StringIO(source).readline)
    for t in g:
        if t.type in _SKIP:
            continue
        tk = _Tok(t)
        tk.start = to_byte(tk.start)
        tk.end = to_byte(tk.end)
        toks.append(tk)
    return toks


class Comment:
    """A source comment with position (see ``comments``)."""
    __slots__ = ("lineno", "col_offset", "text", "own_line", "indent")

    def __init__(self, lineno, col_offset, text, own_line, indent):
        self.lineno = lineno          # 1-based, matches node.lineno
        self.col_offset = col_offset  # UTF-8 byte offset, matches node.col_offset
        self.text = text              # raw, e.g. "#@ requires x > 0"
        self.own_line = own_line      # True iff only whitespace precedes it on the line
        self.indent = indent          # leading-whitespace width (own-line) / start col

    def __repr__(self):
        return (f"Comment(line={self.lineno}, own_line={self.own_line}, "
                f"indent={self.indent}, text={self.text!r})")


def comments(source):
    """Every comment in `source`, with positions — a separate, read-only token
    scan (``_lex`` discards ``COMMENT`` via ``_SKIP``). `own_line` is True iff
    only whitespace precedes the comment on its physical line (the libcst
    ``EmptyLine.comment`` standalone case); a trailing/inline comment after code
    is `own_line=False`. `col_offset` is a UTF-8 byte offset (matching
    ``node.col_offset``); `indent` is the line's leading-whitespace width for an
    own-line comment, else the comment's start column."""
    if isinstance(source, bytes):
        source = source.decode("utf-8")
    out = []
    g = _tokenize.generate_tokens(_io.StringIO(source).readline)
    for t in g:
        if t.type != _tokenize.COMMENT:
            continue
        before = t.line[:t.start[1]]
        own = (before.strip() == "")
        indent = (len(before) - len(before.lstrip())) if own else t.start[1]
        out.append(Comment(t.start[0], len(before.encode("utf-8")),
                           t.string, own, indent))
    return out


# ----------------------------------------------------------------------------
# Parser
# ----------------------------------------------------------------------------

# binary operator precedence (higher binds tighter); excludes ** and unary.
_BINOP = {
    "|": ("BitOr", 4),
    "^": ("BitXor", 5),
    "&": ("BitAnd", 6),
    "<<": ("LShift", 7),
    ">>": ("RShift", 7),
    "+": ("Add", 8),
    "-": ("Sub", 8),
    "*": ("Mult", 9),
    "/": ("Div", 9),
    "//": ("FloorDiv", 9),
    "%": ("Mod", 9),
    "@": ("MatMult", 9),
}
_CMP = {
    "<": "Lt", ">": "Gt", "==": "Eq", "!=": "NotEq", "<=": "LtE", ">=": "GtE",
    "in": "In", "is": "Is",  # 'not in' / 'is not' handled specially
}
_UNARY = {"+": "UAdd", "-": "USub", "~": "Invert"}
_AUG = {
    "+=": "Add", "-=": "Sub", "*=": "Mult", "/=": "Div", "//=": "FloorDiv",
    "%=": "Mod", "@=": "MatMult", "&=": "BitAnd", "|=": "BitOr", "^=": "BitXor",
    "<<=": "LShift", ">>=": "RShift", "**=": "Pow",
}


def _is_aug(tok):
    return tok.type == _tokenize.OP and tok.string in _AUG


class _Parser:
    def __init__(self, toks, filename="<unknown>", source=""):
        self.toks = toks
        self.i = 0
        self.filename = filename
        self.source = source
        self._lines = source.splitlines(keepends=True)

    def _slice(self, start, end):
        (r1, c1), (r2, c2) = start, end
        if r1 == r2:
            return self._lines[r1 - 1][c1:c2]
        out = [self._lines[r1 - 1][c1:]]
        for r in range(r1, r2 - 1):
            out.append(self._lines[r])
        out.append(self._lines[r2 - 1][:c2])
        return "".join(out)

    # -- token helpers ------------------------------------------------------
    def peek(self, k=0):
        j = self.i + k
        return self.toks[j] if j < len(self.toks) else self.toks[-1]

    def cur(self):
        return self.toks[self.i]

    def advance(self):
        t = self.toks[self.i]
        if self.i < len(self.toks) - 1:
            self.i += 1
        return t

    def at_op(self, *vals):
        t = self.cur()
        return t.type == _tokenize.OP and t.string in vals

    def at_name(self, *vals):
        t = self.cur()
        return t.type == _tokenize.NAME and (not vals or t.string in vals)

    def at_kw(self, *vals):
        t = self.cur()
        return t.type == _tokenize.NAME and t.string in vals and t.string in _keyword.kwlist

    def accept_op(self, val):
        if self.at_op(val):
            return self.advance()
        return None

    def expect_op(self, val):
        if not self.at_op(val):
            self.error(f"expected {val!r}")
        return self.advance()

    def accept_kw(self, val):
        if self.at_kw(val):
            return self.advance()
        return None

    def expect_kw(self, val):
        if not self.at_kw(val):
            self.error(f"expected keyword {val!r}")
        return self.advance()

    def error(self, msg: str) -> "NoReturn":
        t = self.cur()
        raise PyCSLSyntaxError(
            f"{msg} (got {_tokenize.tok_name[t.type]} {t.string!r})",
            (self.filename, t.start[0], t.start[1] + 1, t.string),
        )

    def unsupported(self, what: str) -> "NoReturn":
        t = self.cur()
        raise PyCSLSyntaxError(
            f"pure_ast parser: {what} not yet implemented",
            (self.filename, t.start[0], t.start[1] + 1, t.string),
        )

    # -- node construction with positions -----------------------------------
    def _fin(self, node, start_tok, end_tok=None):
        et = end_tok if end_tok is not None else self.toks[max(self.i - 1, 0)]
        node.lineno = start_tok.start[0]
        node.col_offset = start_tok.start[1]
        node.end_lineno = et.end[0]
        node.end_col_offset = et.end[1]
        return node

    def node(self, name, start_tok, **kw):
        n = _N(name)(**kw)
        return self._fin(n, start_tok)

    @staticmethod
    def _max_end(obj, cur):
        """Fold the maximum (end_lineno, end_col_offset) over `obj` into `cur`.
        A located node's own end already covers its whole subtree, so we stop
        there; an UNLOCATED node (e.g. `match_case`, which CPython gives no
        position) is descended into so its located children still count."""
        if isinstance(obj, list):
            for x in obj:
                cur = _Parser._max_end(x, cur)
            return cur
        el = getattr(obj, "end_lineno", None)
        if el is not None:
            ec = getattr(obj, "end_col_offset", 0) or 0
            if el > cur[0] or (el == cur[0] and ec > cur[1]):
                cur = (el, ec)
            return cur
        if hasattr(obj, "_fields"):
            for f in obj._fields:
                cur = _Parser._max_end(getattr(obj, f, None), cur)
        return cur

    def _fin_block(self, node, start_tok):
        """Position a COMPOUND statement: start from `start_tok`, end at the
        last (deepest) body element — matching CPython, which ends a
        def/class/if/while/for/with/try/match at its last body node, not at the
        trailing NEWLINE/DEDENT that `_fin`'s last-consumed-token would pick."""
        node.lineno = start_tok.start[0]
        node.col_offset = start_tok.start[1]
        cur = (node.lineno, start_tok.end[1])
        for fname in node._fields:
            cur = self._max_end(getattr(node, fname, None), cur)
        node.end_lineno, node.end_col_offset = cur
        return node

    # -- entry points -------------------------------------------------------
    def parse_module(self):
        body = []
        while not self.cur().type == _tokenize.ENDMARKER:
            if self.cur().type == _tokenize.NEWLINE:
                self.advance()
                continue
            body.extend(self.statement())
        m = _N("Module")(body=body, type_ignores=[])
        return m

    def parse_eval(self):
        node = self.testlist()
        e = _N("Expression")(body=node)
        return e

    # -- statements ---------------------------------------------------------
    def statement(self):
        t = self.cur()
        if t.type == _tokenize.NAME and t.string in _keyword.kwlist:
            kw = t.string
            if kw == "if":
                return [self.if_stmt()]
            if kw == "while":
                return [self.while_stmt()]
            if kw == "for":
                return [self.for_stmt(async_=False)]
            if kw == "try":
                return [self.try_stmt()]
            if kw == "with":
                return [self.with_stmt(async_=False)]
            if kw == "def":
                return [self.funcdef([], async_=False)]
            if kw == "class":
                return [self.classdef([])]
            if kw == "async":
                return [self.async_stmt()]
        if self.at_op("@"):
            return [self.decorated()]
        # match (soft keyword): `match` NAME ... ':' — detect cautiously
        if self.at_name("match") and self._looks_like_match():
            return [self.match_stmt()]
        if self.at_name("type") and self._looks_like_type_alias():
            return [self.type_alias_stmt()]
        return self.simple_stmt()

    def _looks_like_match(self):
        # 'match' is a soft keyword. Treat as a match statement only when it is
        # clearly not an expression/assignment: the token after 'match' starts a
        # subject and the logical line (at bracket depth 0) ends with ':'.
        nxt = self.peek(1)
        if _is_aug(nxt):
            return False
        if nxt.type == _tokenize.OP and nxt.string in (
                "=", ":", ".", ",", ";", ")", "]", "}", "(", "[",
                "==", "!=", "<", ">", "<=", ">=", "|", "&", "^", "+", "-",
                "*", "/", "//", "%", "@", "<<", ">>", "**"):
            return False
        if nxt.type == _tokenize.NAME and nxt.string in _keyword.kwlist:
            return False
        if nxt.type == _tokenize.NEWLINE:
            return False
        return self._line_ends_with_colon()

    def _line_ends_with_colon(self):
        depth = 0
        j = self.i
        n = len(self.toks)
        last_sig = None
        while j < n:
            tk = self.toks[j]
            if tk.type == _tokenize.OP and tk.string in ("(", "[", "{"):
                depth += 1
            elif tk.type == _tokenize.OP and tk.string in (")", "]", "}"):
                depth -= 1
            elif tk.type == _tokenize.NEWLINE and depth == 0:
                break
            last_sig = tk
            j += 1
        return (last_sig is not None and last_sig.type == _tokenize.OP
                and last_sig.string == ":")

    def _looks_like_type_alias(self):
         # PEP 695: `type NAME [type-params] = ...` ('type' soft keyword).
        nxt = self.peek(1)
        return nxt.type == _tokenize.NAME and nxt.string not in _keyword.kwlist

    def _parse_type_params(self):
         # PEP 695: parse content between '[' and ']'
         # Grammar: type_param ( ',' type_param )*
         #   where type_param is one of:
         #     NAME [ < bound ]       -> TypeVar(name, bound)
         #     * NAME                 -> TypeVarTuple(name)
         #     ** NAME               -> ParamSpec(name)
        self.expect_op("[")
        params = []
        while not self.at_op("]"):
            param_start = self.cur()
            if len(params) > 0:
                self.expect_op(",")

            if self.at_op("**"):
                 # ParamSpec
                self.advance()  # consume '**'
                name = self._name_str()
                params.append(self._fin(_N("ParamSpec")(name=name), param_start))
            elif self.at_op("*"):
                 # TypeVarTuple
                self.advance()  # consume '*'
                name = self._name_str()
                params.append(self._fin(_N("TypeVarTuple")(name=name), param_start))
            else:
                  # TypeVar with optional bound (PEP 695 uses ':' not '<')
                name = self._name_str()
                bound = None
                if self.at_op(":"):
                    self.advance()   # consume ':'
                    bound = self.test()
                params.append(self._fin(_N("TypeVar")(name=name, bound=bound), param_start))

        self.expect_op("]")
        return params

    def type_alias_stmt(self):
         # PEP 695: type NAME [type-params] = expr
        t = self.advance()                             # consume 'type' soft keyword
        name_id = self._name_str()                     # NAME token after 'type'
         # 'name' field holds an expression (Name or Subscript for generic names)
        name_node = _N("Name")(id=name_id, ctx=_N("Load")())
        type_params = []
        if self.at_op("["):
            type_params = self._parse_type_params()
         # Generic name qualifiers handled by the expression parser (e.g. X[Y])
        self.expect_op("=")
        value = self.test()
        return self._fin(_N("TypeAlias")(name=name_node, type_params=type_params, value=value), t)

    def simple_stmt(self):
        stmts = [self.small_stmt()]
        while self.accept_op(";"):
            if self.cur().type == _tokenize.NEWLINE:
                break
            stmts.append(self.small_stmt())
        if self.cur().type == _tokenize.NEWLINE:
            self.advance()
        return stmts

    def small_stmt(self):
        if self.at_kw("pass"):
            t = self.advance(); return self.node("Pass", t)
        if self.at_kw("break"):
            t = self.advance(); return self.node("Break", t)
        if self.at_kw("continue"):
            t = self.advance(); return self.node("Continue", t)
        if self.at_kw("return"):
            return self.return_stmt()
        if self.at_kw("raise"):
            return self.raise_stmt()
        if self.at_kw("del"):
            return self.del_stmt()
        if self.at_kw("assert"):
            return self.assert_stmt()
        if self.at_kw("global"):
            return self.global_stmt("Global")
        if self.at_kw("nonlocal"):
            return self.global_stmt("Nonlocal")
        if self.at_kw("import"):
            return self.import_stmt()
        if self.at_kw("from"):
            return self.import_from()
        if self.at_kw("yield"):
            t = self.cur()
            y = self.yield_expr()
            return self._fin(_N("Expr")(value=y), t)
        return self.expr_stmt()

    def return_stmt(self):
        t = self.advance()
        # PEP-526 local annotation, runtime-INERT (a local's annotation is never evaluated —
        # the same idiom this file already uses for `asname: Optional[str] = None`). It is
        # here for the VERIFIER: without it the `val` local is inferred `ExprIR` from its
        # assignment, the `None` initialiser erases, and `Return`'s OPTIONAL `value` field
        # would be bound from a non-option local — an L3 type error, and a value-less
        # `return` would model as a node rather than as a true `None`.
        val: Optional["ExprIR"] = None
        if not self._stmt_end():
            val = self.testlist()
        return self._fin(_N("Return")(value=val), t)

    def _stmt_end(self):
        return self.cur().type in (_tokenize.NEWLINE, _tokenize.ENDMARKER) or self.at_op(";")

    def raise_stmt(self):
        t = self.advance()
        # PEP-526 local annotations, runtime-INERT (a local's annotation is never evaluated),
        # here for the VERIFIER: they make the two locals real `option emit_ir` carriers, so a
        # bare `raise` / a `raise E` without `from` carries a TRUE `None` and not an erased
        # node. Split onto separate lines only because an annotation needs its own statement.
        exc: Optional["ExprIR"] = None
        cause: Optional["ExprIR"] = None
        if not self._stmt_end():
            exc = self.test()
            if self.accept_kw("from"):
                cause = self.test()
        return self._fin(_N("Raise")(exc=exc, cause=cause), t)

    def del_stmt(self):
        t = self.advance()
        targets = self.exprlist()
        for tg in targets:
            _set_ctx(tg, _N("Del")())
        return self._fin(_N("Delete")(targets=targets), t)

    def assert_stmt(self):
        t = self.advance()
        test = self.test()
        # PEP-526 local annotation, runtime-INERT (a local's annotation is never evaluated),
        # here for the VERIFIER: it makes the local a real `option emit_ir` carrier, so the
        # absent path is a TRUE `None` and not an erased node.
        msg: Optional["ExprIR"] = None
        if self.accept_op(","):
            msg = self.test()
        return self._fin(_N("Assert")(test=test, msg=msg), t)

    def global_stmt(self, kind):
        t = self.advance()
        names = [self._name_str()]
        while self.accept_op(","):
            names.append(self._name_str())
        return self._fin(_N(kind)(names=names), t)

    def _name_str(self) -> str:
        if self.cur().type != _tokenize.NAME:
            self.error("expected name")
        return self.advance().string

    def import_stmt(self):
        t = self.advance()
        names = [self._dotted_as_name()]
        while self.accept_op(","):
            names.append(self._dotted_as_name())
        return self._fin(_N("Import")(names=names), t)

    def _dotted_as_name(self) -> "alias":
        parts = [self._name_str()]
        while self.accept_op("."):
            parts.append(self._name_str())
        name = ".".join(parts)
        asname: Optional[str] = None
        if self.accept_kw("as"):
            asname = self._name_str()
        return _N("alias")(name=name, asname=asname)

    def import_from(self):
        t = self.advance()
        level = 0
        while self.at_op(".", "..."):
            level += 3 if self.cur().string == "..." else 1
            self.advance()
        module: Optional[str] = None
        if not self.at_kw("import"):
            parts = [self._name_str()]
            while self.accept_op("."):
                parts.append(self._name_str())
            module = ".".join(parts)
        self.expect_kw("import")
        if self.accept_op("*"):
            names = [_N("alias")(name="*", asname=None)]
        elif self.at_op("("):
            self.advance()
            names = self._import_as_names()
            self.expect_op(")")
        else:
            names = self._import_as_names()
        return self._fin(_N("ImportFrom")(module=module, names=names, level=level), t)

    def _import_as_names(self):
        names = [self._import_as_name()]
        while self.accept_op(","):
            if self.at_op(")"):
                break
            names.append(self._import_as_name())
        return names

    def _import_as_name(self) -> "alias":
        name = self._name_str()
        asname: Optional[str] = None
        if self.accept_kw("as"):
            asname = self._name_str()
        return _N("alias")(name=name, asname=asname)

    def expr_stmt(self):
        t = self.cur()
        first = self.testlist_star_expr()
        # annotated assignment
        if self.at_op(":"):
            self.advance()
            ann = self.test()
            value = None
            if self.accept_op("="):
                value = self.testlist_star_expr_or_yield()
            _set_ctx(first, _N("Store")())
            simple = 1 if isinstance(first, _N("Name")) else 0
            return self._fin(_N("AnnAssign")(target=first, annotation=ann,
                                              value=value, simple=simple), t)
        # augmented assignment
        if self.cur().type == _tokenize.OP and self.cur().string in _AUG:
            op = _AUG[self.advance().string]
            value = self.testlist_star_expr_or_yield()
            _set_ctx(first, _N("Store")())
            return self._fin(_N("AugAssign")(target=first, op=_N(op)(), value=value), t)
        # plain (possibly chained) assignment
        if self.at_op("="):
            targets = [first]
            while self.accept_op("="):
                nxt = self.testlist_star_expr_or_yield()
                targets.append(nxt)
            value = targets.pop()
            for tg in targets:
                _set_ctx(tg, _N("Store")())
            return self._fin(_N("Assign")(targets=targets, value=value), t)
        # bare expression
        return self._fin(_N("Expr")(value=first), t)

    def testlist_star_expr_or_yield(self):
        if self.at_kw("yield"):
            return self.yield_expr()
        return self.testlist_star_expr()

    def testlist_star_expr(self):
        t = self.cur()
        elts = [self.test_or_star()]
        trailing = False
        while self.accept_op(","):
            trailing = True
            if self._testlist_end():
                break
            trailing = False
            elts.append(self.test_or_star())
        if len(elts) == 1 and not trailing:
            return elts[0]
        tup = _N("Tuple")(elts=elts, ctx=_N("Load")())
        return self._fin(tup, t)

    def _testlist_end(self):
        return (self.cur().type in (_tokenize.NEWLINE, _tokenize.ENDMARKER)
                or self.at_op("=", ":", ")", "]", "}", ";"))

    def exprlist(self):
        elts = [self.expr_or_star()]
        while self.accept_op(","):
            if self._testlist_end() or self.at_kw("in"):
                break
            elts.append(self.expr_or_star())
        return elts

    def expr_or_star(self):
        if self.at_op("*"):
            t = self.advance()
            val = self.expr()
            return self._fin(_N("Starred")(value=val, ctx=_N("Load")()), t)
        return self.expr()

    def test_or_star(self):
        if self.at_op("*"):
            t = self.advance()
            val = self.expr()
            return self._fin(_N("Starred")(value=val, ctx=_N("Load")()), t)
        return self.namedexpr_test()

    def testlist(self):
        t = self.cur()
        first = self.test()
        if not self.at_op(","):
            return first
        elts = [first]
        while self.accept_op(","):
            if self._testlist_end():
                break
            elts.append(self.test())
        return self._fin(_N("Tuple")(elts=elts, ctx=_N("Load")()), t)

    # -- compound statements ------------------------------------------------
    def block(self):
        if self.cur().type == _tokenize.NEWLINE:
            self.advance()
            if self.cur().type != _tokenize.INDENT:
                self.error("expected an indented block")
            self.advance()
            body = []
            while self.cur().type != _tokenize.DEDENT:
                if self.cur().type == _tokenize.NEWLINE:
                    self.advance(); continue
                if self.cur().type == _tokenize.ENDMARKER:
                    break
                body.extend(self.statement())
            if self.cur().type == _tokenize.DEDENT:
                self.advance()
            return body
        # simple statement block on same line after ':'
        return self.simple_stmt()

    def if_stmt(self):
        t = self.advance()
        test = self.namedexpr_test()
        self.expect_op(":")
        body = self.block()
        orelse = self._if_tail()
        return self._fin_block(_N("If")(test=test, body=body, orelse=orelse), t)

    def _if_tail(self):
        if self.at_kw("elif"):
            t = self.advance()
            test = self.namedexpr_test()
            self.expect_op(":")
            body = self.block()
            orelse = self._if_tail()
            return [self._fin_block(_N("If")(test=test, body=body, orelse=orelse), t)]
        if self.at_kw("else"):
            self.advance(); self.expect_op(":")
            return self.block()
        return []

    def while_stmt(self):
        t = self.advance()
        test = self.namedexpr_test()
        self.expect_op(":")
        body = self.block()
        orelse = self._else_block()
        return self._fin_block(_N("While")(test=test, body=body, orelse=orelse), t)

    def _else_block(self):
        if self.at_kw("else"):
            self.advance(); self.expect_op(":")
            return self.block()
        return []

    # -- match statement (PEP 634; literal/capture/wildcard/value/OR/as/
    #    sequence subset — class & mapping patterns raise PyCSLSyntaxError) --
    def match_stmt(self):
        t = self.advance()                       # 'match' (soft keyword)
        subject = self._match_subject()
        self.expect_op(":")
        if self.cur().type != _tokenize.NEWLINE:
            self.error("expected a newline after 'match' subject")
        self.advance()
        if self.cur().type != _tokenize.INDENT:
            self.error("expected an indented block of 'case' clauses")
        self.advance()
        cases = []
        while self.cur().type != _tokenize.DEDENT:
            if self.cur().type == _tokenize.NEWLINE:
                self.advance(); continue
            if self.cur().type == _tokenize.ENDMARKER:
                break
            cases.append(self.case_block())
        if self.cur().type == _tokenize.DEDENT:
            self.advance()
        if not cases:
            self.error("'match' statement requires at least one 'case' clause")
        return self._fin_block(_N("Match")(subject=subject, cases=cases), t)

    def _match_subject(self):
        t = self.cur()
        first = self.namedexpr_test()
        if self.at_op(","):
            elts = [first]
            while self.accept_op(","):
                if self.at_op(":"):
                    break
                elts.append(self.namedexpr_test())
            return self._fin(_N("Tuple")(elts=elts, ctx=_N("Load")()), t)
        return first

    def case_block(self):
        if not self.at_name("case"):
            self.error("expected a 'case' clause inside 'match'")
        self.advance()                           # 'case' (soft keyword)
        pat = self.pattern()
        # PEP-526 local annotation, runtime-INERT (a local's annotation is never evaluated —
        # the same idiom `return_stmt`/`raise_stmt`/`assert_stmt` already use here). It is
        # for the VERIFIER: `match_case.guard` is in `_OPTIONAL_FIELDS`, so without it the
        # local is inferred `ExprIR` from its assignment, the `None` initialiser erases to
        # the emit_ir absent-sentinel, and a guard-less `case` would model as carrying a
        # NODE instead of a true `None`.
        guard: Optional["ExprIR"] = None
        if self.at_kw("if"):
            self.advance()
            guard = self.namedexpr_test()
        self.expect_op(":")
        body = self.block()
        return _N("match_case")(pattern=pat, guard=guard, body=body)

    def pattern(self):                            # as_pattern | or_pattern
        t = self.cur()
        p = self.or_pattern()
        if self.at_kw("as"):
            self.advance()
            return self._fin(_N("MatchAs")(pattern=p, name=self._capture_name("as")), t)
        return p

    def or_pattern(self):
        t = self.cur()
        first = self.closed_pattern()
        if self.at_op("|"):
            pats = [first]
            while self.accept_op("|"):
                pats.append(self.closed_pattern())
            return self._fin(_N("MatchOr")(patterns=pats), t)
        return first

    def _capture_name(self, ctx: str) -> str:
        tk = self.cur()
        if (tk.type != _tokenize.NAME or tk.string in _keyword.kwlist
                or tk.string == "_"):
            self.error(f"expected a capture name after {ctx!r} in pattern")
        self.advance()
        return tk.string

    def closed_pattern(self):
        t = self.cur()
        ty = t.type
        if ty == _tokenize.NUMBER or self.at_op("-", "+"):
            return self._fin(_N("MatchValue")(value=self._pattern_number()), t)
        if ty in (_tokenize.STRING, _tokenize.FSTRING_START):
            return self._fin(_N("MatchValue")(value=self.strings()), t)
        if ty == _tokenize.NAME:
            s = t.string
            if s in ("None", "True", "False"):
                self.advance()
                return self._fin(_N("MatchSingleton")(
                    value={"None": None, "True": True, "False": False}[s]), t)
            if s in _keyword.kwlist:
                self.error(f"unexpected keyword {s!r} in pattern")
            nxt = self.peek(1)
            if nxt.type == _tokenize.OP and nxt.string == ".":
                return self._fin(_N("MatchValue")(value=self._dotted_value()), t)
            if nxt.type == _tokenize.OP and nxt.string == "{":
                self.unsupported("mapping match pattern")
            if nxt.type == _tokenize.OP and nxt.string == "(":
                # class pattern `Ctor(p1, …)` — positional capture sub-patterns (sum-types).
                cls_t = self.advance()                       # consume the constructor NAME
                cls_node = self._fin(_N("Name")(id=s, ctx=_N("Load")()), cls_t)
                self.advance()                               # consume "("
                patterns = []
                while not self.at_op(")"):
                    patterns.append(self.pattern())
                    if not self.accept_op(","):
                        break
                end = self.expect_op(")")
                return self._fin_pos(_N("MatchClass")(
                    cls=cls_node, patterns=patterns, kwd_attrs=[], kwd_patterns=[]), t, end)
            self.advance()                        # capture target / wildcard
            if s == "_":
                return self._fin(_N("MatchAs")(pattern=None, name=None), t)
            return self._fin(_N("MatchAs")(pattern=None, name=s), t)
        if self.at_op("("):
            return self._sequence_pattern("(", ")", t)
        if self.at_op("["):
            return self._sequence_pattern("[", "]", t)
        if self.at_op("{"):
            self.unsupported("mapping match pattern")
        self.error("invalid pattern")

    def _pattern_number(self):
        t = self.cur()
        sign = self.advance().string if self.at_op("-", "+") else None
        if self.cur().type != _tokenize.NUMBER:
            self.error("expected a number literal in pattern")
        ntok = self.advance()
        val = self._fin(_N("Constant")(value=_parse_number(ntok.string), kind=None), ntok)
        if sign == "-":
            return self._fin(_N("UnaryOp")(op=_N("USub")(), operand=val), t)
        if sign == "+":
            return self._fin(_N("UnaryOp")(op=_N("UAdd")(), operand=val), t)
        return val

    def _dotted_value(self):
        t = self.cur()
        nm = self.advance()                       # NAME
        node = self._fin(_N("Name")(id=nm.string, ctx=_N("Load")()), nm)
        while self.accept_op("."):
            attr = self.cur()
            if attr.type != _tokenize.NAME:
                self.error("expected an attribute name after '.' in value pattern")
            self.advance()
            node = self._fin(
                _N("Attribute")(value=node, attr=attr.string, ctx=_N("Load")()), t)
        return node

    def _sequence_pattern(self, openp: str, closep: str, t):
        self.advance()                            # consume opener
        elts = []
        saw_comma = False
        while not self.at_op(closep):
            if self.at_op("*"):
                star_t = self.advance()
                nm = self.cur()
                if nm.type == _tokenize.NAME and nm.string not in _keyword.kwlist:
                    self.advance()
                    name: Optional[str] = None if nm.string == "_" else nm.string
                else:
                    self.error("expected a name after '*' in sequence pattern")
                elts.append(self._fin(_N("MatchStar")(name=name), star_t))
            else:
                elts.append(self.pattern())
            if self.accept_op(","):
                saw_comma = True
                continue
            break
        end = self.expect_op(closep)
        # '(' with a single, comma-less pattern is a group: the inner pattern.
        if openp == "(" and not saw_comma and len(elts) == 1:
            return elts[0]
        return self._fin_pos(_N("MatchSequence")(patterns=elts), t, end)

    def for_stmt(self, async_):
        t = self.advance()
        target = self._for_target()
        self.expect_kw("in")
        it = self.testlist()
        self.expect_op(":")
        body = self.block()
        orelse = self._else_block()
        cls = "AsyncFor" if async_ else "For"
        return self._fin_block(_N(cls)(target=target, iter=it, body=body,
                                       orelse=orelse, type_comment=None), t)

    def _for_target(self):
        elts = [self.expr_or_star()]
        trailing = False
        while self.accept_op(","):
            trailing = True
            if self.at_kw("in"):
                break
            trailing = False
            elts.append(self.expr_or_star())
        if len(elts) == 1 and not trailing:
            tgt = elts[0]
        else:
            tgt = _N("Tuple")(elts=elts, ctx=_N("Load")())
            tgt.lineno = elts[0].lineno; tgt.col_offset = elts[0].col_offset
            tgt.end_lineno = elts[-1].end_lineno; tgt.end_col_offset = elts[-1].end_col_offset
        _set_ctx(tgt, _N("Store")())
        return tgt

    def with_stmt(self, async_):
        t = self.advance()
        items = []
        parenthesized = False
        if self.at_op("(") and self._with_parenthesized():
            self.advance(); parenthesized = True
        items.append(self._with_item())
        while self.accept_op(","):
            if parenthesized and self.at_op(")"):
                break
            items.append(self._with_item())
        if parenthesized:
            self.expect_op(")")
        self.expect_op(":")
        body = self.block()
        cls = "AsyncWith" if async_ else "With"
        return self._fin_block(_N(cls)(items=items, body=body, type_comment=None), t)

    def _with_parenthesized(self) -> bool:
        # lookahead: a parenthesized with-items list (heuristic: '(' then items
        # with 'as' or ',' before matching ')'). Keep simple: treat '(' as a
        # normal expression unless we clearly see "as" at depth 1.
        depth = 0
        j = self.i
        n = len(self.toks)
        while j < n:
            tk = self.toks[j]
            if tk.type == _tokenize.OP and tk.string == "(":
                depth += 1
            elif tk.type == _tokenize.OP and tk.string == ")":
                depth -= 1
                if depth == 0:
                    return False
            elif depth == 1 and tk.type == _tokenize.NAME and tk.string == "as" and "as" in _keyword.kwlist:
                return True
            elif depth == 1 and tk.type == _tokenize.OP and tk.string == "," :
                # could be tuple; keep scanning for 'as'
                pass
            elif tk.type == _tokenize.NEWLINE:
                return False
            j += 1
        return False

    def _with_item(self):
        ctx = self.test()
        optional = None
        if self.accept_kw("as"):
            optional = self.expr()
            _set_ctx(optional, _N("Store")())
        return _N("withitem")(context_expr=ctx, optional_vars=optional)

    def try_stmt(self):
        t = self.advance()
        self.expect_op(":")
        body = self.block()
        handlers = []
        orelse = []
        finalbody = []
        is_star = False
        while self.at_kw("except"):
            ht = self.advance()
            if self.accept_op("*"):
                is_star = True
            typ = None; name = None
            if not self.at_op(":"):
                typ = self.test()
                if self.accept_kw("as"):
                    name = self._name_str()
            self.expect_op(":")
            hbody = self.block()
            handlers.append(self._fin_block(_N("ExceptHandler")(type=typ, name=name, body=hbody), ht))
        if self.at_kw("else"):
            self.advance(); self.expect_op(":")
            orelse = self.block()
        if self.at_kw("finally"):
            self.advance(); self.expect_op(":")
            finalbody = self.block()
        cls = "TryStar" if is_star else "Try"
        return self._fin_block(_N(cls)(body=body, handlers=handlers,
                                       orelse=orelse, finalbody=finalbody), t)

    def decorated(self):
        decorators = []
        while self.at_op("@"):
            self.advance()
            decorators.append(self.namedexpr_test())
            if self.cur().type == _tokenize.NEWLINE:
                self.advance()
        if self.at_kw("def"):
            return self.funcdef(decorators, async_=False)
        if self.at_kw("class"):
            return self.classdef(decorators)
        if self.at_kw("async"):
            self.advance()
            self.expect_kw("def")
            self.i -= 1  # let funcdef see 'def'? simpler: call directly
            return self.funcdef(decorators, async_=True)
        self.error("expected function or class definition after decorator")

    def async_stmt(self):
        t = self.advance()
        if self.at_kw("def"):
            return self.funcdef([], async_=True, start=t)
        if self.at_kw("for"):
            return self.for_stmt(async_=True)
        if self.at_kw("with"):
            return self.with_stmt(async_=True)
        self.error("expected def/for/with after 'async'")

    def funcdef(self, decorators, async_, start=None):
        t = start if start is not None else self.cur()
        self.expect_kw("def")
        name = self._name_str()
        type_params = []
        if self.at_op("["):
            type_params = self._parse_type_params()
        self.expect_op("(")
        args = self.parse_parameters(")")
        self.expect_op(")")
        returns = None
        if self.accept_op("->"):
            returns = self.test()
        self.expect_op(":")
        body = self.block()
        cls = "AsyncFunctionDef" if async_ else "FunctionDef"
        n = _N(cls)(name=name, args=args, body=body, decorator_list=decorators,
                     returns=returns, type_comment=None, type_params=type_params)
        return self._fin_block(n, t)

    def classdef(self, decorators):
        t = self.cur()
        self.expect_kw("class")
        name = self._name_str()
        type_params = []
        if self.at_op("["):
            type_params = self._parse_type_params()
        bases = []; keywords = []
        if self.accept_op("("):
            bases, keywords = self._call_args(")")
            self.expect_op(")")
        self.expect_op(":")
        body = self.block()
        n = _N("ClassDef")(name=name, bases=bases, keywords=keywords,
                           body=body, decorator_list=decorators, type_params=type_params)
        return self._fin_block(n, t)

    # -- parameters ---------------------------------------------------------
    def parse_parameters(self, close):
        posonly = []; args = []; defaults = []
        vararg = None; kwonly = []; kw_defaults = []; kwarg = None
        seen_star = False
        while not self.at_op(close):
            if self.at_op("/"):
                self.advance()
                posonly = args; args = []
                self.accept_op(",")
                continue
            if self.at_op("*"):
                self.advance()
                if self.at_op(",") or self.at_op(close):
                    seen_star = True
                else:
                    vararg = self._param_arg()
                    seen_star = True
                self.accept_op(",")
                continue
            if self.at_op("**"):
                self.advance()
                kwarg = self._param_arg()
                self.accept_op(",")
                continue
            a = self._param_arg()
            default = None
            if self.accept_op("="):
                default = self.test()
            if seen_star:
                kwonly.append(a); kw_defaults.append(default)
            else:
                args.append(a)
                if default is not None:
                    defaults.append(default)
            self.accept_op(",")
        return _N("arguments")(posonlyargs=posonly, args=args, vararg=vararg,
                               kwonlyargs=kwonly, kw_defaults=kw_defaults,
                               kwarg=kwarg, defaults=defaults)

    def _param_arg(self):
        t = self.cur()
        name = self._name_str()
        # PEP-526 local annotation, runtime-INERT (a local's annotation is never evaluated),
        # here for the VERIFIER: it makes the local a real `option emit_ir` carrier, so the
        # absent path is a TRUE `None` and not an erased node.
        ann: Optional["ExprIR"] = None
        if self.accept_op(":"):
            ann = self.test()
        return self._fin(_N("arg")(arg=name, annotation=ann, type_comment=None), t)

    def lambda_parameters(self):
        posonly = []; args = []; defaults = []
        vararg = None; kwonly = []; kw_defaults = []; kwarg = None
        seen_star = False
        while not self.at_op(":"):
            if self.at_op("/"):
                self.advance(); posonly = args; args = []; self.accept_op(","); continue
            if self.at_op("*"):
                self.advance()
                if self.at_op(",") or self.at_op(":"):
                    seen_star = True
                else:
                    vararg = self._lambda_arg(); seen_star = True
                self.accept_op(","); continue
            if self.at_op("**"):
                self.advance(); kwarg = self._lambda_arg(); self.accept_op(","); continue
            a = self._lambda_arg()
            default = None
            if self.accept_op("="):
                default = self.test()
            if seen_star:
                kwonly.append(a); kw_defaults.append(default)
            else:
                args.append(a)
                if default is not None:
                    defaults.append(default)
            self.accept_op(",")
        return _N("arguments")(posonlyargs=posonly, args=args, vararg=vararg,
                               kwonlyargs=kwonly, kw_defaults=kw_defaults,
                               kwarg=kwarg, defaults=defaults)

    def _lambda_arg(self):
        t = self.cur()
        name = self._name_str()
        return self._fin(_N("arg")(arg=name, annotation=None, type_comment=None), t)

    # -- expressions --------------------------------------------------------
    def namedexpr_test(self):
        t = self.cur()
        first = self.test()
        if self.at_op(":="):
            self.advance()
            value = self.test()
            _set_ctx(first, _N("Store")())
            return self._fin(_N("NamedExpr")(target=first, value=value), t)
        return first

    def test(self):
        if self.at_kw("lambda"):
            return self.lambdef()
        t = self.cur()
        cond = self.or_test()
        if self.at_kw("if"):
            self.advance()
            test = self.or_test()
            self.expect_kw("else")
            orelse = self.test()
            return self._fin(_N("IfExp")(test=test, body=cond, orelse=orelse), t)
        return cond

    def lambdef(self):
        t = self.advance()  # 'lambda'
        if self.at_op(":"):
            args = _N("arguments")(posonlyargs=[], args=[], vararg=None,
                                   kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[])
        else:
            args = self.lambda_parameters()
        self.expect_op(":")
        body = self.test()
        return self._fin(_N("Lambda")(args=args, body=body), t)

    def or_test(self):
        t = self.cur()
        left = self.and_test()
        if self.at_kw("or"):
            values = [left]
            while self.accept_kw("or"):
                values.append(self.and_test())
            return self._fin(_N("BoolOp")(op=_N("Or")(), values=values), t)
        return left

    def and_test(self):
        t = self.cur()
        left = self.not_test()
        if self.at_kw("and"):
            values = [left]
            while self.accept_kw("and"):
                values.append(self.not_test())
            return self._fin(_N("BoolOp")(op=_N("And")(), values=values), t)
        return left

    def not_test(self):
        if self.at_kw("not"):
            t = self.advance()
            operand = self.not_test()
            return self._fin(_N("UnaryOp")(op=_N("Not")(), operand=operand), t)
        return self.comparison()

    def comparison(self):
        t = self.cur()
        left = self.expr()
        ops = []; comparators = []
        while True:
            if self.at_kw("not") and self.peek(1).string == "in" and self.peek(1).type == _tokenize.NAME:
                self.advance(); self.advance()
                ops.append(_N("NotIn")())
            elif self.at_kw("is"):
                self.advance()
                if self.at_kw("not"):
                    self.advance(); ops.append(_N("IsNot")())
                else:
                    ops.append(_N("Is")())
            elif self.at_kw("in"):
                self.advance(); ops.append(_N("In")())
            elif self.cur().type == _tokenize.OP and self.cur().string in _CMP:
                ops.append(_N(_CMP[self.advance().string])())
            else:
                break
            comparators.append(self.expr())
        if ops:
            return self._fin(_N("Compare")(left=left, ops=ops, comparators=comparators), t)
        return left

    def expr(self):
        return self._binop(0)

    def _binop(self, min_prec):
        t = self.cur()
        left = self.factor()
        while self.cur().type == _tokenize.OP and self.cur().string in _BINOP:
            opname, prec = _BINOP[self.cur().string]
            if prec < min_prec:
                break
            self.advance()
            right = self._binop(prec + 1)
            left = _N("BinOp")(left=left, op=_N(opname)(), right=right)
            left.lineno = t.start[0]; left.col_offset = t.start[1]
            left.end_lineno = right.end_lineno; left.end_col_offset = right.end_col_offset
        return left

    def factor(self):
        if self.cur().type == _tokenize.OP and self.cur().string in _UNARY:
            t = self.advance()
            operand = self.factor()
            return self._fin(_N("UnaryOp")(op=_N(_UNARY[t.string])(), operand=operand), t)
        return self.power()

    def power(self):
        t = self.cur()
        base = self.await_expr()
        if self.at_op("**"):
            self.advance()
            exp = self.factor()
            n = _N("BinOp")(left=base, op=_N("Pow")(), right=exp)
            n.lineno = t.start[0]; n.col_offset = t.start[1]
            n.end_lineno = exp.end_lineno; n.end_col_offset = exp.end_col_offset
            return n
        return base

    def await_expr(self):
        if self.at_kw("await"):
            t = self.advance()
            value = self.unary_postfix()
            return self._fin(_N("Await")(value=value), t)
        return self.unary_postfix()

    def unary_postfix(self):
        atom = self.atom()
        return self.trailers(atom)

    def trailers(self, atom):
        start_line = atom.lineno; start_col = atom.col_offset
        while True:
            if self.at_op("."):
                self.advance()
                attr = self._name_str()
                end = self.toks[self.i - 1]
                n = _N("Attribute")(value=atom, attr=attr, ctx=_N("Load")())
                n.lineno = start_line; n.col_offset = start_col
                n.end_lineno = end.end[0]; n.end_col_offset = end.end[1]
                atom = n
            elif self.at_op("("):
                self.advance()
                args, keywords = self._call_args(")")
                end = self.expect_op(")")
                n = _N("Call")(func=atom, args=args, keywords=keywords)
                n.lineno = start_line; n.col_offset = start_col
                n.end_lineno = end.end[0]; n.end_col_offset = end.end[1]
                atom = n
            elif self.at_op("["):
                self.advance()
                sl = self._subscript()
                end = self.expect_op("]")
                n = _N("Subscript")(value=atom, slice=sl, ctx=_N("Load")())
                n.lineno = start_line; n.col_offset = start_col
                n.end_lineno = end.end[0]; n.end_col_offset = end.end[1]
                atom = n
            else:
                break
        return atom

    def _subscript(self):
        t = self.cur()
        elts = [self._subscript_item()]
        trailing = False
        while self.accept_op(","):
            trailing = True
            if self.at_op("]"):
                break
            trailing = False
            elts.append(self._subscript_item())
        if len(elts) == 1 and not trailing:
            return elts[0]
        tup = _N("Tuple")(elts=elts, ctx=_N("Load")())
        tup.lineno = elts[0].lineno; tup.col_offset = elts[0].col_offset
        tup.end_lineno = elts[-1].end_lineno; tup.end_col_offset = elts[-1].end_col_offset
        return tup

    def _subscript_item(self):
        t = self.cur()
        lower = upper = step = None
        if not self.at_op(":"):
            lower = self.test_or_star_slice()
            if not self.at_op(":"):
                return lower
        # at ':'
        self.expect_op(":")
        if not self.at_op(":") and not self.at_op("]") and not self.at_op(","):
            upper = self.test()
        if self.accept_op(":"):
            if not self.at_op("]") and not self.at_op(","):
                step = self.test()
        return self._fin(_N("Slice")(lower=lower, upper=upper, step=step), t)

    def test_or_star_slice(self):
        if self.at_op("*"):
            t = self.advance(); v = self.expr()
            return self._fin(_N("Starred")(value=v, ctx=_N("Load")()), t)
        return self.test()

    def _call_args(self, close):
        args = []; keywords = []
        while not self.at_op(close):
            if self.at_op("*"):
                t = self.advance()
                v = self.test()
                args.append(self._fin(_N("Starred")(value=v, ctx=_N("Load")()), t))
            elif self.at_op("**"):
                self.advance()
                v = self.test()
                keywords.append(_N("keyword")(arg=None, value=v))
            else:
                # could be keyword=value, name=value, or positional (maybe genexp)
                if (self.cur().type == _tokenize.NAME and self.peek(1).type == _tokenize.OP
                        and self.peek(1).string == "=" and self.cur().string not in _keyword.kwlist):
                    name = self.advance().string
                    self.advance()  # '='
                    v = self.test()
                    keywords.append(_N("keyword")(arg=name, value=v))
                else:
                    e = self.namedexpr_test()
                    if self.at_kw("for") or (self.at_kw("async") and self.peek(1).string == "for"):
                        gens = self.comp_for()
                        ge = _N("GeneratorExp")(elt=e, generators=gens)
                        ge.lineno = e.lineno; ge.col_offset = e.col_offset
                        last = self.toks[self.i - 1]
                        ge.end_lineno = last.end[0]; ge.end_col_offset = last.end[1]
                        args.append(ge)
                    else:
                        args.append(e)
            if not self.accept_op(","):
                break
        return args, keywords

    # -- atoms --------------------------------------------------------------
    def atom(self):
        t = self.cur()
        ty = t.type
        if ty == _tokenize.NUMBER:
            self.advance()
            return self._fin(_N("Constant")(value=_parse_number(t.string), kind=None), t)
        if ty == _tokenize.STRING or ty == _tokenize.FSTRING_START:
            return self.strings()
        if ty == _tokenize.NAME:
            s = t.string
            if s == "None":
                self.advance(); return self._fin(_N("Constant")(value=None, kind=None), t)
            if s == "True":
                self.advance(); return self._fin(_N("Constant")(value=True, kind=None), t)
            if s == "False":
                self.advance(); return self._fin(_N("Constant")(value=False, kind=None), t)
            if s == "yield" and s in _keyword.kwlist:
                return self.yield_expr()
            if s in _keyword.kwlist and s not in ("await",):
                self.error(f"unexpected keyword {s!r}")
            self.advance()
            return self._fin(_N("Name")(id=s, ctx=_N("Load")()), t)
        if self.at_op("..."):
            self.advance(); return self._fin(_N("Constant")(value=..., kind=None), t)
        if self.at_op("("):
            return self.atom_paren()
        if self.at_op("["):
            return self.atom_list()
        if self.at_op("{"):
            return self.atom_brace()
        self.error("unexpected token in expression")

    def atom_paren(self):
        t = self.advance()  # '('
        if self.at_op(")"):
            end = self.advance()
            return self._fin_pos(_N("Tuple")(elts=[], ctx=_N("Load")()), t, end)
        if self.at_kw("yield"):
            y = self.yield_expr()
            end = self.expect_op(")")
            return y  # parenthesized yield: positions kept from yield
        if self.at_op("*"):
            elts = [self.test_or_star()]
            while self.accept_op(","):
                if self.at_op(")"):
                    break
                elts.append(self.test_or_star())
            end = self.expect_op(")")
            return self._fin_pos(_N("Tuple")(elts=elts, ctx=_N("Load")()), t, end)
        first = self.namedexpr_test()
        if self.at_kw("for") or (self.at_kw("async") and self.peek(1).string == "for"):
            gens = self.comp_for()
            end = self.expect_op(")")
            ge = _N("GeneratorExp")(elt=first, generators=gens)
            return self._fin_pos(ge, t, end)
        if self.at_op(","):
            elts = [first]
            while self.accept_op(","):
                if self.at_op(")"):
                    break
                elts.append(self.test_or_star())
            end = self.expect_op(")")
            return self._fin_pos(_N("Tuple")(elts=elts, ctx=_N("Load")()), t, end)
        end = self.expect_op(")")
        # parenthesized single expression: CPython keeps inner node's position
        return first

    def _fin_pos(self, node, start_tok, end_tok):
        node.lineno = start_tok.start[0]; node.col_offset = start_tok.start[1]
        node.end_lineno = end_tok.end[0]; node.end_col_offset = end_tok.end[1]
        return node

    def atom_list(self):
        t = self.advance()  # '['
        if self.at_op("]"):
            end = self.advance()
            return self._fin_pos(_N("List")(elts=[], ctx=_N("Load")()), t, end)
        first = self.test_or_star()
        if self.at_kw("for") or (self.at_kw("async") and self.peek(1).string == "for"):
            gens = self.comp_for()
            end = self.expect_op("]")
            return self._fin_pos(_N("ListComp")(elt=first, generators=gens), t, end)
        elts = [first]
        while self.accept_op(","):
            if self.at_op("]"):
                break
            elts.append(self.test_or_star())
        end = self.expect_op("]")
        return self._fin_pos(_N("List")(elts=elts, ctx=_N("Load")()), t, end)

    def atom_brace(self):
        t = self.advance()  # '{'
        if self.at_op("}"):
            end = self.advance()
            return self._fin_pos(_N("Dict")(keys=[], values=[]), t, end)
        if self.at_op("**"):
            return self._dict_rest(t, first_key=None)
        first = self.test_or_star()
        if self.at_op(":"):
            # dict
            self.advance()
            firstval = self.test()
            if self.at_kw("for") or (self.at_kw("async") and self.peek(1).string == "for"):
                gens = self.comp_for()
                end = self.expect_op("}")
                return self._fin_pos(_N("DictComp")(key=first, value=firstval, generators=gens), t, end)
            keys = [first]; values = [firstval]
            while self.accept_op(","):
                if self.at_op("}"):
                    break
                if self.at_op("**"):
                    self.advance()
                    keys.append(None); values.append(self.test())
                else:
                    k = self.test(); self.expect_op(":"); v = self.test()
                    keys.append(k); values.append(v)
            end = self.expect_op("}")
            return self._fin_pos(_N("Dict")(keys=keys, values=values), t, end)
        # set (or set comp)
        if self.at_kw("for") or (self.at_kw("async") and self.peek(1).string == "for"):
            gens = self.comp_for()
            end = self.expect_op("}")
            return self._fin_pos(_N("SetComp")(elt=first, generators=gens), t, end)
        elts = [first]
        while self.accept_op(","):
            if self.at_op("}"):
                break
            elts.append(self.test_or_star())
        end = self.expect_op("}")
        return self._fin_pos(_N("Set")(elts=elts), t, end)

    def _dict_rest(self, t, first_key):
        self.advance()  # '**'
        keys = [None]; values = [self.test()]
        while self.accept_op(","):
            if self.at_op("}"):
                break
            if self.at_op("**"):
                self.advance(); keys.append(None); values.append(self.test())
            else:
                k = self.test(); self.expect_op(":"); v = self.test()
                keys.append(k); values.append(v)
        end = self.expect_op("}")
        return self._fin_pos(_N("Dict")(keys=keys, values=values), t, end)

    def comp_for(self):
        gens = []
        while self.at_kw("for") or (self.at_kw("async") and self.peek(1).string == "for"):
            is_async = 0
            if self.at_kw("async"):
                self.advance(); is_async = 1
            self.expect_kw("for")
            target = self._comp_target()
            self.expect_kw("in")
            it = self.or_test()
            ifs = []
            while self.at_kw("if"):
                self.advance()
                ifs.append(self.or_test_no_cond())
            gens.append(_N("comprehension")(target=target, iter=it, ifs=ifs, is_async=is_async))
        return gens

    def or_test_no_cond(self):
        # comprehension 'if' uses or_test (no ternary, no walrus per grammar uses test_nocond)
        if self.at_kw("lambda"):
            return self.lambdef()
        return self.or_test()

    def _comp_target(self):
        elts = [self.expr_or_star()]
        trailing = False
        while self.accept_op(","):
            trailing = True
            if self.at_kw("in"):
                break
            trailing = False
            elts.append(self.expr_or_star())
        if len(elts) == 1 and not trailing:
            tgt = elts[0]
        else:
            tgt = _N("Tuple")(elts=elts, ctx=_N("Load")())
            tgt.lineno = elts[0].lineno; tgt.col_offset = elts[0].col_offset
            tgt.end_lineno = elts[-1].end_lineno; tgt.end_col_offset = elts[-1].end_col_offset
        _set_ctx(tgt, _N("Store")())
        return tgt

    def yield_expr(self):
        t = self.advance()  # 'yield'
        if self.accept_kw("from"):
            val = self.test()
            return self._fin(_N("YieldFrom")(value=val), t)
        # PEP-526 local annotation, runtime-INERT (a local's annotation is never
        # evaluated), here for the VERIFIER: it makes the local a real optional carrier,
        # so the absent path is a TRUE `None` and not an erased node.
        value: Optional["ExprIR"] = None
        if not self._stmt_end() and not self.at_op(")", "]", "}", ":", ","):
            value = self.testlist()
        return self._fin(_N("Yield")(value=value), t)

    # -- strings / f-strings ------------------------------------------------
    def strings(self):
        t = self.cur()
        parts = []  # list of ('str', value, kind) or ('joined', JoinedStr node)
        has_f = False
        kinds = set()
        while self.cur().type in (_tokenize.STRING, _tokenize.FSTRING_START):
            if self.cur().type == _tokenize.STRING:
                tok = self.advance()
                val, kind, is_bytes = _decode_string(tok.string)
                parts.append(("bytes" if is_bytes else "str", val, kind, tok))
                if kind:
                    kinds.add(kind)
            else:
                js = self._fstring()
                parts.append(("joined", js, None, None))
                has_f = True
        last = self.toks[self.i - 1]
        if not has_f:
            # concatenate constants
            if all(p[0] == "bytes" for p in parts):
                value = b"".join(p[1] for p in parts)
            else:
                value = "".join(p[1] for p in parts)
            kind = "u" if "u" in kinds else None
            n = _N("Constant")(value=value, kind=kind)
            return self._fin_pos(n, t, last)
        # build JoinedStr from mixed string/f-string parts
        values = []
        for kind_tag, payload, _k, ptok in parts:
            if kind_tag == "joined":
                values.extend(payload.values)
            else:
                c = _N("Constant")(value=payload, kind=None)
                c.lineno = ptok.start[0]; c.col_offset = ptok.start[1]
                c.end_lineno = ptok.end[0]; c.end_col_offset = ptok.end[1]
                values.append(c)
        # merge adjacent Constants
        values = _merge_str_constants(values)
        n = _N("JoinedStr")(values=values)
        return self._fin_pos(n, t, last)

    def _fstring(self):
        start = self.advance()  # FSTRING_START
        is_raw = _fstring_prefix_raw(start.string)
        values = []
        while self.cur().type != _tokenize.FSTRING_END:
            tk = self.cur()
            if tk.type == _tokenize.FSTRING_MIDDLE:
                self.advance()
                text = _decode_fstring_middle(tk.string, is_raw)
                if text != "":
                    values.append(self._fin(_N("Constant")(value=text, kind=None), tk))
            elif self.at_op("{"):
                values.extend(self._fstring_replacement(is_raw))
            else:
                self.error("malformed f-string")
        end = self.advance()  # FSTRING_END
        js = _N("JoinedStr")(values=_merge_str_constants(values, drop_empty=True))
        return self._fin_pos(js, start, end)

    def _fstring_replacement(self, is_raw=False):
        lb = self.advance()  # '{'
        expr = self.testlist_for_fstring()
        is_debug = False
        debug_text = None
        if self.at_op("="):
            eq = self.advance()
            is_debug = True
            # CPython records source from just after '{' up to the start of the
            # next part (conversion '!', spec ':' or closing '}').
            debug_text = self._slice(lb.end, self.cur().start)
        conversion = -1
        if self.at_op("!"):
            self.advance()
            conv = self._name_str() if self.cur().type == _tokenize.NAME else self.advance().string
            conversion = ord(conv[0])
        format_spec = None
        if self.at_op(":"):
            self.advance()
            format_spec = self._fstring_format_spec(is_raw)
        end = self.expect_op("}")
        if is_debug and conversion == -1 and format_spec is None:
            conversion = 114  # bare {x=} defaults conversion to 'r'
        fv = _N("FormattedValue")(value=expr, conversion=conversion, format_spec=format_spec)
        self._fin_pos(fv, lb, end)
        out = []
        if debug_text is not None:
            c = _N("Constant")(value=debug_text, kind=None)
            c.lineno = lb.start[0]; c.col_offset = lb.start[1]
            c.end_lineno = lb.end[0]; c.end_col_offset = lb.end[1]
            out.append(c)
        out.append(fv)
        return out

    def testlist_for_fstring(self):
        t = self.cur()
        first = self.namedexpr_test()
        if not self.at_op(","):
            return first
        elts = [first]
        while self.accept_op(","):
            if self.at_op("}") or self.at_op("!") or self.at_op(":") or self.at_op("="):
                break
            elts.append(self.namedexpr_test())
        return self._fin(_N("Tuple")(elts=elts, ctx=_N("Load")()), t)

    def _fstring_format_spec(self, is_raw=False):
        t = self.cur()
        values = []
        while not self.at_op("}") and self.cur().type != _tokenize.FSTRING_END:
            tk = self.cur()
            if tk.type == _tokenize.FSTRING_MIDDLE:
                self.advance()
                text = _decode_fstring_middle(tk.string, is_raw)
                values.append(self._fin(_N("Constant")(value=text, kind=None), tk))
            elif self.at_op("{"):
                values.extend(self._fstring_replacement(is_raw))
            else:
                break
        js = _N("JoinedStr")(values=_merge_str_constants(values, drop_empty=False))
        if values:
            js.lineno = values[0].lineno; js.col_offset = values[0].col_offset
            js.end_lineno = values[-1].end_lineno; js.end_col_offset = values[-1].end_col_offset
        else:
            js.lineno = t.start[0]; js.col_offset = t.start[1]
            js.end_lineno = t.start[0]; js.end_col_offset = t.start[1]
        return js


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def _fstring_prefix_raw(start_string):
    pre = ""
    for ch in start_string:
        if ch.isalpha():
            pre += ch
        else:
            break
    return "r" in pre.lower()


def _decode_fstring_middle(text, is_raw):
    if is_raw:
        return text
    return _decode_escapes(text, False)


def _merge_str_constants(values, drop_empty=True):
    out = []
    Constant = _N("Constant")
    for v in values:
        if (drop_empty and isinstance(v, Constant) and v.value == ""):
            continue
        if (out and isinstance(out[-1], Constant) and isinstance(v, Constant)
                and isinstance(out[-1].value, str) and isinstance(v.value, str)):
            out[-1].value += v.value
            out[-1].end_lineno = getattr(v, "end_lineno", out[-1].end_lineno)
            out[-1].end_col_offset = getattr(v, "end_col_offset", out[-1].end_col_offset)
        else:
            out.append(v)
    return out


def _set_ctx(node, ctx):
    Name = _N("Name"); Attribute = _N("Attribute"); Subscript = _N("Subscript")
    Starred = _N("Starred"); List = _N("List"); Tuple = _N("Tuple")
    if isinstance(node, (Name, Attribute, Subscript)):
        node.ctx = ctx
    elif isinstance(node, Starred):
        node.ctx = ctx
        _set_ctx(node.value, ctx)
    elif isinstance(node, (List, Tuple)):
        node.ctx = ctx
        for e in node.elts:
            _set_ctx(e, ctx)


def _parse_number(s):
    s = s.replace("_", "")
    low = s.lower()
    if low.endswith("j"):
        return complex(0, float(s[:-1]))
    if low.startswith(("0x", "0o", "0b")):
        return int(s, 0)
    if any(c in low for c in ".e") and not low.startswith("0x"):
        return float(s)
    try:
        return int(s)
    except ValueError:
        return float(s)


_SIMPLE_ESCAPES = {
    "\n": "", "\\": "\\", "'": "'", '"': '"', "a": "\a", "b": "\b",
    "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v",
}


def _decode_string(tok):
    # returns (value, kind, is_bytes)
    i = 0
    prefix = ""
    while i < len(tok) and tok[i] not in "'\"":
        prefix += tok[i]; i += 1
    rest = tok[i:]
    p = prefix.lower()
    is_bytes = "b" in p
    is_raw = "r" in p
    kind = "u" if "u" in p else None
    # strip quotes
    if rest[:3] in ('"""', "'''"):
        q = rest[:3]; body = rest[3:-3]
    else:
        q = rest[0]; body = rest[1:-1]
    if is_raw:
        if is_bytes:
            return (body.encode("latin-1", "backslashreplace") if False else bytes(body, "utf-8"), kind, True)
        return (body, kind, False)
    decoded = _decode_escapes(body, is_bytes)
    if is_bytes:
        return (decoded, kind, True)
    return (decoded, kind, False)


def _decode_escapes(body, is_bytes):
    out = []
    i = 0
    n = len(body)
    while i < n:
        c = body[i]
        if c != "\\":
            out.append(c); i += 1; continue
        i += 1
        if i >= n:
            out.append("\\"); break
        e = body[i]
        if e in _SIMPLE_ESCAPES:
            out.append(_SIMPLE_ESCAPES[e]); i += 1
        elif e in "01234567":
            j = i; digits = ""
            while j < n and len(digits) < 3 and body[j] in "01234567":
                digits += body[j]; j += 1
            out.append(chr(int(digits, 8))); i = j
        elif e == "x":
            hexd = body[i + 1:i + 3]; out.append(chr(int(hexd, 16))); i += 3
        elif e == "u" and not is_bytes:
            hexd = body[i + 1:i + 5]; out.append(chr(int(hexd, 16))); i += 5
        elif e == "U" and not is_bytes:
            hexd = body[i + 1:i + 9]; out.append(chr(int(hexd, 16))); i += 9
        elif e == "N" and not is_bytes:
            close = body.index("}", i)
            name = body[i + 2:close]
            out.append(_unicodedata.lookup(name)); i = close + 1
        else:
            out.append("\\"); out.append(e); i += 1
    s = "".join(out)
    if is_bytes:
        return s.encode("latin-1")
    return s


def parse(source, filename="<unknown>", mode="exec", *,
          type_comments=False, feature_version=None):
    if type_comments:
        raise PyCSLSyntaxError("pure_ast parser: type_comments not yet implemented")
    if isinstance(source, bytes):
        source = source.decode("utf-8")
    norm = source if source.endswith("\n") else source + "\n"
    toks = _lex(source)
    p = _Parser(toks, filename, norm)
    if mode == "exec":
        return p.parse_module()
    if mode == "eval":
        return p.parse_eval()
    if mode == "single":
        # interactive: list of statements wrapped in Interactive
        body = []
        while p.cur().type != _tokenize.ENDMARKER:
            if p.cur().type == _tokenize.NEWLINE:
                p.advance(); continue
            body.extend(p.statement())
        return _N("Interactive")(body=body)
    raise ValueError(f"unsupported mode {mode!r}")


# ---------------------------------------------------------------------------
# literal_eval
# ---------------------------------------------------------------------------

def literal_eval(node_or_string):
    """Safely evaluate an expression node or string of Python literals."""
    if isinstance(node_or_string, str):
        node_or_string = parse(node_or_string.lstrip(" \t"), mode='eval')
    if isinstance(node_or_string, Expression):  # noqa: F821
        node_or_string = node_or_string.body

    def _raise_malformed_node(node):
        msg = "malformed node or string"
        lno = getattr(node, 'lineno', None)
        if lno is not None:
            msg += f' on line {lno}'
        raise ValueError(msg + f': {node!r}')

    def _convert_num(node):
        if (not isinstance(node, Constant)  # noqa: F821
                or type(node.value) not in (int, float, complex)):
            _raise_malformed_node(node)
        return node.value

    def _convert_signed_num(node):
        if isinstance(node, UnaryOp) and isinstance(node.op, (UAdd, USub)):  # noqa: F821
            operand = _convert_num(node.operand)
            if isinstance(node.op, UAdd):  # noqa: F821
                return +operand
            return -operand
        return _convert_num(node)

    def _convert(node):
        if isinstance(node, Constant):  # noqa: F821
            return node.value
        if isinstance(node, Tuple):  # noqa: F821
            return tuple(map(_convert, node.elts))
        if isinstance(node, List):  # noqa: F821
            return list(map(_convert, node.elts))
        if isinstance(node, Set):  # noqa: F821
            return set(map(_convert, node.elts))
        if (isinstance(node, Call) and isinstance(node.func, Name) and  # noqa: F821
                node.func.id == 'set' and node.args == node.keywords == []):
            return set()
        if isinstance(node, Dict):  # noqa: F821
            if len(node.keys) != len(node.values):
                _raise_malformed_node(node)
            return dict(zip(map(_convert, node.keys),
                            map(_convert, node.values)))
        if isinstance(node, BinOp) and isinstance(node.op, (Add, Sub)):  # noqa: F821
            left = _convert_signed_num(node.left)
            right = _convert_num(node.right)
            if isinstance(left, (int, float)) and isinstance(right, complex):
                if isinstance(node.op, Add):  # noqa: F821
                    return left + right
                return left - right
        return _convert_signed_num(node)

    return _convert(node_or_string)


# ---------------------------------------------------------------------------
# Tree introspection helpers
# ---------------------------------------------------------------------------

def iter_fields(node):
    """Yield ``(fieldname, value)`` for each field present on *node*."""
    for field in node._fields:
        try:
            yield field, getattr(node, field)
        except AttributeError:
            pass


def iter_child_nodes(node):
    """Yield all direct child nodes of *node*."""
    for _name, field in iter_fields(node):
        if isinstance(field, AST):
            yield field
        elif isinstance(field, list):
            for item in field:
                if isinstance(item, AST):
                    yield item


def walk(node):
    """Recursively yield all descendant nodes (including *node*)."""
    from collections import deque
    todo = deque([node])
    while todo:
        node = todo.popleft()
        todo.extend(iter_child_nodes(node))
        yield node


def get_docstring(node, clean=True):
    """Return the docstring of *node*, or ``None``."""
    if not isinstance(node, (AsyncFunctionDef, FunctionDef, ClassDef, Module)):  # noqa: F821
        raise TypeError("%r can't have docstrings" % node.__class__.__name__)
    if not (node.body and isinstance(node.body[0], Expr)):  # noqa: F821
        return None
    node = node.body[0].value
    if isinstance(node, Constant) and isinstance(node.value, str):  # noqa: F821
        text = node.value
    else:
        return None
    if clean:
        import inspect
        text = inspect.cleandoc(text)
    return text


def copy_location(new_node, old_node):
    """Copy source location attributes from *old_node* to *new_node*."""
    for attr in ('lineno', 'col_offset', 'end_lineno', 'end_col_offset'):
        if attr in old_node._attributes and attr in new_node._attributes \
                and hasattr(old_node, attr):
            value = getattr(old_node, attr)
            if value is not None or (
                hasattr(new_node, attr) and getattr(new_node, attr) is None
            ):
                setattr(new_node, attr, value)
    return new_node


def fix_missing_locations(node):
    """Recursively fill in missing location attributes from the parent."""
    def _fix(node, lineno, col_offset, end_lineno, end_col_offset):
        if 'lineno' in node._attributes:
            if getattr(node, 'lineno', None) is None:
                node.lineno = lineno
            else:
                lineno = node.lineno
        if 'end_lineno' in node._attributes:
            if getattr(node, 'end_lineno', None) is None:
                node.end_lineno = end_lineno
            else:
                end_lineno = node.end_lineno
        if 'col_offset' in node._attributes:
            if getattr(node, 'col_offset', None) is None:
                node.col_offset = col_offset
            else:
                col_offset = node.col_offset
        if 'end_col_offset' in node._attributes:
            if getattr(node, 'end_col_offset', None) is None:
                node.end_col_offset = end_col_offset
            else:
                end_col_offset = node.end_col_offset
        for child in iter_child_nodes(node):
            _fix(child, lineno, col_offset, end_lineno, end_col_offset)
    _fix(node, 1, 0, 1, 0)
    return node


def increment_lineno(node, n=1):
    """Increment the line numbers of every node in *node* by *n*."""
    for child in walk(node):
        if 'lineno' in child._attributes:
            child.lineno = getattr(child, 'lineno', 0) + n
        if 'end_lineno' in child._attributes:
            end = getattr(child, 'end_lineno', None)
            if end is not None:
                child.end_lineno = end + n
    return node


# ---------------------------------------------------------------------------
# dump
# ---------------------------------------------------------------------------

def dump(node, annotate_fields=True, include_attributes=False, *, indent=None):
    """Return a formatted dump of the tree in *node* (mirrors ``ast.dump``)."""
    def _format(node, level=0):
        if indent is not None:
            level += 1
            prefix = '\n' + indent * level
            sep = ',\n' + indent * level
        else:
            prefix = ''
            sep = ', '
        if isinstance(node, AST):
            cls = type(node)
            args = []
            allsimple = True
            keywords = annotate_fields
            for name in node._fields:
                try:
                    value = getattr(node, name)
                except AttributeError:
                    keywords = True
                    continue
                if value is None and getattr(cls, name, ...) is None:
                    keywords = True
                    continue
                value, simple = _format(value, level)
                allsimple = allsimple and simple
                if keywords:
                    args.append('%s=%s' % (name, value))
                else:
                    args.append(value)
            if include_attributes and node._attributes:
                for name in node._attributes:
                    try:
                        value = getattr(node, name)
                    except AttributeError:
                        continue
                    if value is None and getattr(cls, name, ...) is None:
                        continue
                    value, simple = _format(value, level)
                    allsimple = allsimple and simple
                    args.append('%s=%s' % (name, value))
            if allsimple and len(args) <= 3:
                return '%s(%s)' % (node.__class__.__name__, ', '.join(args)), not args
            return '%s(%s%s)' % (node.__class__.__name__, prefix, sep.join(args)), False
        elif isinstance(node, list):
            if not node:
                return '[]', True
            return '[%s%s]' % (prefix, sep.join(_format(x, level)[0] for x in node)), False
        return repr(node), True

    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    if indent is not None and not isinstance(indent, str):
        indent = ' ' * indent
    return _format(node)[0]


# ---------------------------------------------------------------------------
# get_source_segment
# ---------------------------------------------------------------------------

def _splitlines_no_ff(source):
    """Split a string into lines ignoring form feed and other chars (\\n only)."""
    idx = 0
    lines = []
    next_line = ''
    while idx < len(source):
        c = source[idx]
        next_line += c
        idx += 1
        if c == '\r' and idx < len(source) and source[idx] == '\n':
            next_line += '\n'
            idx += 1
            lines.append(next_line)
            next_line = ''
        elif c in '\r\n':
            lines.append(next_line)
            next_line = ''
    if next_line:
        lines.append(next_line)
    return lines


def _pad_whitespace(source: str) -> str:
    r"""Replace all chars except '\f\t' in a line with spaces."""
    result = ''
    for c in source:
        if c in '\f\t':
            result += c
        else:
            result += ' '
    return result


def get_source_segment(source, node, *, padded=False):
    """Get the source segment of *source* that generated *node*."""
    try:
        if node.end_lineno is None or node.end_col_offset is None:
            return None
        lineno = node.lineno - 1
        end_lineno = node.end_lineno - 1
        col_offset = node.col_offset
        end_col_offset = node.end_col_offset
    except AttributeError:
        return None

    lines = _splitlines_no_ff(source)
    if end_lineno == lineno:
        return lines[lineno].encode()[col_offset:end_col_offset].decode()

    if padded:
        padding = _pad_whitespace(lines[lineno].encode()[:col_offset].decode())
    else:
        padding = ''

    first = padding + lines[lineno].encode()[col_offset:].decode()
    last = lines[end_lineno].encode()[:end_col_offset].decode()
    lines = lines[lineno + 1:end_lineno]

    lines.insert(0, first)
    lines.append(last)
    return ''.join(lines)


# ---------------------------------------------------------------------------
# Visitors
# ---------------------------------------------------------------------------

_const_node_type_names = {
    bool: 'NameConstant',
    type(None): 'NameConstant',
    int: 'Num',
    float: 'Num',
    complex: 'Num',
    str: 'Str',
    bytes: 'Bytes',
    type(...): 'Ellipsis',
}


class NodeVisitor:
    """Walk a tree, dispatching to ``visit_<Classname>`` methods."""

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for _field, value in iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item)
            elif isinstance(value, AST):
                self.visit(value)

    def visit_Constant(self, node):
        value = node.value
        type_name = _const_node_type_names.get(type(value))
        if type_name is None:
            for cls, name in _const_node_type_names.items():
                if isinstance(value, cls):
                    type_name = name
                    break
        if type_name is not None:
            method = 'visit_' + type_name
            try:
                visitor = getattr(self, method)
            except AttributeError:
                pass
            else:
                import warnings
                warnings.warn(f"{method} is deprecated; add visit_Constant",
                              DeprecationWarning, 2)
                return visitor(node)
        return self.generic_visit(node)


class NodeTransformer(NodeVisitor):
    """In-place AST transformer (mirrors ``ast.NodeTransformer``)."""

    def generic_visit(self, node):
        for field, old_value in iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node


# ---------------------------------------------------------------------------
# unparse — AST back to source (port of CPython's _Unparser)
# ---------------------------------------------------------------------------

import enum as _enum
from contextlib import contextmanager as _contextmanager, nullcontext as _nullcontext

_SINGLE_QUOTES = ("'", '"')
_MULTI_QUOTES = ('"""', "'''")
_ALL_QUOTES = (*_SINGLE_QUOTES, *_MULTI_QUOTES)
_INFSTR = "1e" + repr(_sys.float_info.max_10_exp + 1)


class _Precedence(_enum.IntEnum):
    NAMED_EXPR = _enum.auto()   # <target> := <expr1>
    TUPLE = _enum.auto()        # <expr1>, <expr2>
    YIELD = _enum.auto()        # 'yield', 'yield from'
    TEST = _enum.auto()         # 'if'-'else', 'lambda'
    OR = _enum.auto()           # 'or'
    AND = _enum.auto()          # 'and'
    NOT = _enum.auto()          # 'not'
    CMP = _enum.auto()          # comparisons
    EXPR = _enum.auto()
    BOR = EXPR                  # '|'
    BXOR = _enum.auto()         # '^'
    BAND = _enum.auto()         # '&'
    SHIFT = _enum.auto()        # '<<', '>>'
    ARITH = _enum.auto()        # '+', '-'
    TERM = _enum.auto()         # '*', '@', '/', '%', '//'
    FACTOR = _enum.auto()       # unary '+', '-', '~'
    POWER = _enum.auto()        # '**'
    AWAIT = _enum.auto()        # 'await'
    ATOM = _enum.auto()

    def next(self):
        try:
            return self.__class__(self + 1)
        except ValueError:
            return self


class _Unparser(NodeVisitor):
    """Methods in this class recursively traverse an AST and output source."""

    def __init__(self, *, _avoid_backslashes=False):
        self._source = []
        self._precedences = {}
        self._type_ignores = {}
        self._indent = 0
        self._avoid_backslashes = _avoid_backslashes
        self._in_try_star = False

    def interleave(self, inter, f, seq):
        seq = iter(seq)
        try:
            f(next(seq))
        except StopIteration:
            pass
        else:
            for x in seq:
                inter()
                f(x)

    def items_view(self, traverser, items):
        if len(items) == 1:
            traverser(items[0])
            self.write(",")
        else:
            self.interleave(lambda: self.write(", "), traverser, items)

    def maybe_newline(self):
        if self._source:
            self.write("\n")

    def fill(self, text=""):
        self.maybe_newline()
        self.write("    " * self._indent + text)

    def write(self, *text):
        self._source.extend(text)

    @_contextmanager
    def buffered(self, buffer=None):
        if buffer is None:
            buffer = []
        original_source = self._source
        self._source = buffer
        yield buffer
        self._source = original_source

    @_contextmanager
    def block(self, *, extra=None):
        self.write(":")
        if extra:
            self.write(extra)
        self._indent += 1
        yield
        self._indent -= 1

    @_contextmanager
    def delimit(self, start, end):
        self.write(start)
        yield
        self.write(end)

    def delimit_if(self, start, end, condition):
        if condition:
            return self.delimit(start, end)
        return _nullcontext()

    def require_parens(self, precedence, node):
        return self.delimit_if("(", ")", self.get_precedence(node) > precedence)

    def get_precedence(self, node):
        return self._precedences.get(node, _Precedence.TEST)

    def set_precedence(self, precedence, *nodes):
        for node in nodes:
            self._precedences[node] = precedence

    def get_raw_docstring(self, node):
        if not isinstance(node, (AsyncFunctionDef, FunctionDef, ClassDef, Module)) \
                or len(node.body) < 1:
            return None
        node = node.body[0]
        if not isinstance(node, Expr):
            return None
        node = node.value
        if isinstance(node, Constant) and isinstance(node.value, str):
            return node
        return None

    def get_type_comment(self, node):
        comment = self._type_ignores.get(getattr(node, "lineno", None)) \
            or getattr(node, "type_comment", None)
        if comment is not None:
            return f" # type: {comment}"
        return None

    def traverse(self, node):
        if isinstance(node, list):
            for item in node:
                self.traverse(item)
        else:
            super().visit(node)

    def visit(self, node):
        self._source = []
        self.traverse(node)
        return "".join(self._source)

    def _write_docstring_and_traverse_body(self, node):
        docstring = self.get_raw_docstring(node)
        if docstring:
            self._write_docstring(docstring)
            self.traverse(node.body[1:])
        else:
            self.traverse(node.body)

    def visit_Module(self, node):
        self._type_ignores = {
            ignore.lineno: f"ignore{ignore.tag}"
            for ignore in node.type_ignores
        }
        self._write_docstring_and_traverse_body(node)
        self._type_ignores.clear()

    def visit_FunctionType(self, node):
        with self.delimit("(", ")"):
            self.interleave(lambda: self.write(", "), self.traverse, node.argtypes)
        self.write(" -> ")
        self.traverse(node.returns)

    def visit_Expr(self, node):
        self.fill()
        self.set_precedence(_Precedence.YIELD, node.value)
        self.traverse(node.value)

    def visit_NamedExpr(self, node):
        with self.require_parens(_Precedence.NAMED_EXPR, node):
            self.set_precedence(_Precedence.ATOM, node.target, node.value)
            self.traverse(node.target)
            self.write(" := ")
            self.traverse(node.value)

    def visit_Import(self, node):
        self.fill("import ")
        self.interleave(lambda: self.write(", "), self.traverse, node.names)

    def visit_ImportFrom(self, node):
        self.fill("from ")
        self.write("." * (node.level or 0))
        if node.module:
            self.write(node.module)
        self.write(" import ")
        self.interleave(lambda: self.write(", "), self.traverse, node.names)

    def visit_Assign(self, node):
        self.fill()
        for target in node.targets:
            self.set_precedence(_Precedence.TUPLE, target)
            self.traverse(target)
            self.write(" = ")
        self.traverse(node.value)
        type_comment = self.get_type_comment(node)
        if type_comment:
            self.write(type_comment)

    def visit_AugAssign(self, node):
        self.fill()
        self.traverse(node.target)
        self.write(" " + self.binop[node.op.__class__.__name__] + "= ")
        self.traverse(node.value)

    def visit_AnnAssign(self, node):
        self.fill()
        with self.delimit_if(
            "(", ")", not node.simple and isinstance(node.target, Name)
        ):
            self.traverse(node.target)
        self.write(": ")
        self.traverse(node.annotation)
        if node.value:
            self.write(" = ")
            self.traverse(node.value)

    def visit_Return(self, node):
        self.fill("return")
        if node.value:
            self.write(" ")
            self.traverse(node.value)

    def visit_Pass(self, node):
        self.fill("pass")

    def visit_Break(self, node):
        self.fill("break")

    def visit_Continue(self, node):
        self.fill("continue")

    def visit_Delete(self, node):
        self.fill("del ")
        self.interleave(lambda: self.write(", "), self.traverse, node.targets)

    def visit_Assert(self, node):
        self.fill("assert ")
        self.traverse(node.test)
        if node.msg:
            self.write(", ")
            self.traverse(node.msg)

    def visit_Global(self, node):
        self.fill("global ")
        self.interleave(lambda: self.write(", "), self.write, node.names)

    def visit_Nonlocal(self, node):
        self.fill("nonlocal ")
        self.interleave(lambda: self.write(", "), self.write, node.names)

    def visit_Await(self, node):
        with self.require_parens(_Precedence.AWAIT, node):
            self.write("await")
            if node.value:
                self.write(" ")
                self.set_precedence(_Precedence.ATOM, node.value)
                self.traverse(node.value)

    def visit_Yield(self, node):
        with self.require_parens(_Precedence.YIELD, node):
            self.write("yield")
            if node.value:
                self.write(" ")
                self.set_precedence(_Precedence.ATOM, node.value)
                self.traverse(node.value)

    def visit_YieldFrom(self, node):
        with self.require_parens(_Precedence.YIELD, node):
            self.write("yield from ")
            if not node.value:
                raise ValueError("Node can't be used without a value attribute.")
            self.set_precedence(_Precedence.ATOM, node.value)
            self.traverse(node.value)

    def visit_Raise(self, node):
        self.fill("raise")
        if not node.exc:
            if node.cause:
                raise ValueError("Node can't use cause without an exception.")
            return
        self.write(" ")
        self.traverse(node.exc)
        if node.cause:
            self.write(" from ")
            self.traverse(node.cause)

    def do_visit_try(self, node):
        self.fill("try")
        with self.block():
            self.traverse(node.body)
        for ex in node.handlers:
            self.traverse(ex)
        if node.orelse:
            self.fill("else")
            with self.block():
                self.traverse(node.orelse)
        if node.finalbody:
            self.fill("finally")
            with self.block():
                self.traverse(node.finalbody)

    def visit_Try(self, node):
        prev_in_try_star = self._in_try_star
        try:
            self._in_try_star = False
            self.do_visit_try(node)
        finally:
            self._in_try_star = prev_in_try_star

    def visit_TryStar(self, node):
        prev_in_try_star = self._in_try_star
        try:
            self._in_try_star = True
            self.do_visit_try(node)
        finally:
            self._in_try_star = prev_in_try_star

    def visit_ExceptHandler(self, node):
        self.fill("except*" if self._in_try_star else "except")
        if node.type:
            self.write(" ")
            self.traverse(node.type)
        if node.name:
            self.write(" as ")
            self.write(node.name)
        with self.block():
            self.traverse(node.body)

    def visit_ClassDef(self, node):
        self.maybe_newline()
        for deco in node.decorator_list:
            self.fill("@")
            self.traverse(deco)
        self.fill("class " + node.name)
        self._type_params_helper(node.type_params)
        with self.delimit_if("(", ")", condition=node.bases or node.keywords):
            comma = False
            for e in node.bases:
                if comma:
                    self.write(", ")
                else:
                    comma = True
                self.traverse(e)
            for e in node.keywords:
                if comma:
                    self.write(", ")
                else:
                    comma = True
                self.traverse(e)
        with self.block():
            self._write_docstring_and_traverse_body(node)

    def visit_FunctionDef(self, node):
        self._function_helper(node, "def")

    def visit_AsyncFunctionDef(self, node):
        self._function_helper(node, "async def")

    def _function_helper(self, node, fill_suffix):
        self.maybe_newline()
        for deco in node.decorator_list:
            self.fill("@")
            self.traverse(deco)
        def_str = fill_suffix + " " + node.name
        self.fill(def_str)
        self._type_params_helper(node.type_params)
        with self.delimit("(", ")"):
            self.traverse(node.args)
        if node.returns:
            self.write(" -> ")
            self.traverse(node.returns)
        with self.block(extra=self.get_type_comment(node)):
            self._write_docstring_and_traverse_body(node)

    def _type_params_helper(self, type_params):
        if type_params is not None and len(type_params) > 0:
            with self.delimit("[", "]"):
                self.interleave(lambda: self.write(", "), self.traverse, type_params)

    def visit_TypeVar(self, node):
        self.write(node.name)
        if node.bound:
            self.write(": ")
            self.traverse(node.bound)

    def visit_TypeVarTuple(self, node):
        self.write("*" + node.name)

    def visit_ParamSpec(self, node):
        self.write("**" + node.name)

    def visit_TypeAlias(self, node):
        self.fill("type ")
        self.traverse(node.name)
        self._type_params_helper(node.type_params)
        self.write(" = ")
        self.traverse(node.value)

    def visit_For(self, node):
        self._for_helper("for ", node)

    def visit_AsyncFor(self, node):
        self._for_helper("async for ", node)

    def _for_helper(self, fill, node):
        self.fill(fill)
        self.set_precedence(_Precedence.TUPLE, node.target)
        self.traverse(node.target)
        self.write(" in ")
        self.traverse(node.iter)
        with self.block(extra=self.get_type_comment(node)):
            self.traverse(node.body)
        if node.orelse:
            self.fill("else")
            with self.block():
                self.traverse(node.orelse)

    def visit_If(self, node):
        self.fill("if ")
        self.traverse(node.test)
        with self.block():
            self.traverse(node.body)
        while node.orelse and len(node.orelse) == 1 and isinstance(node.orelse[0], If):
            node = node.orelse[0]
            self.fill("elif ")
            self.traverse(node.test)
            with self.block():
                self.traverse(node.body)
        if node.orelse:
            self.fill("else")
            with self.block():
                self.traverse(node.orelse)

    def visit_While(self, node):
        self.fill("while ")
        self.traverse(node.test)
        with self.block():
            self.traverse(node.body)
        if node.orelse:
            self.fill("else")
            with self.block():
                self.traverse(node.orelse)

    def visit_With(self, node):
        self.fill("with ")
        self.interleave(lambda: self.write(", "), self.traverse, node.items)
        with self.block(extra=self.get_type_comment(node)):
            self.traverse(node.body)

    def visit_AsyncWith(self, node):
        self.fill("async with ")
        self.interleave(lambda: self.write(", "), self.traverse, node.items)
        with self.block(extra=self.get_type_comment(node)):
            self.traverse(node.body)

    def _write_docstring(self, node):
        self.fill()
        if node.kind == "u":
            self.write("u")
        self._write_str_avoiding_backslashes(node.value, quote_types=_MULTI_QUOTES)

    def _write_constant(self, value):
        if isinstance(value, (float, complex)):
            # Substitute overflowing decimal literal for AST infinities,
            # and inf - inf for NaNs.
            self.write(
                repr(value)
                .replace("inf", _INFSTR)
                .replace("nan", f"({_INFSTR}-{_INFSTR})")
            )
        elif self._avoid_backslashes and isinstance(value, str):
            self._write_str_avoiding_backslashes(value)
        else:
            self.write(repr(value))

    def visit_Constant(self, node):
        value = node.value
        if isinstance(value, tuple):
            with self.delimit("(", ")"):
                self.items_view(self._write_constant, value)
        elif value is ...:
            self.write("...")
        else:
            if node.kind == "u":
                self.write("u")
            self._write_constant(node.value)

    def visit_List(self, node):
        with self.delimit("[", "]"):
            self.interleave(lambda: self.write(", "), self.traverse, node.elts)

    def visit_ListComp(self, node):
        with self.delimit("[", "]"):
            self.traverse(node.elt)
            for gen in node.generators:
                self.traverse(gen)

    def visit_GeneratorExp(self, node):
        with self.delimit("(", ")"):
            self.traverse(node.elt)
            for gen in node.generators:
                self.traverse(gen)

    def visit_SetComp(self, node):
        with self.delimit("{", "}"):
            self.traverse(node.elt)
            for gen in node.generators:
                self.traverse(gen)

    def visit_DictComp(self, node):
        with self.delimit("{", "}"):
            self.traverse(node.key)
            self.write(": ")
            self.traverse(node.value)
            for gen in node.generators:
                self.traverse(gen)

    def visit_comprehension(self, node):
        if node.is_async:
            self.write(" async for ")
        else:
            self.write(" for ")
        self.set_precedence(_Precedence.TUPLE, node.target)
        self.traverse(node.target)
        self.write(" in ")
        self.set_precedence(_Precedence.TEST.next(), node.iter, *node.ifs)
        self.traverse(node.iter)
        for if_clause in node.ifs:
            self.write(" if ")
            self.traverse(if_clause)

    def visit_IfExp(self, node):
        with self.require_parens(_Precedence.TEST, node):
            self.set_precedence(_Precedence.TEST.next(), node.body, node.test)
            self.traverse(node.body)
            self.write(" if ")
            self.traverse(node.test)
            self.write(" else ")
            self.set_precedence(_Precedence.TEST, node.orelse)
            self.traverse(node.orelse)

    def visit_Set(self, node):
        if node.elts:
            with self.delimit("{", "}"):
                self.interleave(lambda: self.write(", "), self.traverse, node.elts)
        else:
            # `{}` would be interpreted as a dictionary literal, and
            # `set` might be shadowed. Thus:
            self.write("{*()}")

    def visit_Dict(self, node):
        def write_key_value_pair(k, v):
            self.traverse(k)
            self.write(": ")
            self.traverse(v)

        def write_item(item):
            k, v = item
            if k is None:
                # for dictionary unpacking operator in dicts {**{'y': 2}}
                # see PEP 448 for details
                self.write("**")
                self.set_precedence(_Precedence.EXPR, v)
                self.traverse(v)
            else:
                write_key_value_pair(k, v)

        with self.delimit("{", "}"):
            self.interleave(
                lambda: self.write(", "), write_item, zip(node.keys, node.values)
            )

    def visit_Tuple(self, node):
        with self.delimit_if(
            "(",
            ")",
            len(node.elts) == 0 or self.get_precedence(node) > _Precedence.TUPLE,
        ):
            self.items_view(self.traverse, node.elts)

    unop = {"Invert": "~", "Not": "not", "UAdd": "+", "USub": "-"}
    unop_precedence = {
        "not": _Precedence.NOT,
        "~": _Precedence.FACTOR,
        "+": _Precedence.FACTOR,
        "-": _Precedence.FACTOR,
    }

    def visit_UnaryOp(self, node):
        operator = self.unop[node.op.__class__.__name__]
        operator_precedence = self.unop_precedence[operator]
        with self.require_parens(operator_precedence, node):
            self.write(operator)
            # factor prefixes (+, -, ~) shouldn't be separated
            # from the value they belong, (e.g: +1 instead of + 1)
            if operator_precedence is not _Precedence.FACTOR:
                self.write(" ")
            self.set_precedence(operator_precedence, node.operand)
            self.traverse(node.operand)

    binop = {
        "Add": "+",
        "Sub": "-",
        "Mult": "*",
        "MatMult": "@",
        "Div": "/",
        "Mod": "%",
        "LShift": "<<",
        "RShift": ">>",
        "BitOr": "|",
        "BitXor": "^",
        "BitAnd": "&",
        "FloorDiv": "//",
        "Pow": "**",
    }

    binop_precedence = {
        "+": _Precedence.ARITH,
        "-": _Precedence.ARITH,
        "*": _Precedence.TERM,
        "@": _Precedence.TERM,
        "/": _Precedence.TERM,
        "%": _Precedence.TERM,
        "<<": _Precedence.SHIFT,
        ">>": _Precedence.SHIFT,
        "|": _Precedence.BOR,
        "^": _Precedence.BXOR,
        "&": _Precedence.BAND,
        "//": _Precedence.TERM,
        "**": _Precedence.POWER,
    }

    binop_rassoc = frozenset(("**",))

    def visit_BinOp(self, node):
        operator = self.binop[node.op.__class__.__name__]
        operator_precedence = self.binop_precedence[operator]
        with self.require_parens(operator_precedence, node):
            if operator in self.binop_rassoc:
                left_precedence = operator_precedence.next()
                right_precedence = operator_precedence
            else:
                left_precedence = operator_precedence
                right_precedence = operator_precedence.next()

            self.set_precedence(left_precedence, node.left)
            self.traverse(node.left)
            self.write(f" {operator} ")
            self.set_precedence(right_precedence, node.right)
            self.traverse(node.right)

    cmpops = {
        "Eq": "==",
        "NotEq": "!=",
        "Lt": "<",
        "LtE": "<=",
        "Gt": ">",
        "GtE": ">=",
        "Is": "is",
        "IsNot": "is not",
        "In": "in",
        "NotIn": "not in",
    }

    def visit_Compare(self, node):
        with self.require_parens(_Precedence.CMP, node):
            self.set_precedence(_Precedence.CMP.next(), node.left, *node.comparators)
            self.traverse(node.left)
            for o, e in zip(node.ops, node.comparators):
                self.write(" " + self.cmpops[o.__class__.__name__] + " ")
                self.traverse(e)

    boolops = {"And": "and", "Or": "or"}
    boolop_precedence = {"and": _Precedence.AND, "or": _Precedence.OR}

    def visit_BoolOp(self, node):
        operator = self.boolops[node.op.__class__.__name__]
        operator_precedence = self.boolop_precedence[operator]

        def increasing_level_traverse(node):
            nonlocal operator_precedence
            operator_precedence = operator_precedence.next()
            self.set_precedence(operator_precedence, node)
            self.traverse(node)

        with self.require_parens(operator_precedence, node):
            s = f" {operator} "
            self.interleave(lambda: self.write(s), increasing_level_traverse, node.values)

    def visit_Attribute(self, node):
        self.set_precedence(_Precedence.ATOM, node.value)
        self.traverse(node.value)
        # Special case: 3.__abs__() is a syntax error, so if node.value
        # is an integer literal then we need to either parenthesize
        # it or add an extra space to get 3 .__abs__().
        if isinstance(node.value, Constant) and isinstance(node.value.value, int):
            self.write(" ")
        self.write(".")
        self.write(node.attr)

    def visit_Call(self, node):
        self.set_precedence(_Precedence.ATOM, node.func)
        self.traverse(node.func)
        with self.delimit("(", ")"):
            comma = False
            for e in node.args:
                if comma:
                    self.write(", ")
                else:
                    comma = True
                self.traverse(e)
            for e in node.keywords:
                if comma:
                    self.write(", ")
                else:
                    comma = True
                self.traverse(e)

    def visit_Subscript(self, node):
        def is_non_empty_tuple(slice_value):
            return isinstance(slice_value, Tuple) and slice_value.elts

        self.set_precedence(_Precedence.ATOM, node.value)
        self.traverse(node.value)
        with self.delimit("[", "]"):
            if is_non_empty_tuple(node.slice):
                # parentheses can be omitted if the tuple isn't empty
                self.items_view(self.traverse, node.slice.elts)
            else:
                self.traverse(node.slice)

    def visit_Starred(self, node):
        self.write("*")
        self.set_precedence(_Precedence.EXPR, node.value)
        self.traverse(node.value)

    def visit_Ellipsis(self, node):
        self.write("...")

    def visit_Slice(self, node):
        if node.lower:
            self.traverse(node.lower)
        self.write(":")
        if node.upper:
            self.traverse(node.upper)
        if node.step:
            self.write(":")
            self.traverse(node.step)

    def visit_Name(self, node):
        self.write(node.id)

    def visit_arg(self, node):
        self.write(node.arg)
        if node.annotation:
            self.write(": ")
            self.traverse(node.annotation)

    def visit_arguments(self, node):
        first = True
        # normal arguments
        all_args = node.posonlyargs + node.args
        defaults = [None] * (len(all_args) - len(node.defaults)) + node.defaults
        for index, elements in enumerate(zip(all_args, defaults), 1):
            a, d = elements
            if first:
                first = False
            else:
                self.write(", ")
            self.traverse(a)
            if d:
                self.write("=")
                self.traverse(d)
            if index == len(node.posonlyargs):
                self.write(", /")

        # varargs, or bare '*' if no varargs but keyword-only arguments present
        if node.vararg or node.kwonlyargs:
            if first:
                first = False
            else:
                self.write(", ")
            self.write("*")
            if node.vararg:
                self.write(node.vararg.arg)
                if node.vararg.annotation:
                    self.write(": ")
                    self.traverse(node.vararg.annotation)

        # keyword-only arguments
        if node.kwonlyargs:
            for a, d in zip(node.kwonlyargs, node.kw_defaults):
                self.write(", ")
                self.traverse(a)
                if d:
                    self.write("=")
                    self.traverse(d)

        # kwargs
        if node.kwarg:
            if first:
                first = False
            else:
                self.write(", ")
            self.write("**" + node.kwarg.arg)
            if node.kwarg.annotation:
                self.write(": ")
                self.traverse(node.kwarg.annotation)

    def visit_keyword(self, node):
        if node.arg is None:
            self.write("**")
        else:
            self.write(node.arg)
            self.write("=")
        self.traverse(node.value)

    def visit_Lambda(self, node):
        with self.require_parens(_Precedence.TEST, node):
            self.write("lambda")
            with self.buffered() as buffer:
                self.traverse(node.args)
            if buffer:
                self.write(" ", *buffer)
            self.write(": ")
            self.set_precedence(_Precedence.TEST, node.body)
            self.traverse(node.body)

    def visit_alias(self, node):
        self.write(node.name)
        if node.asname:
            self.write(" as " + node.asname)

    def visit_withitem(self, node):
        self.traverse(node.context_expr)
        if node.optional_vars:
            self.write(" as ")
            self.traverse(node.optional_vars)

    # ---- f-string / string-literal helpers -------------------------------

    def _str_literal_helper(
        self, string, *, quote_types=_ALL_QUOTES, escape_special_whitespace=False
    ):
        """Helper for writing string literals, minimizing escapes.

        Returns the tuple (string literal to write, possible quote types).
        """

        def escape_char(c):
            # \n and \t are non-printable, but we only escape them if
            # escape_special_whitespace is True
            if not escape_special_whitespace and c in "\n\t":
                return c
            # Always escape backslashes and other non-printable characters
            if c == "\\" or not c.isprintable():
                return c.encode("unicode_escape").decode("ascii")
            return c

        escaped_string = "".join(map(escape_char, string))
        possible_quotes = quote_types
        if "\n" in escaped_string:
            possible_quotes = [q for q in possible_quotes if q in _MULTI_QUOTES]
        possible_quotes = [q for q in possible_quotes if q not in escaped_string]
        if not possible_quotes:
            # If there aren't any possible_quotes, fallback to using repr
            # on the original string. Try to use a quote we can use later.
            string = repr(string)
            quote = next((q for q in quote_types if string[0] in q), string[0])
            return string[1:-1], [quote]
        if escaped_string:
            # Sort so that we prefer '''"''' over """\""""
            possible_quotes.sort(key=lambda q: q[0] == escaped_string[-1])
            # If we're using triple quotes and we'd need to escape a final
            # quote, escape it
            if possible_quotes[0][0] == escaped_string[-1]:
                assert len(possible_quotes[0]) == 3
                escaped_string = escaped_string[:-1] + "\\" + escaped_string[-1]
        return escaped_string, possible_quotes

    def _write_str_avoiding_backslashes(self, string, *, quote_types=_ALL_QUOTES):
        """Write string literal value with a best effort attempt to avoid backslashes."""
        string, quote_types = self._str_literal_helper(string, quote_types=quote_types)
        quote_type = quote_types[0]
        self.write(f"{quote_type}{string}{quote_type}")

    def visit_JoinedStr(self, node):
        self.write("f")
        if self._avoid_backslashes:
            with self.buffered() as buffer:
                self._write_fstring_inner(node)
            return self._write_str_avoiding_backslashes("".join(buffer))

        # If we don't need to avoid backslashes globally (i.e., we only need
        # to avoid them inside FormattedValues), it's cosmetically preferred
        # to use escaped whitespace. That is, it's preferred to use backslashes
        # for cases like: f"{x}\n". To accomplish this, we keep track of what
        # in our buffer corresponds to FormattedValues and what corresponds to
        # Constant parts of the f-string, and allow escapes accordingly.
        buffer = []
        for value in node.values:
            meth = getattr(self, "_fstring_" + type(value).__name__)
            with self.buffered() as buf:
                meth(value)
            buffer.append(("".join(buf), isinstance(value, Constant)))
        new_buffer = []
        quote_types = _ALL_QUOTES
        for value, is_constant in buffer:
            # Repeatedly narrow down the list of possible quote_types
            value, quote_types = self._str_literal_helper(
                value,
                quote_types=quote_types,
                escape_special_whitespace=is_constant,
            )
            new_buffer.append(value)
        value = "".join(new_buffer)
        quote_type = quote_types[0]
        self.write(f"{quote_type}{value}{quote_type}")

    def _write_fstring_inner(self, node):
        if isinstance(node, JoinedStr):
            # for both the f-string itself, and format_spec
            for value in node.values:
                self._write_fstring_inner(value)
        elif isinstance(node, Constant) and isinstance(node.value, str):
            value = node.value.replace("{", "{{").replace("}", "}}")
            self.write(value)
        elif isinstance(node, FormattedValue):
            self.visit_FormattedValue(node)
        else:
            raise ValueError(f"Unexpected node inside JoinedStr, {node!r}")

    def _fstring_JoinedStr(self, node):
        self._write_fstring_inner(node)

    def _fstring_Constant(self, node):
        self._write_fstring_inner(node)

    def _fstring_FormattedValue(self, node):
        self.visit_FormattedValue(node)

    def visit_FormattedValue(self, node):
        def unparse_inner(inner):
            unparser = type(self)(_avoid_backslashes=True)
            unparser.set_precedence(_Precedence.TEST.next(), inner)
            return unparser.visit(inner)

        with self.delimit("{", "}"):
            expr = unparse_inner(node.value)
            if expr.startswith("{"):
                # Separate pair of opening brackets as "{ {"
                self.write(" ")
            self.write(expr)
            if node.conversion != -1:
                self.write(f"!{chr(node.conversion)}")
            if node.format_spec:
                self.write(":")
                self._write_fstring_inner(node.format_spec)

    # ---- match statement -------------------------------------------------

    def visit_Match(self, node):
        self.fill("match ")
        self.traverse(node.subject)
        with self.block():
            for case in node.cases:
                self.traverse(case)

    def visit_match_case(self, node):
        self.fill("case ")
        self.traverse(node.pattern)
        if node.guard:
            self.write(" if ")
            self.traverse(node.guard)
        with self.block():
            self.traverse(node.body)

    def visit_MatchValue(self, node):
        self.traverse(node.value)

    def visit_MatchSingleton(self, node):
        self._write_constant(node.value)

    def visit_MatchSequence(self, node):
        with self.delimit("[", "]"):
            self.interleave(
                lambda: self.write(", "), self.traverse, node.patterns
            )

    def visit_MatchStar(self, node):
        name = node.name
        if name is None:
            name = "_"
        self.write(f"*{name}")

    def visit_MatchMapping(self, node):
        def write_key_pattern_pair(pair):
            k, p = pair
            self.traverse(k)
            self.write(": ")
            self.traverse(p)

        with self.delimit("{", "}"):
            keys = node.keys
            self.interleave(
                lambda: self.write(", "),
                write_key_pattern_pair,
                zip(keys, node.patterns, strict=True),
            )
            rest = node.rest
            if rest is not None:
                if keys:
                    self.write(", ")
                self.write(f"**{rest}")

    def visit_MatchClass(self, node):
        self.set_precedence(_Precedence.ATOM, node.cls)
        self.traverse(node.cls)
        with self.delimit("(", ")"):
            patterns = node.patterns
            self.interleave(
                lambda: self.write(", "), self.traverse, patterns
            )
            attrs = node.kwd_attrs
            if attrs:
                def write_attr_pattern(pair):
                    attr, pattern = pair
                    self.write(f"{attr}=")
                    self.traverse(pattern)

                if patterns:
                    self.write(", ")
                self.interleave(
                    lambda: self.write(", "),
                    write_attr_pattern,
                    zip(attrs, node.kwd_patterns, strict=True),
                )

    def visit_MatchAs(self, node):
        name = node.name
        pattern = node.pattern
        if name is None:
            self.write("_")
        elif pattern is None:
            self.write(node.name)
        else:
            with self.require_parens(_Precedence.TEST, node):
                self.set_precedence(_Precedence.BOR, node.pattern)
                self.traverse(node.pattern)
                self.write(f" as {node.name}")

    def visit_MatchOr(self, node):
        with self.require_parens(_Precedence.BOR, node):
            self.set_precedence(_Precedence.BOR.next(), *node.patterns)
            self.interleave(lambda: self.write(" | "), self.traverse, node.patterns)


def unparse(ast_obj):
    unparser = _Unparser()
    return unparser.visit(ast_obj)


def _self_test(limit=None):
    """Differential acceptance test against the stdlib ``ast`` (dev aid).

    Parses every .py file in the standard library with both this module and
    the built-in ``ast`` and compares ``dump`` output (structure).  Requires
    the stdlib ``ast`` to be importable purely as an oracle; the parser itself
    never uses it.  Prints a tally and returns it.
    """
    import ast as _real
    import os as _os
    import sysconfig as _sysconfig

    stdlib = _sysconfig.get_paths()["stdlib"]
    files = []
    for root, _dirs, fs in _os.walk(stdlib):
        if "test" in root.split(_os.sep):
            continue
        for f in fs:
            if f.endswith(".py"):
                files.append(_os.path.join(root, f))
    files.sort()
    if limit:
        files = files[:limit]
    struct = unsupported = diff = crash = skipped = 0
    failures = []
    for path in files:
        try:
            src = open(path, encoding="utf-8").read()
        except Exception:
            continue
        try:
            oracle = _real.parse(src)
        except SyntaxError:
            skipped += 1
            continue
        try:
            ours = parse(src)
        except PyCSLSyntaxError:
            unsupported += 1
            continue
        except Exception as exc:  # pragma: no cover
            crash += 1
            failures.append((path, "CRASH", repr(exc)[:80]))
            continue
        if _real.dump(oracle) == dump(ours):
            struct += 1
        else:
            diff += 1
            failures.append((path, "DIFF", ""))
    total = len(files)
    print(f"pure_ast self-test over {total} stdlib files "
          f"({skipped} skipped as real SyntaxError):")
    print(f"  structure-equal : {struct}")
    print(f"  unsupported     : {unsupported}  (deferred constructs, raised cleanly)")
    print(f"  DIFF            : {diff}")
    print(f"  CRASH           : {crash}")
    for path, kind, extra in failures[:20]:
        print(f"    {kind}  {_os.path.basename(path)}  {extra}")
    return {"structure": struct, "unsupported": unsupported,
            "diff": diff, "crash": crash, "total": total}


def main(args=None):
    argv = list(_sys.argv[1:] if args is None else args)
    if argv and argv[0] == "--self-test":
        limit = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else None
        _self_test(limit)
        return

    import argparse

    parser = argparse.ArgumentParser(prog="python -m ast")
    parser.add_argument(
        "infile",
        nargs="?",
        default="-",
        help="the file to parse; defaults to stdin",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="exec",
        choices=("exec", "single", "eval", "func_type"),
        help="specify what kind of code must be parsed",
    )
    parser.add_argument(
        "--no-type-comments",
        default=True,
        action="store_false",
        help="don't add information about type comments",
    )
    parser.add_argument(
        "-a",
        "--include-attributes",
        action="store_true",
        help="include attributes such as line numbers and column offsets",
    )
    parser.add_argument(
        "-i",
        "--indent",
        type=int,
        default=3,
        help="indentation of nodes (number of spaces)",
    )
    args = parser.parse_args(args)

    if args.infile == "-":
        name = "<stdin>"
        source = _sys.stdin.buffer.read()
    else:
        name = args.infile
        with open(args.infile, "rb") as infile:
            source = infile.read()
    tree = parse(source, name, args.mode)
    print(dump(tree, include_attributes=args.include_attributes, indent=args.indent))


if __name__ == "__main__":
    main()
